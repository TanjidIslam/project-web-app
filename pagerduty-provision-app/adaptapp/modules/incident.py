from time import time, gmtime, strftime

from pdpyras import APISession


def incident_iter_selected(api_key, duration, service_ids, integrations, all_tags):
    api_session = APISession(api_key)
    durations = {"0": 30, "1": 60, "2": 90, "3": 120, "4": 150, "5": 180, "6": 210, "7": 240, "8": 270, "9": 300,
                 "10": 330, "11": 360, "12": 440, "13": 720, "14": 900, "15": 1080}
    incidents = get_incidents(durations[duration], api_session, service_ids, integrations, all_tags)
    print("Found %s for Service %s for %s months with integration: %s" % (\
        str(len(incidents)), service_ids[0], str(int(duration) + 1), integrations))

    return incidents


def get_incidents(duration, api_session, service_ids, integrations, all_tags):
    incidents = []
    for i in range(30, duration + 30, 30):
        disco_param = discovery_params(i, service_ids)
        temp_incidents = iter_incidents(api_session, disco_param, integrations, all_tags)
        incidents = incidents + temp_incidents

    return incidents


def discovery_params(i, services):
    current_window = i + 5 if i == 360 else i
    time_today = int(time()) - ((i - 30) * 24 * 60 * 60)
    time_to = int(time()) - (current_window * 24 * 60 * 60)

    discover_from = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(time_today))
    discover_to = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(time_to))

    window_param = {'since': discover_to, 'until': discover_from, 'service_ids[]': [services], 'time_zone': 'UTC',
                    'include[]': ['first_trigger_log_entries']}
    return window_param


def iter_incidents(api_session, window_param, integrations, all_tags):
    all_incidents = []
    ignored = []

    count = 0

    # Making PagerDuty API calls for Incidents in this section
    for current_incident in api_session.iter_all('incidents', params=window_param, paginate=True):
        temp_incident = current_incident
        alerts = api_session.rget('incidents/%s/alerts' % current_incident['id'])
        try:
            temp_incident["all_alerts"] = alerts["alerts"]
        except TypeError:
            temp_incident["all_alerts"] = alerts
        if "[REDACTED] by" in current_incident['description']:
            continue

        ftle_channel = current_incident["first_trigger_log_entry"]["channel"]
        # print('--------\n',integrations)
        # print(ftle_channel['details'], '\n')
        if integrations.lower() == 'datadog' and 'tags' in ftle_channel['details']:
            tags = current_incident["first_trigger_log_entry"]["channel"]["details"]["tags"]
        elif integrations.lower() == 'dynatrace' and 'Tags' in ftle_channel['details']:
            tags = current_incident["first_trigger_log_entry"]["channel"]["details"]["Tags"]
        elif integrations.lower() == 'nagios' and 'host' in ftle_channel:
            tags = 'hostname:' + current_incident["first_trigger_log_entry"]["channel"]["host"]
        elif integrations.lower() == 'checkmk' and 'host' in ftle_channel:
            tags = current_incident["first_trigger_log_entry"]["channel"]["host"]
        else:
            tags = ""
        if tags:
            extract_tags(tags, all_tags)

        temp_incident["tags"] = tags
        temp_incident["integration"] = integrations
        all_incidents.append(temp_incident)
    return all_incidents


def extract_tags(current_tags, all_tags):
    first_layer_tags = current_tags.split(",")

    if "untagged" not in all_tags:
        all_tags["untagged"] = []

    for tag in first_layer_tags:
        tag_extract = tag.strip().replace(" ", "_").split(":")

        if len(tag_extract) == 1 and tag_extract[0] not in all_tags["untagged"]:
            all_tags["untagged"].append(tag_extract[0])
        elif len(tag_extract) == 2:
            if tag_extract[0] not in all_tags:
                all_tags[tag_extract[0]] = [tag_extract[1]]
            elif tag_extract[1] not in all_tags[tag_extract[0]]:
                all_tags[tag_extract[0]].append(tag_extract[1])
        elif len(tag_extract) == 3:
            if tag_extract[0] not in all_tags:
                all_tags[tag_extract[0]] = [tag_extract[1] + tag_extract[2]]
            elif tag_extract[1] + tag_extract[2] not in all_tags[tag_extract[0]]:
                all_tags[tag_extract[0]].append(tag_extract[1] + tag_extract[2])



# api_key = "ozhUyFftDxYFTR2rsVWQ"
# service_ids = ['PG8L64X', 'PYZQ56E']
# integrations = ['Datadog', 'Dynatrace']
# durations = ['5', '9', '10']
# print("---GETTING INCIDENTS---")
# incidents = []
# tags = {}
# for i in range(len(service_ids)):
#     print("---Getting incidents for %s in %s month(s)---" % (service_ids[i], str(int(durations[i]) + 1)))
#     incidents += incident_iter_selected(api_key, durations[i], service_ids[i], integrations[i], tags)
#
# print("---GOT INCIDENTS---")
#
# count = 1
# for incident in incidents:
#     print(count, incident)
#     count += 1
