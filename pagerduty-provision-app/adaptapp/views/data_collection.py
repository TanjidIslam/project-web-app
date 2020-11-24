from datetime import datetime, date
from json import dump, load
from os import path, getcwd

from flask import flash
from flask import request, render_template, session, redirect, url_for
from pdpyras import APISession

from adaptapp import app
from adaptapp.modules.escalation_policy import ep_iter_all
from adaptapp.modules.file_modifier import create_folder
from adaptapp.modules.validator import is_token_valid, is_dd_token_valid


@app.route('/', methods=['GET'])
def get_discovery_method():
    session.clear()
    return render_template('select_discovery_method.html')


@app.route('/', methods=['POST'])
def post_discovery_method():
    disco_choice = request.form['disco_select']
    session['disco_choice'] = disco_choice

    if disco_choice == "0":
        flash("You have to choose a method!")
        return redirect(url_for('get_discovery_method'))
    return redirect(url_for('get_api_token'))


@app.route('/authenticate', methods=['GET'])
def get_api_token():
    if 'disco_choice' not in session:
        flash('Session has been reset. Start a new session!')
        return redirect(url_for('get_discovery_method'))
    session['unique_tags'] = {}
    disco_choice = False
    if session['disco_choice'] == '2':
        disco_choice = True
    return render_template('api_token.html', disco_choice=disco_choice)


@app.route('/authenticate', methods=['POST'])
def verify_api_token():
    # Get all user inputs from POST
    global_token = request.form['global_token']
    user_token = request.form['user_token']

    if session['disco_choice'] == '2':
        dd_api_token = request.form['dd_api_token']
        dd_app_token = request.form['dd_app_token']
        if not is_dd_token_valid(dd_api_token, dd_app_token):
            last_4_dd_api = (len(dd_api_token) - 4) * "*" + dd_api_token[-4:]
            last_4_dd_app = (len(dd_app_token) - 4) * "*" + dd_app_token[-4:]
            flash("Invalid Tokens! API Token: %s or Application Token: %s" % (last_4_dd_api, last_4_dd_app))
        else:
            session['dd_api_token'] = dd_api_token
            session['dd_app_token'] = dd_app_token
    last_4_global = (len(global_token) - 4) * "*" + global_token[-4:]
    last_4_user = (len(user_token) - 4) * "*" + user_token[-4:]

    if not is_token_valid(global_token) and not is_token_valid(user_token):
        flash("Invalid Tokens! Global API Token: '%s' & User API Token: '%s'" % (last_4_global, last_4_user))
    elif not is_token_valid(global_token):
        flash("Invalid Tokens! Global Level API Token: '%s'" % last_4_global)
    elif not is_token_valid(user_token):
        flash("Invalid Tokens! User Level API Token: '%s'" % last_4_user)
    else:
        session['message'] = "Global API Token '%s' and  User API Token '%s' are valid!" % (last_4_global, last_4_user)
        session['global_token'] = global_token
        session['user_token'] = user_token
        subdomain = get_subdomain(global_token)
        subdomain_user = get_subdomain(user_token)
        if subdomain != subdomain_user:
            flash("Tokens don't belong to the same subdomain. Recheck")
            return redirect(url_for('get_api_token'))
        session['subdomain'] = subdomain

        tags_exists = False
        provisioned = False
        incidents_exist = False
        provision_previewed = False

        create_folder('resources/' + subdomain)
        create_folder('resources/' + subdomain + '/logs')

        save_path = getcwd()
        complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)
        complete_name_api_log = path.join(save_path, "resources/%s/api_logs.json" % subdomain)

        today = date.today()
        log_file = path.join(save_path, "resources/%s/logs/log_%s.log" % (subdomain, today))

        lf = open(log_file, 'a+')

        lf.write("\n[%s] [%s]: Subdomain for global API: %s" % (datetime.now(), 'Info', subdomain))
        lf.write("\n[%s] [%s]: Subdomain for user API: %s" % (datetime.now(), 'Info', subdomain_user))

        lf.close()

        complete_name_changes = path.join(save_path, "resources/%s/changes.json" % subdomain)

        try:
            with open(complete_name_changes) as json_file:
                provision_preview = load(json_file)
                if provision_preview:
                    provision_previewed = True
        except:
            provision_preview = {}
            with open(complete_name_changes, 'w+') as outfile:
                dump(provision_preview, outfile)

        try:
            with open(complete_name) as json_file:
                tags = load(json_file)
                if tags:
                    tags_exists = True
        except IOError:
            tags = {}
            with open(complete_name, 'w+') as outfile:
                dump(tags, outfile)

        try:
            with open(complete_name_api_log) as json_file:
                api_logs = load(json_file)
                if api_logs:
                    provisioned = True
        except IOError:
            api_logs = {}
            with open(complete_name_api_log, 'w+') as outfile:
                dump(api_logs, outfile)

        complete_name_events = path.join(save_path, "resources/%s/incidents.json" % subdomain)

        try:
            with open(complete_name_events) as json_file:
                incidents = load(json_file)
                if incidents:
                    incidents_exist = True
        except IOError:
            incidents = []
            with open(complete_name_events, 'w+') as outfile:
                dump(incidents, outfile)

        session['tags_exist'] = tags_exists
        session['provisioned'] = provisioned
        session['incidents_exist'] = incidents_exist
        session['provision_previewed'] = provision_previewed

        return redirect(url_for('get_metadata'))
    return redirect(url_for('get_api_token'))


@app.route('/discovery/metadata', methods=['GET'])
def get_metadata():
    global_key = session['global_token']
    all_ep = ep_iter_all(global_key)

    subdomain = session['subdomain']
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/session.json" % subdomain)

    try:
        with open(complete_name) as json_file:
            current_session = load(json_file)
    except IOError:
        print("No customers found")
        current_session = {}

    return render_template('metadata_view.html', session=current_session, all_ep=all_ep, subdomain=session['subdomain'])


@app.route('/discovery/metadata', methods=['POST'])
def post_metadata():
    default_ep = request.form["escalation_policy"]
    session["escalation_policy"] = default_ep
    session["consultant_name"] = request.form["consultant_name"]
    session["customer_name"] = request.form["customer_name"]
    session["escalation_policy"] = default_ep
    session["tech_owner"] = request.form["tech_owner"]
    session["biz_owner"] = request.form["biz_owner"]
    session["slack_number"] = request.form["slack_number"]
    session["github_id"] = request.form["github_id"]
    session["support_hours"] = request.form["support_hours"]
    session["run_book"] = request.form["run_book"]
    session["note"] = request.form["customer_note"]

    session["session_owner"] = {"consultant_name": session["consultant_name"],
                                "customer_name": session["customer_name"], "note": session["note"],
                                "tech_owner": session["tech_owner"], "biz_owner": session["biz_owner"],
                                "slack_number": session["slack_number"], "github_id": session["github_id"],
                                "support_hours": session["support_hours"], "run_book": session["run_book"]}

    subdomain = session['subdomain']
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/session.json" % subdomain)

    if session['provision_previewed']:
        complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)
        with open(complete_name_template) as json_file:
            template = load(json_file)
            template['escalation_policy'] = session["escalation_policy"]

        with open(complete_name_template, 'w+') as outfile:
            dump(template, outfile)

    with open(complete_name, 'w+') as outfile:
        dump(session["session_owner"], outfile)

    if session['disco_choice'] == '2':
        return redirect(url_for('tag_list_multiple'))
    return redirect(url_for("get_service_discovery"))


@app.route('/clearcache', methods=['GET'])
def clear_cache():
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_tag = path.join(save_path, "resources/%s/tags.json" % subdomain)
    tags = {}
    with open(complete_name_tag, 'w+') as outfile:
        dump(tags, outfile)

    complete_name_api = path.join(save_path, "resources/%s/api_logs.json" % subdomain)
    api_logs = {}
    with open(complete_name_api, 'w+') as outfile:
        dump(api_logs, outfile)

    complete_name_changes = path.join(save_path, "resources/%s/changes.json" % subdomain)
    changes = {}
    with open(complete_name_changes, 'w+') as outfile:
        dump(changes, outfile)

    complete_name_tag_combo = path.join(save_path, "resources/%s/tag_combo.json" % subdomain)
    tag_combo = {}
    with open(complete_name_tag_combo, 'w+') as outfile:
        dump(tag_combo, outfile)

    complete_name_combo = path.join(save_path, "resources/%s/combos.json" % subdomain)
    combos = []
    with open(complete_name_combo, 'w+') as outfile:
        dump(combos, outfile)

    complete_name_types = path.join(save_path, "resources/%s/types.json" % subdomain)
    types = {}
    with open(complete_name_types, 'w+') as outfile:
        dump(types, outfile)

    complete_name_sep = path.join(save_path, "resources/%s/separators.json" % subdomain)
    separators = []
    with open(complete_name_sep, 'w+') as outfile:
        dump(separators, outfile)

    complete_name_str = path.join(save_path, "resources/%s/str_abstractions.json" % subdomain)
    str_abstractions = []
    with open(complete_name_str, 'w+') as outfile:
        dump(str_abstractions, outfile)

    complete_name_abs = path.join(save_path, "resources/%s/abstractions.json" % subdomain)
    abstractions = []
    with open(complete_name_abs, 'w+') as outfile:
        dump(abstractions, outfile)

    complete_name_service = path.join(save_path, "resources/%s/service.json" % subdomain)
    log_services = []
    with open(complete_name_service, 'w+') as outfile:
        dump(log_services, outfile)

    complete_name_events = path.join(save_path, "resources/%s/incidents.json" % subdomain)
    incidents = []
    with open(complete_name_events, 'w+') as outfile:
        dump(incidents, outfile)

    complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)
    # Set to a Datadog default
    template = {"escalation_policy": "", "alert_creation": "create_alerts_and_incidents",
                "alert_grouping": "intelligent", "timed_grouping": False,
                "event_rules_path": ["path", "details", "tags"], "event_rules_path_str": "details.tags",
                "integrations": "datadog", "business_services": True, "impact_metrics": True,
                "business_services_relation": "1:1", "poi": ""}
    with open(complete_name_template, 'w+') as outfile:
        dump(template, outfile)

    complete_name_abstraction = path.join(save_path, "resources/%s/service_abstraction.json" % subdomain)
    abstractions = ""
    with open(complete_name_abstraction, 'w+') as outfile:
        dump(abstractions, outfile)

    session["tags_exist"] = False
    session['provisioned'] = False
    session['incidents_exist'] = False
    session['provision_previewed'] = False

    if session['disco_choice'] == '2':
        return redirect(url_for('tag_list_multiple'))
    else:
        return redirect(url_for('get_service_discovery'))


def get_subdomain(auth_token):
    account = APISession(auth_token)
    try:
        subdomain = account.subdomain
    except Exception as e:
        subdomain = None
    if subdomain is None:
        subdomain = 'NETWORK_ERR_OR_TOKEN_INVALID'
        print(subdomain)
    return subdomain
