from copy import deepcopy
from json import dump, load
from os import getcwd, path

from flask import request, render_template, session, redirect, url_for, flash
from json_flatten import flatten

from adaptapp import app
from adaptapp.modules.incident import incident_iter_selected
from adaptapp.modules.file_modifier import create_folder
from adaptapp.modules.service import flatten


@app.route('/discovery/incidents', methods=['GET'])
def get_incident_list():
    if 'tags_path' not in session:
        session['tags_path'] = {}

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_tags = path.join(save_path, "resources/%s/tags.json" % subdomain)

    try:
        with open(complete_name_tags) as json_file:
            tags = load(json_file)
    except IOError:
        tags = {}
        with open(complete_name_tags, 'w+') as outfile:
            dump(tags, outfile)

    complete_name_events = path.join(save_path, "resources/%s/incidents.json" % subdomain)

    try:
        with open(complete_name_events) as json_file:
            incidents = load(json_file)
        print("Found incidents. Loading the file")
    except IOError:
        incidents = []
        with open(complete_name_events, 'w+') as outfile:
            dump(incidents, outfile)
        print("Couldn't find incidents. Dumping empty list.")

    if not incidents:
        for i in range(len(session["selected_services_id"])):
            incidents = incidents + incident_iter_selected(session['global_token'], session['selected_windows'][i],
                                                           [session['selected_services_id'][i]],
                                                           session["integrations"],
                                                           tags)

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/combos.json" % subdomain)

    try:
        with open(complete_name) as json_file:
            combos = load(json_file)
    except IOError:
        combos = []
        with open(complete_name, 'w+') as outfile:
            dump(combos, outfile)

    keys = []
    flattened_keys = []
    flattened_incidents = []
    ftle = []
    ftle_keys = []

    channels = []
    channels_keys = []

    alerts = []
    alerts_keys = []

    for incident in incidents:
        incident_temp = deepcopy(incident)
        ftle_temp = incident_temp.pop("first_trigger_log_entry")
        # ftle_channel = ftle_temp.pop("channel")
        alerts_temp = incident_temp.pop("all_alerts")

        flattened_incidents.append(flatten(incident_temp))
        flattened_keys = list(set(flattened_keys + list(flatten(incident_temp).keys())))

        ftle.append(flatten(ftle_temp))
        ftle_keys = list(set(ftle_keys + list(flatten(ftle_temp).keys())))

        # channels.append(flatten(ftle_channel))
        # channels_keys = list(set(channels_keys + list(flatten(ftle_channel).keys())))

        alerts.append(flatten(alerts_temp))
        alerts_keys = list(set(alerts_keys + list(flatten(alerts_temp).keys())))

    flattened_keys.sort()
    alerts_keys.sort()
    ftle_keys.sort()

    session["flattened_keys"] = flattened_keys
    session["ftle_keys"] = ftle_keys
    session['alerts_keys'] = alerts_keys

    disco_choice = session["disco_choice"]

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    with open(complete_name, 'w+') as outfile:
        dump(tags, outfile)

    if not incidents:
        flash("No incidents found in the selected window. Please select a larger window!")
        return redirect(url_for('get_service_config'))

    complete_name_events = path.join(save_path, "resources/%s/incidents.json" % subdomain)

    with open(complete_name_events, 'w+') as outfile:
        dump(incidents, outfile)

    return render_template('incident_list.html', incidents=flattened_incidents, keys=flattened_keys,
                           alerts=alerts, alerts_keys=alerts_keys, ftle=ftle, ftle_keys=ftle_keys,
                           channels=channels, channels_keys=channels_keys, disco_choice=disco_choice,
                           tags=tags, provisioned=session['provisioned'], tags_exist=session['tags_exist'],
                           subdomain=session['subdomain'], incidents_exist=session['incidents_exist'])


@app.route('/discovery/incidents', methods=['POST'])
def post_incident_list():
    tags_path = session['tags_path']
    tag_action = request.form["tag_action"]
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_tags = path.join(save_path, "resources/%s/tags.json" % subdomain)

    try:
        with open(complete_name_tags) as json_file:
            tags = load(json_file)
    except IOError:
        tags = {}
        with open(complete_name_tags, 'w+') as outfile:
            dump(tags, outfile)

    if tag_action == "delete":
        # tags = session["tags"]
        tag_keys = list(tags.keys())
        for tag in tag_keys:
            if request.form.get("tag-%s" % tag):
                del tags[tag]
    elif tag_action == "update":
        flattened_keys = session["flattened_keys"]
        ftle_keys = session["ftle_keys"]
        alerts_keys = session['alerts_keys']

        incidents = []
        # tags = session["tags"]
        disco_choice = session["disco_choice"]
        has_tags = disco_choice != "3"
        for i in range(len(session["selected_services_id"])):
            incidents = incidents + incident_iter_selected(session['global_token'], session['selected_windows'][i],
                                                           [session['selected_services_id'][i]],
                                                           session["integrations"][i],
                                                           tags)

        tagged_keys = [[], []]

        for i in range(len(flattened_keys)):
            if request.form.get("incident_field_%s" % str(i)):
                incident_field = request.form.get("incident_field_%s" % str(i))
                tagged_keys[0].append(incident_field)
                if incident_field not in tags:
                    tags[incident_field] = []

        for i in range(len(ftle_keys)):
            if request.form.get("ftle_field_%s" % str(i)):
                ftle_field = request.form.get("ftle_field_%s" % str(i))
                tagged_keys[1].append(ftle_field)
                if ftle_field not in tags:
                    tags[ftle_field] = []

        for incident in incidents:
            incident_temp = incident
            ftle_temp = incident_temp.pop("first_trigger_log_entry")

            flattened_incident = flatten(incident_temp)
            ftle = flatten(ftle_temp)

            for key in tagged_keys[0]:
                if key in flattened_incident and flattened_incident[key] not in tags[key]:
                    tags[key].append(flattened_incident[key])

            for key in tagged_keys[1]:
                if key in ftle and ftle[key] not in tags[key]:
                    tags[key].append(ftle[key])

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    with open(complete_name, 'w+') as outfile:
        dump(tags, outfile)
    return redirect(url_for('get_incident_list'))


@app.route('/discovery/incidents/reload', methods=['GET'])
def reload_incident():
    return redirect(url_for('clear_cache'))
