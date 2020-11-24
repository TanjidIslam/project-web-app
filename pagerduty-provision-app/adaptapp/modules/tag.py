import itertools
from copy import deepcopy
from re import findall, error


def tag_extract(combo, combo_tags, tags, service_abstractions, separator):
    data_combo = extract_combo_tokens(combo_tags, tags, service_abstractions)
    print("Data Combo:", data_combo)

    tag_combo = []
    tag_combo_2 = []
    for data in data_combo:
        tag_combo.append(list(itertools.product(*data[0])))
        tag_combo_2.append(list(itertools.product(*data[1])))
    print("Tag Combo 1:", tag_combo)
    print("Tag Combo 2:", tag_combo_2)

    top_layers = []
    top_layers_2 = []
    for i in range(len(tag_combo)):
        bot_layers = []
        bot_layers_2 = []
        sep = separator[i]
        for layer2 in tag_combo[i]:
            layer_str = ""
            for layer3 in layer2:
                layer_str += layer3 + sep
            bot_layers.append(layer_str.strip(sep))
        top_layers.append(bot_layers)
        for layer2 in tag_combo_2[i]:
            layer_str = ""
            for layer3 in layer2:
                layer_str += layer3 + ":"
            bot_layers_2.append(layer_str.strip(":"))
        top_layers_2.append(bot_layers_2)
    print("Top Layer 1:", top_layers)
    print("Top Layer 2:", top_layers_2)

    mapped_tags = map_tags(combo, top_layers, top_layers_2)

    return mapped_tags


def extract_combo_tokens(combo_tags, tags, service_abstractions):
    data_combo = []

    print(len(combo_tags), 'vs', len(service_abstractions))
    print("combo_tags:", combo_tags)
    print("service_abstraction:", service_abstractions)
    for i in range(len(combo_tags)):
        print("tag_list:", combo_tags[i])
        extract_combo = []
        extract_combo_2 = []
        temp_abstraction = service_abstractions[:]
        for j in range(len(combo_tags[i])):
            print("tag:", combo_tags[i][j])
            temp_tags = tags[combo_tags[i][j].strip()]
            temp_extract = []
            temp_extract_2 = []
            for tag in temp_tags:
                print("TANJID TEST:", tag)
                temp_extract_2.append(tag)
                temp_extract.append(''.join([temp_abstraction[i][j][0], tag, temp_abstraction[i][j][2]]))
            extract_combo.append(temp_extract)
            extract_combo_2.append(temp_extract_2)
        data_combo.append([extract_combo, extract_combo_2])
    return data_combo


def map_tags(combo, top_layers, top_layers_2):
    tag_map = {}
    tag_map["MAX_LEN_ADAPT"] = 0
    print("TOP LAYER:", top_layers)
    print("COMBO?:", combo)
    for i in range(len(combo)):
        tag_map[combo[i]] = [top_layers[i], top_layers_2[i]]
        current_len = len(top_layers[i])
        print("CURRENT LEN:", current_len)
        if current_len > tag_map["MAX_LEN_ADAPT"]:
            tag_map["MAX_LEN_ADAPT"] = current_len
            print("MAX LEN:", tag_map["MAX_LEN_ADAPT"])
    return tag_map


def extract_key_value(tags, key):
    new_tags = deepcopy(tags)
    for i in range(len(tags[key])):
        fields = ""
        if ';' in tags[key]:
            fields = tags[key].split(";")
        elif ',' in tags[key]:
            fields = tags[key].split(',')

        if not fields:
            print("No Key:value/Key=value format found")
            continue

        for field in fields:
            if '=' not in field or ':' not in field:
                print("No Key:value/Key=value format found")
                continue
            temp = field.replace("=", ":")
            if temp.split(":")[0] in new_tags and temp.split(":")[1] not in new_tags[temp.split(":")[0]]:
                new_tags[temp.split(":")[0]].append(temp.split(":")[1])
            else:
                new_tags[temp.split(":")[0]] = [temp.split(":")[1]]
        new_tags[key].remove(tags[key][i])
        if not new_tags[key]:
            new_tags.pop(key)
    return new_tags


def extract_separators(tags, key):
    new_tags = deepcopy(tags)
    for i in range(len(tags[key])):
        selected_field = tags[key][i]
        hostname = selected_field.replace(".", "_").replace("-", "_").replace(" ", "_").replace(":", "_")
        if "_" in hostname:
            fields = hostname.split("_")
        else:
            print("No separators found to extract")
            continue
        for x in range(len(fields)):
            current_key = key + "_" + str(x + 1)
            if current_key in new_tags and fields[x] not in new_tags[current_key]:
                new_tags[current_key].append(fields[x])
            elif current_key not in new_tags:
                new_tags[current_key] = [fields[x]]
    return new_tags


def extract_regex(regex, tags, key):
    new_tags = deepcopy(tags)
    for i in range(len(tags[key])):
        current_field = tags[key][i]
        while True:
            try:
                regex_result = findall(regex, current_field)
                if regex_result:
                    fields = list(regex_result[0])
                    fields = [i for i in fields if i]
                else:
                    fields = []
                break
            except error as e:
                msg = "Regex Expression Error: {}".format(str(e))
                print(msg)
                continue
            except IndexError as ie:
                print("Regex Expression Error: Invalid character in the expression")
                continue
        for x in range(len(fields)):
            current_key = key + "_" + str(x + 1)
            if current_key in new_tags and fields[x] not in new_tags[current_key]:
                new_tags[current_key].append(fields[x])
            elif current_key not in new_tags:
                new_tags[current_key] = [fields[x]]
    return new_tags


# def map_tags(combo, top_layers):
#     tag_map = {}
#     tag_map["MAX_LEN_ADAPT"] = 0
#     print("TOP LAYER:", top_layers)
#     for i in range(len(combo)):
#         tag_map[combo[i]] = top_layers[i]
#         if len(tag_map[combo[i]]) > tag_map["MAX_LEN_ADAPT"]:
#             tag_map["MAX_LEN_ADAPT"] = len(tag_map[combo[i]])
#     return tag_map

#
# combo = ['platform', 'region', 'reason', 'platform : region', 'platform : reason', 'reason : region',
#          'platform : reason : region', 'platform : pd_chef_env']
# combo_tags = [['platform'], ['region'], ['reason'], ['platform ', ' region'], ['platform ', ' reason'],
#               ['reason ', ' region'], ['platform ', ' reason ', ' region'], ['platform ', ' pd_chef_env']]
# tags = {'aws_env': ['prod', 'dr'], 'aws_type': ['prod-bffmobile-app', 'dr-bffmobile-app'], 'direction': ['above'],
#         'env': ['production', 'prod', 'prod-bffmobile', 'dr-bffmobile'],
#         'host': ['prod-bffmobile-app06', 'prod-bffmobile-app07', 'prod-bffmobile-app03', 'dr-bffmobile-app02',
#                  'dr-bffmobile-app04'], 'ignored': ['aws-prod', 'base', 'bffmobile-app', 'production'],
#         'instance_index': ['2', '0', '1', '4'], 'pd_az': ['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-1b'],
#         'pd_chef_env': ['prod-bffmobile', 'dr-bffmobile'], 'pd_deployment_env_of_host': ['production'],
#         'pd_env': ['production'], 'pd_world': ['production'], 'platform': ['bff_mobile', 'bff_web', 'bff_public_api'],
#         'reason': ['unexpected_failure_while_authenticating', 'kafka_events_consumed', 'server_error', 'response_count',
#                    'proxy_error', 'authenticate_request_count', 'slack_auth_hmac_check_fails',
#                    'authentication_attempt_count'], 'region': ['us-west-1', 'us-west-2'], 'result': ['failure'],
#         'untagged': ['auto-managed', 'monitor']}
#
# print(tag_extract(combo, combo_tags, tags))
