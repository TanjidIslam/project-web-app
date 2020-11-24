from copy import deepcopy
from json import dump, load
from os import getcwd, path
from re import findall, error

from flask import request, render_template, session, redirect, url_for, flash

from adaptapp import app
from adaptapp.modules.datadog_config import get_all_tags
from adaptapp.modules.file_modifier import create_folder
from adaptapp.modules.tag import tag_extract


@app.route('/discovery/fields/single', methods=['GET'])
def tag_list_single():
    get_tag_response = get_tags()
    return render_template('fields_single.html', subdomain=get_tag_response['subdomain'],
                           provisioned=session['provisioned'], tags_exist=session['tags_exist'], tags=get_tag_response['tags'],
                           disco_choice=session['disco_choice'], maxlen=get_tag_response['max_tag_len'])


@app.route('/discovery/fields/multiple', methods=['GET'])
def tag_list_multiple():
    get_tag_response = get_tags()
    return render_template('fields_multiple.html', subdomain=get_tag_response['subdomain'],
                           provisioned=session['provisioned'], tags_exist=session['tags_exist'], tags=get_tag_response['tags'],
                           disco_choice=session['disco_choice'], maxlen=get_tag_response['max_tag_len'])


@app.route('/discovery/fields/single', methods=['POST'])
def tag_discovery():
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    try:
        with open(complete_name) as json_file:
            tags = load(json_file)
    except IOError:
        tags = {}
        with open(complete_name, 'w+') as outfile:
            dump(tags, outfile)
    new_tags = deepcopy(tags)
    action = request.form["tag_action"]
    for key in tags:
        for i in range(len(tags[key])):
            if request.form.get('tag_%s_%s' % (key, str(i + 1))):
                if action == "delete":
                    new_tags[key].remove(tags[key][i])
                    if not new_tags[key]:
                        new_tags.pop(key)
                elif action == "save":
                    new_key = request.form["tag_selection"]
                    if not new_key:
                        continue
                    if new_key == "custom_adapt":
                        custom_key = request.form["custom_field"]
                        if custom_key not in new_tags:
                            new_tags[custom_key] = [tags[key][i]]
                        elif custom_key in new_tags:
                            new_tags[custom_key].append(tags[key][i])
                    elif new_key and new_key != "custom_adapt":
                        new_tags[new_key].append(tags[key][i])
                    new_tags[key].remove(tags[key][i])
                    if not new_tags[key]:
                        new_tags.pop(key)
                elif action == "extract_tags":
                    selected_field = tags[key][i]
                    fields = ""
                    if ";" in selected_field:
                        fields = selected_field.split(";")
                    elif "," in selected_field:
                        fields = selected_field.split(",")
                    if not fields:
                        flash("No key-value format found")
                        flash("key=value or key:value")
                        return redirect(url_for("tag_discovery"))

                    for field in fields:
                        if "=" not in field or ":" not in field:
                            flash("No key-value format found")
                            flash("key=value or key:value")
                        print(field)
                        temp = field.replace("=", ":")
                        if temp.split(":")[0] in new_tags and temp.split(":")[1] not in new_tags[temp.split(":")[0]]:
                            new_tags[temp.split(":")[0]].append(temp.split(":")[1])
                        else:
                            new_tags[temp.split(":")[0]] = [temp.split(":")[1]]

                    new_tags[key].remove(tags[key][i])
                    if not new_tags[key]:
                        new_tags.pop(key)
                elif action == "extract_sep":
                    selected_field = tags[key][i]
                    hostname = selected_field.replace(".", "_").replace("-", "_").replace(" ", "_")
                    if "_" in hostname:
                        fields = hostname.split("_")
                    else:
                        flash("No separators found to extract")
                        return redirect(url_for("tag_list"))
                    for x in range(len(fields)):
                        print("CURRENT KEY:", key)
                        current_key = key + "_" + str(x + 1)
                        if current_key in new_tags and fields[x] not in new_tags[current_key]:
                            new_tags[current_key].append(fields[x])
                        elif current_key not in new_tags:
                            new_tags[current_key] = [fields[x]]
                elif action == "extract_regex":
                    regex = ["(^[a-zA-Z0-9]{3})([a-zA-Z0-9]{3}\d?)([A-Za-z]{2,3})([A-Za-z]\d{1,2}|\d{2})"]
                    selected_field = tags[key][i]
                    try:
                        for r in regex:
                            regex_result = findall(r, selected_field)
                            fields = list(regex_result[0])
                            if not regex_result:
                                break
                    except error as e:
                        msg = "Regex Expression Error: {}".format(str(e))
                        flash(msg)
                        return redirect(url_for("tag_discovery"))
                    except IndexError as ie:
                        flash("Regex Expression Error: Invalid character in the expression")
                        return redirect(url_for("tag_discovery"))
                    for x in range(len(fields)):
                        current_key = key + "_" + str(x + 1)
                        if current_key in new_tags and fields[x] not in new_tags[current_key]:
                            new_tags[current_key].append(fields[x])
                        elif current_key not in new_tags:
                            new_tags[current_key] = [fields[x]]
                elif action == "extract_regex_custom":
                    regex = request.form["custom_regex"]
                    print("REGEX:", regex)
                    selected_field = tags[key][i]

                    try:
                        regex_result = findall(regex, selected_field)
                        fields = list(regex_result[0])
                        print(fields)
                    except error as e:
                        msg = "Regex Expression Error: {}".format(str(e))
                        flash(msg)
                        print("ERROR:", e)
                        return redirect(url_for("tag_discovery_all"))
                    except IndexError as ie:
                        print("ERROR:", ie)
                        flash("Regex Expression Error: Invalid character in the expression")
                        return redirect(url_for("tag_discovery_all"))
                    for x in range(len(fields)):
                        current_key = key + "_" + str(x + 1)
                        if current_key in new_tags and fields[x].upper() not in new_tags[current_key]:
                            new_tags[current_key].append(fields[x].upper())
                        elif current_key not in new_tags:
                            new_tags[current_key] = [fields[x].upper()]

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    with open(complete_name, 'w+') as outfile:
        dump(new_tags, outfile)
    return redirect(url_for("tag_list_single"))


@app.route('/discovery/fields/multiple', methods=['POST'])
def tag_discovery_all():
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    try:
        with open(complete_name) as json_file:
            tags = load(json_file)
    except IOError:
        tags = {}
        with open(complete_name, 'w+') as outfile:
            dump(tags, outfile)
    new_tags = deepcopy(tags)
    action = request.form["tag_action"]
    for key in tags:
        if request.form.get(key):
            for i in range(len(tags[key])):
                if action == "delete":
                    new_tags[key].remove(tags[key][i])
                    if not new_tags[key]:
                        new_tags.pop(key)
                elif action == "save":
                    new_key = request.form["tag_selection"]
                    if not new_key:
                        continue
                    if new_key == "custom_adapt":
                        custom_key = request.form["custom_field"]
                        if custom_key not in new_tags:
                            new_tags[custom_key] = [tags[key][i]]
                        elif custom_key in new_tags:
                            new_tags[custom_key].append(tags[key][i])
                    elif new_key and new_key != "custom_adapt":
                        new_tags[new_key].append(tags[key][i])
                    new_tags[key].remove(tags[key][i])
                    if not new_tags[key]:
                        new_tags.pop(key)
                elif action == "extract_tags":
                    selected_field = tags[key][i]
                    fields = ""
                    if ";" in selected_field:
                        fields = selected_field.split(";")
                    elif "," in selected_field:
                        fields = selected_field.split(",")
                    if not fields:
                        flash("No key-value format found")
                        flash("key=value or key:value")
                        return redirect(url_for("tag_discovery_all"))

                    for field in fields:
                        if "=" not in field or ":" not in field:
                            flash("No key-value format found")
                            flash("key=value or key:value")

                        temp = field.replace("=", ":")
                        if temp.split(":")[0] in new_tags and temp.split(":")[1] not in new_tags[temp.split(":")[0]]:
                            new_tags[temp.split(":")[0]].append(temp.split(":")[1])
                        else:
                            new_tags[temp.split(":")[0]] = [temp.split(":")[1]]

                    new_tags[key].remove(tags[key][i])
                    if not new_tags[key]:
                        new_tags.pop(key)
                elif action == "extract_sep":
                    selected_field = tags[key][i]
                    hostname = selected_field.replace(".", "_").replace("-", "_").replace(" ", "_").replace(":", "_")
                    if "_" in hostname:
                        fields = hostname.split("_")
                    else:
                        flash("No separators found to extract")
                        return redirect(url_for("tag_list_multiple"))
                    print("CURRENT FIELD:", fields)
                    for x in range(len(fields)):
                        current_key = key + "_" + str(x + 1)
                        if current_key in new_tags and fields[x] not in new_tags[current_key]:
                            new_tags[current_key].append(fields[x])
                        elif current_key not in new_tags:
                            new_tags[current_key] = [fields[x]]
                elif action == "extract_regex":
                    regex = ["(^[a-zA-Z0-9]{3})([a-zA-Z0-9]{3}\d?)([A-Za-z]{2,3})([A-Za-z]\d{1,2}|\d{2})"]
                    selected_field = tags[key][i]

                    try:
                        for r in regex:
                            regex_result = findall(r, selected_field)
                            fields = list(regex_result[0])
                            if not regex_result:
                                break
                    except error as e:
                        msg = "Regex Expression Error: {}".format(str(e))
                        flash(msg)
                        return redirect(url_for("tag_discovery_all"))
                    except IndexError as ie:
                        flash("Regex Expression Error: Invalid character in the expression")
                        return redirect(url_for("tag_discovery_all"))
                    for x in range(len(fields)):
                        current_key = key + "_" + str(x + 1)
                        if current_key in new_tags and fields[x].upper() not in new_tags[current_key]:
                            new_tags[current_key].append(fields[x].upper())
                        elif current_key not in new_tags:
                            new_tags[current_key] = [fields[x].upper()]
                elif action == "extract_regex_custom":
                    regex = request.form["custom_regex"]
                    # print("REGEX:", regex)
                    selected_field = tags[key][i]

                    try:
                        regex_result = findall(regex, selected_field)
                        if regex_result:
                            fields = list(regex_result[0])
                            fields = [i for i in fields if i]
                        else:
                            fields = []
                        print(fields)
                    except error as e:
                        msg = "Regex Expression Error: {}".format(str(e))
                        flash(msg)
                        return redirect(url_for("tag_discovery_all"))
                    except IndexError as ie:
                        flash("Regex Expression Error: Invalid character in the expression")
                        return redirect(url_for("tag_discovery_all"))
                    for x in range(len(fields)):
                        current_key = key + "_" + str(x + 1)
                        if current_key in new_tags and fields[x] not in new_tags[current_key]:
                            new_tags[current_key].append(fields[x])
                        elif current_key not in new_tags:
                            new_tags[current_key] = [fields[x]]

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    with open(complete_name, 'w+') as outfile:
        dump(new_tags, outfile)

    return redirect(url_for("tag_list_multiple"))


def get_tags():
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    try:
        with open(complete_name) as json_file:
            tags = load(json_file)
    except IOError:
        tags = {}
        with open(complete_name, 'w+') as outfile:
            dump(tags, outfile)
    if not tags and session['disco_choice'] == '2':
        tags = get_all_tags(session['dd_api_token'], session['dd_app_token'])

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name = path.join(save_path, "resources/%s/tags.json" % subdomain)

    with open(complete_name, 'w+') as outfile:
        dump(tags, outfile)
    max_tag_len = max([len(data) for data in tags.values()])

    return {'subdomain': subdomain,
            'tags': tags,
            'max_tag_len': max_tag_len}
