from time import time, gmtime, strftime

from pdpyras import APISession, PDClientError

from adaptapp.models.service import Service


def get_service(api_token, service_id):
    try:
        session = APISession(api_token)
        service = session.rget("/services/%s" % service_id)
        if not service['last_incident_timestamp']:
            print("The selected service '%s' [%s] has no incident" % (service['summary'], service['id']))
            service = None
    except PDClientError as e:
        # print(e.response)
        # print(e.response.url)
        # print(e.response.text)

        service = None

    return service


def service_iter_all(api_key):
    api_session = APISession(api_key)
    all_services = list(api_session.iter_all("services"))

    return all_services


def service_iter_print(api_key):
    api_session = APISession(api_key)
    # all_services = list(api_session.iter_all("services"))
    count = 1
    for service in api_session.iter_all("services"):
        print(count, service)
        count += 1
    # return all_services


def service_iter_selected(api_key, service_ids):
    api_session = APISession(api_key)
    all_services = []

    for service_id in service_ids:
        service = api_session.rget('/services/%s' % service_id)
        all_services.append(service)
    return all_services


def service_get_payload(tags, ep, alert_creation, alert_grouping, time_grouping):
    services = []

    for tag in tags[0]:
        service = {"name": tag,
                   "ep_id": ep,
                   "alert_creation": alert_creation,
                   "alert_grouping": alert_grouping}
        if alert_grouping == "time":
            service["alert_grouping_timeout"] = int(time_grouping)
        print(service)
        services.append(service)

    return services


def provision_service(service_abstraction, ep, alert_creation, alert_grouping):
    time_now = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(int(time())))
    new_service = Service(name=service_abstraction,
                          description="This service was created using the PagerDuty Expert Services ADAPT Solution. Provisioned at: " + time_now,
                          status="active",
                          escalation_policy=ep,
                          alert_creation=alert_creation,
                          alert_grouping=alert_grouping)
    return new_service


def flatten(d, sep="[]"):
    import collections

    obj = collections.OrderedDict()

    def recurse(t, parent_key=""):

        if isinstance(t, list):
            for i in range(len(t)):
                recurse(t[i], parent_key + sep[0] + str(i) + sep[1] if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep[0] + k + sep[1] if parent_key else k)
        else:
            obj[parent_key] = t

    recurse(d)
    return dict(obj)

# api_key = "ebzC6JE-yNT8JpCgrbyy"
# api_key = "QxYPNEw5vvAGZeCPxp9J"
# service_iter_print(api_key)
#
# example = {'id': 'PG8L64X', 'name': 'ACME BFF Watcher', 'description': 'Monitoring Backend-for-Frontend tools',
#            'created_at': '2019-11-28T00:49:25Z', 'status': 'active',
#            'teams': [
#                {'id': 'PI6CL9Q', 'type': 'team_reference', 'summary': 'DD Responders',
#                 'self': 'https://api.pagerduty.com/teams/PI6CL9Q',
#                 'html_url': 'https://pdt-tislam-adapt.pagerduty.com/teams/PI6CL9Q'}],
#            'alert_creation': 'create_alerts_and_incidents', 'addons': [], 'scheduled_actions': [],
#            'support_hours': None, 'last_incident_timestamp': '2019-11-28T02:58:25Z',
#            'escalation_policy': {
#                'id': 'PHJJ801', 'type': 'escalation_policy_reference', 'summary': 'Engineers',
#                'self': 'https://api.pagerduty.com/escalation_policies/PHJJ801',
#                'html_url': 'https://pdt-tislam-adapt.pagerduty.com/escalation_policies/PHJJ801'},
#            'incident_urgency_rule': {'type': 'constant', 'urgency': 'high'}, 'acknowledgement_timeout': None,
#            'auto_resolve_timeout': None, 'alert_grouping': 'intelligent', 'alert_grouping_timeout': None,
#            'integrations': [
#                {'id': 'PRT47QR', 'type': 'generic_events_api_inbound_integration_reference', 'summary': 'Datadog',
#                 'self': 'https://api.pagerduty.com/services/PG8L64X/integrations/PRT47QR',
#                 'html_url': 'https://pdt-tislam-adapt.pagerduty.com/services/PG8L64X/integrations/PRT47QR'},
#                {'id': 'PXX5BHV', 'type': 'events_api_v2_inbound_integration_reference', 'summary': 'Manual Events',
#                 'self': 'https://api.pagerduty.com/services/PG8L64X/integrations/PXX5BHV',
#                 'html_url': 'https://pdt-tislam-adapt.pagerduty.com/services/PG8L64X/integrations/PXX5BHV'}],
#            'response_play': None, 'type': 'service', 'summary': 'ACME BFF Watcher',
#            'self': 'https://api.pagerduty.com/services/PG8L64X',
#            'html_url': 'https://pdt-tislam-adapt.pagerduty.com/services/PG8L64X'}
# print(flatten(example))
