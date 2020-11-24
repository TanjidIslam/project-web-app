from adaptapp.models.eventrules import EventRules


def get_event_rules(tags, service, path):
    conditions = []
    for i in range(len(tags[1])):
        condition = ['and']
        split_tags = tags[1][i].split(":")
        for tag in split_tags:
            condition.append(["contains", path, tag])
        event_rules_payload = {"condition": condition,
                               "str_rep": cond_to_str(condition, tags[0][i])}
        conditions.append(event_rules_payload)
    return conditions


def cond_to_str(condition, service):
    text_format = ""
    gate = {"and": "All", "or": "Any"}

    for item in condition:
        if item in ['and', 'or']:
            text_format += "If <strong>%s</strong> of the following conditions are true:" % gate[item]
        else:
            field = '.'.join(item[1][1:])
            rule = item[0]
            keyword = item[2]
            text_format += "<br>    <em>%s</em> %s '%s'" % (field, rule, keyword)
    return text_format[:-1] + "<br>        then provision to current associated service: <strong>%s</strong>." % service


def provision_event_rules(new_service, condition, current_service_id):
    service_id = new_service.id
    action = "route"
    new_event_rule = EventRules(condition, action, current_service_id)
    return new_event_rule

# all_tags = ['bff_mobile : prod-bffmobile', 'bff_mobile : dr-bffmobile', 'bff_web : prod-bffmobile',
#             'bff_web : dr-bffmobile', 'bff_public_api : prod-bffmobile', 'bff_public_api : dr-bffmobile']
# conditions = get_event_rule(all_tags)
# print()
