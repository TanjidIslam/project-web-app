from json import dump, load
from os import getcwd, path

from flask import request, render_template, session, redirect, url_for, flash

from adaptapp import app
from adaptapp.config.integrations import INTEGRATION_PATH
from adaptapp.modules.file_modifier import create_folder
from adaptapp.modules.service import service_iter_all, service_iter_selected


@app.route('/discovery/services', methods=['GET'])
def get_service_discovery():
    global_key = session['global_token']
    subdomain = session['subdomain']

    save_path = getcwd()
    complete_name_changes = path.join(save_path, "resources/%s/changes.json" % subdomain)
    with open(complete_name_changes) as json_file:
        provision_preview = load(json_file)
        if provision_preview:
            session['provision_previewed'] = True

    complete_name_tags = path.join(save_path, "resources/%s/tags.json" % subdomain)
    with open(complete_name_tags) as json_file:
        tags = load(json_file)
        if tags:
            session['tags_exist'] = True

    if session['provision_previewed']:
        complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)
        with open(complete_name_template) as json_file:
            template = load(json_file)
            template['escalation_policy'] = session["escalation_policy"]

        with open(complete_name_template, 'w+') as outfile:
            dump(template, outfile)

    all_services = service_iter_all(global_key)
    if len(all_services) == 0:
        flash("No services found!")
        return redirect(url_for("get_discovery_method"))

    for i in range(len(all_services)):
        keys = list(all_services[i].keys())
        break
    return render_template('services_list.html', provisioned=session['provisioned'], tags_exist=session['tags_exist'],
                           services=all_services, keys=keys, session_info=session["session_owner"],
                           subdomain=session['subdomain'], incidents_exist=session['incidents_exist'], previewed=session['provision_previewed'])


@app.route('/discovery/services', methods=['POST'])
def post_service_discovery():
    all_services = service_iter_all(session['global_token'])
    selected_services = []
    for i in range(len(all_services)):
        if request.form.get('service_' + str(i + 1)):
            selected_services.append(request.form.get('service_' + str(i + 1)))

    session['selected_services_id'] = selected_services

    if not selected_services:
        flash("Warning: No service was selected. To proceed with discovery, select relevant services.")
        return redirect(url_for('get_service_discovery'))

    return redirect(url_for('get_service_config'))


@app.route('/discovery/services/configure', methods=['GET'])
def get_service_config():
    if not session['selected_services_id']:
        flash("No service was selected!")
        return redirect(url_for('get_service_discovery'))
    integrations = []

    service_payloads = service_iter_selected(session['global_token'], session['selected_services_id'])
    for service in service_payloads:
        current_integrations = []
        for integration in service["integrations"]:
            current_integrations.append(integration['summary'])
        integrations.append(", ".join(current_integrations))
    session["integrations"] = list(dict.fromkeys(integrations))

    return render_template('configure_services.html', services=service_payloads, integrations=integrations,
                           subdomain=session['subdomain'], provisioned=session['provisioned'],
                           tags_exist=session['tags_exist'], incidents_exist=session['incidents_exist'])


@app.route('/discovery/services/configure', methods=['POST'])
def post_service_config():
    default_ep = session["escalation_policy"]

    disco_windows = []
    for i in range(len(session["selected_services_id"])):
        disco_windows.append(request.form['window_duration_%s' % str(i + 1)])

    session["integrations"] = request.form['integration_choice']

    integration_path = INTEGRATION_PATH[session["integrations"]]
    print(integration_path)
    session['selected_windows'] = disco_windows

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()

    complete_name_tags = path.join(save_path, "resources/%s/tags.json" % subdomain)

    tags = {}
    with open(complete_name_tags, 'w+') as outfile:
        dump(tags, outfile)

    complete_name_events = path.join(save_path, "resources/%s/incidents.json" % subdomain)

    incidents = []
    with open(complete_name_events, 'w+') as outfile:
        dump(incidents, outfile)

    complete_name_session = path.join(save_path, "resources/%s/session.json" % subdomain)
    with open(complete_name_session) as json_file:
        session_data = load(json_file)

    template = {
        "escalation_policy": default_ep,
        "alert_creation": "create_alerts_and_incidents",
        "alert_grouping": "intelligent",
        "timed_grouping": False,
        "event_rules_path": integration_path,
        "event_rules_path_str": ".".join(integration_path[1:]),
        "integrations": session["integrations"],
        "business_services": True,
        "impact_metrics": True,
        "business_services_relation": "1:1",
        "poi": session_data['biz_owner']
    }
    complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)
    with open(complete_name_template, 'w+') as outfile:
        dump(template, outfile)

    return redirect(url_for('get_incident_list'))
