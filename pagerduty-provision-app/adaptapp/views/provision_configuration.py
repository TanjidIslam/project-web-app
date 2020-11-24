from json import dump, load
from os import getcwd, path

from flask import request, render_template, session, redirect, url_for

from adaptapp import app
from adaptapp.modules.file_modifier import create_folder
from adaptapp.modules.tag import tag_extract


@app.route("/provision/combination/build", methods=["GET"])
def get_tag_config():
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_tags = path.join(save_path, "resources/%s/tags.json" % subdomain)
    complete_name_combo = path.join(save_path, "resources/%s/combos.json" % subdomain)
    complete_name_types = path.join(save_path, "resources/%s/types.json" % subdomain)
    complete_name_abs = path.join(save_path, "resources/%s/abstractions.json" % subdomain)
    complete_name_str = path.join(save_path, "resources/%s/str_abstractions.json" % subdomain)
    complete_name_sep = path.join(save_path, "resources/%s/separators.json" % subdomain)

    try:
        with open(complete_name_tags) as json_file:
            tags = load(json_file)
    except IOError:
        tags = {}
        with open(complete_name_tags, 'w+') as outfile:
            dump(tags, outfile)

    try:
        with open(complete_name_combo) as json_file:
            combo = load(json_file)
    except IOError:
        combo = []
        with open(complete_name_combo, 'w+') as outfile:
            dump(combo, outfile)

    try:
        with open(complete_name_types) as json_file:
            combo_types = load(json_file)
    except IOError:
        combo_types = {}
        with open(complete_name_types, 'w+') as outfile:
            dump(combo_types, outfile)

    try:
        with open(complete_name_abs) as json_file:
            service_abstractions = load(json_file)
    except IOError:
        service_abstractions = []
        with open(complete_name_types, 'w+') as outfile:
            dump(service_abstractions, outfile)

    try:
        with open(complete_name_str) as json_file:
            str_abstractions = load(json_file)
    except IOError:
        str_abstractions = []
        with open(complete_name_str, 'w+') as outfile:
            dump(str_abstractions, outfile)

    try:
        with open(complete_name_sep) as json_file:
            separators = load(json_file)
    except IOError:
        separators = []
        with open(complete_name_sep, 'w+') as outfile:
            dump(separators, outfile)

    tag_keys = list(tags.keys())
    session["tag_keys"] = tag_keys
    tags_size = len(tag_keys)
    if "ignored" in tags:
        tags_size -= 1
    print("TEST", combo_types)
    type_keys = list(combo_types.keys())
    return render_template("combination_config.html", tags=tags, tags_size=tags_size, tag_keys=tag_keys,
                           type_keys=type_keys,
                           disco_choice=session['disco_choice'], combo_types=combo_types,
                           subdomain=session['subdomain'],
                           provisioned=session['provisioned'], tags_exist=session['tags_exist'],
                           incidents_exist=session['incidents_exist'])


@app.route("/provision/combination/build", methods=["POST"])
def post_tag_config():
    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_combo = path.join(save_path, "resources/%s/combos.json" % subdomain)
    complete_name_types = path.join(save_path, "resources/%s/types.json" % subdomain)
    complete_name_abs = path.join(save_path, "resources/%s/abstractions.json" % subdomain)
    complete_name_str = path.join(save_path, "resources/%s/str_abstractions.json" % subdomain)
    complete_name_sep = path.join(save_path, "resources/%s/separators.json" % subdomain)

    try:
        with open(complete_name_combo) as json_file:
            combo = load(json_file)
    except IOError:
        combo = []
        with open(complete_name_combo, 'w+') as outfile:
            dump(combo, outfile)

    try:
        with open(complete_name_types) as json_file:
            combo_types = load(json_file)
    except IOError:
        combo_types = {}
        with open(complete_name_types, 'w+') as outfile:
            dump(combo_types, outfile)

    try:
        with open(complete_name_abs) as json_file:
            service_abstractions = load(json_file)
    except IOError:
        service_abstractions = []
        with open(complete_name_abs, 'w+') as outfile:
            dump(service_abstractions, outfile)

    try:
        with open(complete_name_str) as json_file:
            str_abstractions = load(json_file)
    except IOError:
        str_abstractions = []
        with open(complete_name_str, 'w+') as outfile:
            dump(str_abstractions, outfile)

    try:
        with open(complete_name_sep) as json_file:
            sep_list = load(json_file)
    except IOError:
        sep_list = []
        with open(complete_name_sep, 'w+') as outfile:
            dump(sep_list, outfile)

    max_combo = len(combo)
    if request.form["tag_action"] == "add":
        current_combo = []
        current_abstraction = []
        current_string = ""
        sep = " "
        if request.form.get("separator"):
            sep = request.form.get("separator")

        if sep != " ":
            sep = " " + sep + " "
        for i in range(5):
            tag_id = "tag_option_%s" % str(i)
            prefix_id = "prefix_%s" % str(i)
            suffix_id = "suffix_%s" % str(i)
            if request.form.get(tag_id):
                if request.form[tag_id] != "null":
                    if current_string:
                        current_string += sep
                    current_abstraction.append(['', '', ''])
                    index = len(current_abstraction) - 1
                    if request.form.get(prefix_id):
                        current_abstraction[index][0] = request.form.get(prefix_id)
                    current_abstraction[index][1] = request.form[tag_id]
                    current_combo.append(request.form[tag_id].strip())
                    if request.form.get(suffix_id):
                        current_abstraction[index][2] = request.form.get(suffix_id)
                    current_string += "".join(current_abstraction[index])
        if current_string not in str_abstractions:
            service_abstractions.append(current_abstraction)
            str_abstractions.append(current_string)
            combo.append(current_combo)
            sep_list.append(sep)
    elif request.form["tag_action"] == "delete":
        for i in range(len(service_abstractions)):
            # print(i, combo[i], request.form.get("service_%s" % str(i)))
            if request.form.get("service_%s" % str(i)):
                service_abstractions[i] = None
                combo[i] = None
                str_abstractions[i] = None
                sep_list[i] = None
                combo_types = {}

    with open(complete_name_abs, 'w+') as outfile:
        service_abstractions = [i for i in service_abstractions if i]
        dump(service_abstractions, outfile)
    # session["combo"] = [i for i in combo if i]
    temp_combo = combo[:]
    combo = [i for i in temp_combo if i]
    # session["str_abstractions"] = [i for i in str_abstractions if i]
    with open(complete_name_str, 'w+') as outfile:
        str_abstractions = [i for i in str_abstractions if i]
        dump(str_abstractions, outfile)

    # session["separators"] = [i for i in sep_list if i]
    with open(complete_name_sep, 'w+') as outfile:
        separators = [i for i in sep_list if i]
        dump(separators, outfile)

    complete_name_combo = path.join(save_path, "resources/%s/combos.json" % subdomain)

    with open(complete_name_combo, 'w+') as outfile:
        dump(combo, outfile)

    for i in range(len(combo)):
        combo_types["type%s" % str(i + 1)] = {'key': [], 'abstraction': '', 'separator': ''}
        combo_types["type%s" % str(i + 1)]['key'] = combo[i]
        combo_types["type%s" % str(i + 1)]['abstraction'] = service_abstractions[i]
        combo_types["type%s" % str(i + 1)]['string'] = str_abstractions[i]
        combo_types["type%s" % str(i + 1)]['separator'] = separators[i]
    # session["combo_types"] = combo_types

    with open(complete_name_types, 'w+') as outfile:
        dump(combo_types, outfile)

    with open(complete_name_combo, 'w+') as outfile:
        dump(combo, outfile)

    return redirect(url_for("get_tag_config"))


@app.route("/provision/combination/list", methods=["GET"])
def get_tag_combo():
    # combo_types = session["combo_types"]
    # service_abstractions = session["service_abstractions"]
    # string_abstraction = session["str_abstractions"]
    # separator = session["separators"]
    combo_tags = []
    # tags = session["tags"]
    # with open('resources\\tags.json') as json_file:
    #     tags = load(json_file)

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_types = path.join(save_path, "resources/%s/types.json" % subdomain)
    complete_name_combo = path.join(save_path, "resources/%s/combos.json" % subdomain)
    complete_name_abs = path.join(save_path, "resources/%s/abstractions.json" % subdomain)
    complete_name_str = path.join(save_path, "resources/%s/str_abstractions.json" % subdomain)
    complete_name_sep = path.join(save_path, "resources/%s/separators.json" % subdomain)

    try:
        with open(complete_name_sep) as json_file:
            separators = load(json_file)
    except IOError:
        separators = []
        with open(complete_name_sep, 'w+') as outfile:
            dump(separators, outfile)
    try:
        with open(complete_name_abs) as json_file:
            service_abstractions = load(json_file)
    except IOError:
        service_abstractions = []
        with open(complete_name_abs, 'w+') as outfile:
            dump(service_abstractions, outfile)

    try:
        with open(complete_name_str) as json_file:
            string_abstraction = load(json_file)
    except IOError:
        string_abstraction = []
        with open(complete_name_str, 'w+') as outfile:
            dump(string_abstraction, outfile)

    try:
        with open(complete_name_combo) as json_file:
            combo = load(json_file)
    except IOError:
        combo = []
        with open(complete_name_combo, 'w+') as outfile:
            dump(combo, outfile)

    try:
        with open(complete_name_types) as json_file:
            combo_types = load(json_file)
    except IOError:
        combo_types = {}
        with open(complete_name_types, 'w+') as outfile:
            dump(combo_types, outfile)

    complete_name_tags = path.join(save_path, "resources/%s/tags.json" % subdomain)

    try:
        with open(complete_name_tags) as json_file:
            tags = load(json_file)
    except IOError:
        tags = {}
        with open(complete_name_tags, 'w+') as outfile:
            dump(tags, outfile)

    complete_name_tag_combo = path.join(save_path, "resources/%s/tag_combo.json" % subdomain)

    try:
        with open(complete_name_tag_combo) as json_file:
            tag_combo = load(json_file)
    except IOError:
        tag_combo = {}
        with open(complete_name_tag_combo, 'w+') as outfile:
            dump(tag_combo, outfile)

    for type in combo_types:
        combo_tags.append(combo_types[type]['key'])

    tag_list = list(tags.keys())

    tag_combo = tag_extract(string_abstraction, combo_tags, tags, service_abstractions, separators)
    max_len = tag_combo["MAX_LEN_ADAPT"]
    tag_combo.pop("MAX_LEN_ADAPT")
    # session["tag_combo"] = tag_combo
    with open(complete_name_tag_combo, 'w+') as outfile:
        dump(tag_combo, outfile)

    type_keys = list(combo_types.keys())

    print("SERVICE ABS:", service_abstractions)
    print("TAG COMBO:", tag_combo)
    print("TAGS:", tags)
    print("COMBO:", combo)
    print("Abstraction:", service_abstractions)
    print("Types:", combo_types)
    print("String Abs:", string_abstraction)

    return render_template("combination_list.html", combo=service_abstractions, tag_combo=tag_combo, max_len=max_len,
                           disco_choice=session['disco_choice'], combo_types=combo_types, type_keys=type_keys,
                           incidents_exist=session['incidents_exist'],
                           string_abstraction=string_abstraction, subdomain=session['subdomain'],
                           provisioned=session['provisioned'], tags_exist=session['tags_exist'])


@app.route("/provision/combination/list", methods=["POST"])
def post_tag_combo():
    service_abstraction = request.form["tag"]
    # combo_types = session["combo_types"]

    subdomain = session["subdomain"]
    create_folder('resources/' + subdomain)

    save_path = getcwd()
    complete_name_types = path.join(save_path, "resources/%s/types.json" % subdomain)
    complete_name_abstraction = path.join(save_path, "resources/%s/service_abstraction.json" % subdomain)

    try:
        with open(complete_name_types) as json_file:
            combo_types = load(json_file)
    except IOError:
        combo_types = {}
        with open(complete_name_types, 'w+') as outfile:
            dump(combo_types, outfile)

    # session["service_abstraction"] = combo_types[service_abstraction]
    service_abstractions = combo_types[service_abstraction]
    with open(complete_name_abstraction, 'w+') as outfile:
        dump(service_abstractions, outfile)

    print("New ABS:", combo_types[service_abstraction])
    return redirect(url_for("get_provision_data"))
