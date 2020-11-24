from time import time, gmtime, strftime
from pdpyras import APISession
import re
from adaptapp.models.service import Service
from adaptapp.models.eventrules import EventRules
from adaptapp.models.bizservice import BizService
from adaptapp.models.impactmetric import ImpactMetric

services = ['PRJR2U8']
regex = r"([^\-\:]+)"
min_service_name = 4
service_combo = [["SCOM", 2],  # environment
                 ["SCOM", 3],
                 ["SCOM", 3, 4],
                 []]  # application
# i.e. AWS-SE-PROD:IT21-TA-04
# i.e. [0]-[1]-[2]:[3]-[4]-[5]
chosen_combo = [3, 4, 1]
catch_all_ep = "P1Y3MTL"
rest_api_token = "ebzC6JE-yNT8JpCgrbyy"
user_api_token = 'XSz_byZVtm7CobA8RxNm'
session = APISession(rest_api_token)
hidden_session = APISession(user_api_token)
company_name = "ACME Company"
dependent_services = {}
DURATION = 360


def process(duration):
    for i in range(30, duration + 30, 30):
        window_param = discovery_window(i)
        provision(session, window_param)


def discovery_window(i):
    current_window = i + 5 if i == 360 else i
    time_today = int(time()) - ((i - 30) * 24 * 60 * 60)
    time_to = int(time()) - (current_window * 24 * 60 * 60)

    discover_from = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(time_today))
    discover_to = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(time_to))

    window_param = {'since': discover_to, 'until': discover_from, 'service_ids[]': [services], 'time_zone': 'UTC',
                    'include[]': ['first_trigger_log_entries']}
    return window_param


def provision(session, window_param):
    incident_counter = 0
    host_list = []
    current_services = {}
    # provision_biz_service = True
    for incident in session.iter_all('incidents', params=window_param, paginate=True):
        incident_counter += 1

        ftle = incident['first_trigger_log_entry']
        if ftle['channel']['cef_details']['source_origin']:
            hostname = ftle['channel']['cef_details']['source_origin']
            host_list.append(hostname)
            hostname_parts = re.findall(regex, hostname)
            if len(hostname_parts) < min_service_name:
                continue

            condition = ["and"]
            service_abstraction = service_host_extract(hostname_parts, condition)
            print("The discovered serviceAbstraction is:=====>" + service_abstraction)

            provision = verify_service(service_abstraction, current_services)

            if provision:
                new_service = provision_service(service_abstraction)
                current_services[new_service.provisioned_name] = new_service.provisioned_id
                print("Current Services are", current_services)
                if new_service.response_code == 2001:
                    continue

                if new_service.provisioned_name:
                    new_event_rule = provision_event_rules(new_service, condition)
                    provision_business_services_metrics(new_service, hostname_parts, provision)


def provision_service(service_abstraction):
    time_now = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(int(time())))
    new_service = Service(name=service_abstraction,
                          description="This service was created using the PagerDuty Expert Services ADAPT Solution. Provisioned at: " + time_now,
                          status="active",
                          escalation_policy="P1Y3MTL",
                          alert_creation="create_alerts_and_incidents",
                          alert_grouping="intelligent")
    new_service.create(rest_api_token)
    return new_service


def provision_event_rules(new_service, condition):
    service_id = new_service.provisioned_id
    action = "route"
    new_event_rule = EventRules(condition, action, service_id)
    new_event_rule.create(rest_api_token)
    return new_event_rule


def provision_business_services_metrics(service, hostname_parts, provision):
    provision_biz_service = True
    if provision_biz_service:
        # Change if you wanna modify biz service name
        biz_service_name = service.provisioned_name
        print("The proposed biz svc is: ", biz_service_name)

        all_biz_services = hidden_session.rget('/business_services?depth=all&offset=0&limit=100')

        for biz_service in all_biz_services:
            biz_service_exist = False
            existing_biz_name = biz_service['name']
            existing_biz_id = biz_service['id']

            if existing_biz_name == biz_service_name:
                biz_service_exist = True
                provision = False
            else:
                provision = True
        print("Will the service be provisioned?", provision)

        if provision:
            new_impact_metrics = provision_impact_metrics(service.provisioned_name)
            new_biz_service = provision_biz_associations(service, hostname_parts[chosen_combo[0]], new_impact_metrics.id)


def provision_impact_metrics(service_name):
    time_now = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(int(time())))
    new_impact_metrics = ImpactMetric(name=service_name + ": Unique Sessions [count/min]",
                                      aggregation_types=["average"],
                                      description="[%s] An example application KPI. Provisioned by PagerDuty Expert Services ADAPT at: %s" % (
                                          company_name, time_now),
                                      precision=0,
                                      unit_short="minutes",
                                      y_range_max=1500,
                                      y_range_min=1)
    new_impact_metrics.create(user_api_token)
    return new_impact_metrics


def provision_biz_associations(service, tech_name, impact_id):
    time_now = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(int(time())))
    new_biz_service = BizService(name="Dependant Service: %s" % service.provisioned_name,
                                 description="[%s] Business Service provisioned by PagerDuty Expert Services ADAPT at %s" % (
                                     company_name, time_now),
                                 point_of_contact='%s %s Ops Team' % (company_name, tech_name))
    new_biz_service.create(user_api_token)
    new_biz_service.assign_impact_metrics(user_api_token, impact_id)

    supporting_service = [{"id": service.provisioned_id, "type": "service_reference"}]

    new_biz_service.assign_technical_services(user_api_token, company_name, tech_name, supporting_service)

    # if tech_name in service.provisioned_name:
    #     if tech_name not in supporting_services:
    #         supporting_services[tech_name] = {
    #             service.provisioned_id: [
    #                 {"id": service.provisioned_id, "type": "service_reference", "name": service.provisioned_name}]}
    #     else:
    #         if service.provisioned_id not in supporting_services[tech_name]:
    #             supporting_services[tech_name][service.provisioned_id].append({"id": service.provisioned_id,
    #                                                                            "type": "service_reference",
    #                                                                            "name": service.provisioned_name})
    # new_biz_service.assign_technical_services(user_api_token, company_name, tech_name,
    #                                           supporting_services=supporting_services[tech_name][
    #                                               service.provisioned_id])
    return new_biz_service


def service_host_extract(hostname_parts, condition):
    service_abstraction = ""
    for i in range(len(chosen_combo)):
        if i != len(chosen_combo) - 1:
            service_abstraction += hostname_parts[chosen_combo[i]] + " : "
        else:
            service_abstraction += hostname_parts[chosen_combo[i]]
        condition.append(["contains", ["path", "payload", "source"], hostname_parts[chosen_combo[i]]])
    return service_abstraction


def verify_service(service_abstraction, current_services):
    provision = False
    all_services = list(
        session.iter_all('services', params={'query': service_abstraction}, paginate=True))

    print("Is there a matching service?")
    print(all_services)

    matched_services = []
    matched_services_count = 0

    for matched_service in all_services:
        service_name = matched_service["name"]
        matched_services.append(service_name)
        matched_services_count += 1

    if service_abstraction not in matched_services:
        print("The current service list is:", current_services)

    if service_abstraction in current_services.keys():
        existing_service = service_abstraction
        print("The service already exists: ", existing_service)
    else:
        print("The service will be provisioned: ", service_abstraction)
        provision = True
    print("Will the service be provisioned?", provision)
    return provision



# process(DURATION)
