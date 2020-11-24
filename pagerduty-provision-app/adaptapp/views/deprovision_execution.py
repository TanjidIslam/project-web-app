from datetime import date
from json import dump, load
from os import getcwd, path

from flask import session, redirect, url_for, flash

from adaptapp import app
from adaptapp.modules.deprovision import deprovision
from adaptapp.modules.file_modifier import create_folder


@app.route('/deprovision', methods=['GET'])
def deprovision_data():
    global_api = session['global_token']
    user_api = session['user_token']
    today = date.today()

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/api_logs.json" % subdomain)
    log_file = path.join(save_path, "resources/%s/logs/log_%s.log" % (subdomain, today))
    complete_name_logs = path.join(save_path, "resources/%s/service.json" % subdomain)

    complete_name_template = path.join(save_path, "resources/%s/template.json" % subdomain)

    with open(complete_name_template) as json_file:
        template = load(json_file)

    with open(complete_name) as json_file:
        api_logs = load(json_file)

    deprovision(global_api, user_api, api_logs, log_file, template)

    api_logs = {}
    with open(complete_name, 'w+') as outfile:
        dump(api_logs, outfile)

    log_services = []
    with open(complete_name, 'w+') as outfile:
        dump(log_services, outfile)

    session['provisioned'] = False

    if "provision_failed" in session and session["provision_failed"] == True:
        flash("Something went wrong with the provisioning!")
        session["provision_failed"] = False
        return redirect(url_for('get_provision_data'))
    if session['disco_choice'] != '2':
        return redirect(url_for('get_service_discovery'))
    return redirect(url_for('tag_list_multiple'))
