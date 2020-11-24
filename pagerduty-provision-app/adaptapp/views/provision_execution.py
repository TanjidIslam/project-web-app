from datetime import date
from json import dump, load
from os import getcwd, path
from time import sleep

from flask import render_template, session, redirect, url_for, request

from adaptapp import app
from adaptapp.config.integrations import INTEGRATION_PATH
from adaptapp.modules.business_services import biz_svc_get_payload, impact_get_payload, provision_biz_associations, \
    provision_impact_metrics
from adaptapp.modules.escalation_policy import ep_iter_all
from adaptapp.modules.event_rule import get_event_rules
from adaptapp.modules.event_rule import provision_event_rules, cond_to_str
from adaptapp.modules.file_modifier import create_folder
from adaptapp.modules.service import service_get_payload, provision_service


@app.route('/provision/preview', methods=['GET'])
def get_provision_data():
    global_key = session['global_token']
    all_ep = ep_iter_all(global_key)

    # service_abstraction = session["service_abstraction"]
    default_ep = session["escalation_policy"]
    # tag_combo = session["tag_combo"]

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_tag_combo = path.join(save_path, "resources/%s/tag_combo.json" % subdomain)

    try:
        with open(complete_name_tag_combo) as json_file:
            tag_combo = load(json_file)
    except IOError:
        tag_combo = {}
        with open(complete_name_tag_combo, 'w+') as outfile:
            dump(tag_combo, outfile)

    complete_name_abstraction = path.join(save_path, "resources/%s/service_abstraction.json" % subdomain)

    with open(complete_name_abstraction) as json_file:
        service_abstraction = load(json_file)

    complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)

    with open(complete_name_template) as json_file:
        template = load(json_file)

    # integration_path = INTEGRATION_PATH[template["integrations"]]

    tags = tag_combo[service_abstraction['string']]
    # tags_2 = tag_combo[service_abstraction['string']]
    # integrations = session["integrations"]
    conditions = get_event_rules(tags, service_abstraction, template["event_rules_path"])
    services = service_get_payload(tags, template["escalation_policy"], template["alert_creation"], \
                                   template["alert_grouping"], template["timed_grouping"])
    business_services = biz_svc_get_payload(tags, customer_name=session["customer_name"], poi=template["poi"])
    impact_metrics = impact_get_payload(tags)

    changes = {}
    print("TAGS !@!#@!#:", tags[0])
    for i in range(len(tags[0])):
        changes[tags[0][i]] = {
            "service": services[i],
            "event_rules": conditions[i],
            "impact_metrics": impact_metrics[i],
            "business_service": business_services[i]
        }

    complete_name_changes = path.join(save_path, "resources/%s/changes.json" % subdomain)

    with open(complete_name_changes, 'w+') as outfile:
        dump(changes, outfile)

    all_services = list(changes.keys())
    print("ALL SERVICES:", all_services)

    session['provision_previewed'] = True

    return render_template("provision_preview.html", changes=changes, all_services=all_services,
                           subdomain=session['subdomain'], template=template,
                           provisioned=session['provisioned'], tags_exist=session['tags_exist'],
                           incidents_exist=session['incidents_exist'], all_ep=all_ep)


@app.route('/provision/preview', methods=['POST'])
def post_provision_data():
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)

    with open(complete_name_template) as json_file:
        template = load(json_file)

    if request.form.get("escalation_policy"):
        template['escalation_policy'] = request.form.get("escalation_policy")

    if request.form.get("business_service"):
        # print("PRINTING BIZ SERVICE REQ:", request.form['business_service'])
        if request.form['business_service'] == "true":
            template['business_services'] = True
        else:
            template['business_services'] = False

    if request.form.get("impact_metrics"):
        if request.form['impact_metrics'] == "true":
            template['impact_metrics'] = True
        else:
            template['impact_metrics'] = False

    if request.form.get("eventRules"):
        template['event_rules_path_str'] = request.form.get("eventRules")
        template['event_rules_path'] = ['path'] + template['event_rules_path_str'].split(".")

    if request.form.get("alert_creation"):
        template['alert_creation'] = request.form.get("alert_creation")
        if template['alert_creation'] == 'create_alerts_and_incidents':
            if request.form.get("alert_grouping"):
                template['alert_grouping'] = request.form.get("alert_grouping")
                if template['alert_grouping'] == 'time' and request.form.get("timed_grouping"):
                    template['timed_grouping'] = request.form.get("timed_grouping")

    with open(complete_name_template, 'w+') as outfile:
        dump(template, outfile)

    return redirect(url_for('get_provision_data'))


@app.route('/provision/results', methods=['GET'])
def extract_logs():
    api_logs = {}
    global_token = session['global_token']
    user_token = session['user_token']
    customer_name = session['customer_name']

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/changes.json" % subdomain)
    today = date.today()
    complete_name_success = path.join(save_path, "resources/%s/logs/log_%s.log" % (subdomain, today))

    try:
        with open(complete_name) as json_file:
            reviewed_data = load(json_file)
    except IOError:
        reviewed_data = {}
        with open(complete_name, 'w+') as outfile:
            dump(reviewed_data, outfile)

    complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)

    with open(complete_name_template) as json_file:
        template = load(json_file)

    for data in reviewed_data:
        sleep(2)
        service_name = reviewed_data[data]['service']['name']
        ep_name = reviewed_data[data]['service']['ep_id']
        alert_creation = reviewed_data[data]['service']['alert_creation']
        alert_grouping = reviewed_data[data]['service']['alert_grouping']

        # Create New Service here and log changes
        new_service = provision_service(service_name, ep_name, alert_creation, alert_grouping)
        new_service.create(global_token, complete_name_success)
        service_href = '<a href="%s" target="_blank">%s</a>' % (new_service.html_url, service_name)
        current_service_id = new_service.id
        api_logs[service_name] = {
            "service": {
                "name": new_service.name,
                "id": new_service.id,
                "url": new_service.html_url,
                "href": service_href,
                "payload": new_service.payload
            }
        }

        print("PRINTING CONDITION:", reviewed_data[data]['event_rules']['condition'])

        condition = reviewed_data[data]['event_rules']['condition']

        # Create new event rules and log it here
        new_event_rule = provision_event_rules(new_service, condition, current_service_id)
        new_event_rule.create(global_token, complete_name_success)
        api_logs[service_name]["event_rules"] = {
            "service_id": new_service.id,
            "condition": condition,
            "payload": new_event_rule.payload,
            "str_rep": cond_to_str(new_event_rule.condition, service_href),
            "id": new_event_rule.payload["id"]
        }

        is_name = reviewed_data[data]["impact_metrics"]["name"]

        if template["business_services"]:
            biz_name = reviewed_data[data]["business_service"]["name"]
            biz_poc = reviewed_data[data]["business_service"]["point_of_contact"]
            biz_rel = reviewed_data[data]["business_service"]["relationship"]

            # Create new business service and log it here
            new_biz_service = provision_biz_associations(biz_name, biz_poc, biz_rel, customer_name)
            new_biz_service.create(global_token, complete_name_success)
            api_logs[service_name]["business_service"] = {
                "name": new_biz_service.name,
                "supporting_services": None,
                "dependent_services": None,
                "id": new_biz_service.id,
                "test": new_biz_service.payload
            }
            service_reference = {"id": new_service.id, "type": "service_reference"}
            if biz_rel == "supporting_services":
                new_biz_service.assign_supporting_services(global_token, new_service.id, complete_name_success)
                api_logs[service_name]["business_service"]["support_services"] = new_biz_service.supporting_services
            elif biz_rel == "dependent_services":
                new_biz_service.assign_dependent_services(global_token, new_service.id, complete_name_success)
                api_logs[service_name]["business_service"]["dependent_services"] = new_biz_service.dependent_services

        # Create new impact metrics and log it here
        if template["impact_metrics"]:
            new_impact_metrics = provision_impact_metrics(is_name, customer_name)
            new_impact_metrics.create(user_token, complete_name_success)
            api_logs[service_name]["impact_metrics"] = {
                "name": new_impact_metrics.provisioned_name,
                "payload": new_impact_metrics.payload,
                "id": new_impact_metrics.id
            }
            impact_id = new_impact_metrics.id
            if template["business_services"]:
                # Associate impact metrics and supporting services
                new_biz_service.assign_impact_metrics(user_token, impact_id, complete_name_success)
        else:
            print("SKIPPING IMPACT METRICS")

    print("====\n", api_logs)
    all_services = list(api_logs.keys())

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/api_logs.json" % subdomain)

    with open(complete_name, 'w+') as outfile:
        dump(api_logs, outfile)

    complete_name_logs = path.join(save_path, "resources/%s/service.json" % subdomain)
    with open(complete_name_logs, 'w+') as outfile:
        dump(list(api_logs.keys()), outfile)
    session['global_token'] = global_token
    session['user_token'] = user_token

    print("====\n", api_logs)
    all_services = list(api_logs.keys())

    with open(complete_name_logs) as log_file:
        log_services = load(log_file)

    # log_services = session["log_services"]
    session['provisioned'] = True

    return render_template("provision_result.html", api_logs=api_logs, log_services=log_services,
                           subdomain=session['subdomain'], template=template,
                           all_services=all_services, provisioned=session['provisioned'],
                           tags_exist=session['tags_exist'], incidents_exist=session['incidents_exist'])
