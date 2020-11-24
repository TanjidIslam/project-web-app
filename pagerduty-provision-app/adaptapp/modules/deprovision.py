from datetime import datetime
from traceback import print_exc

from pdpyras import APISession, PDClientError


def deprovision(global_api, user_api, api_logs, log_file, template):
    global_session = APISession(global_api)
    user_session = APISession(user_api)

    for key in api_logs:
        lf = open(log_file, 'a+')
        if "service" in api_logs[key]:
            service_id = api_logs[key]["service"]["id"]
            lf.write("\n[%s] [%s]: Deleting components for Service: %s [id: %s]" % (
            datetime.now(), 'Info', api_logs[key]['service']['name'], service_id))

        if "event_rules" in api_logs[key]:
            event_rules_id = api_logs[key]["event_rules"]["id"]
            delete_pd_field(global_session, event_rules_id, "event_rules", "Event Rules", log_file)

        if "service" in api_logs[key]:
            delete_pd_field(global_session, service_id, "services", "Service", log_file)

        if "business_service" in api_logs[key]:
            biz_service_id = api_logs[key]["business_service"]["id"]
            delete_pd_field(user_session, biz_service_id, "business_services", "Business Service", log_file)
        if "impact_metrics" in api_logs[key]:
            impact_metrics_id = api_logs[key]["impact_metrics"]["id"]
            delete_pd_field(user_session, impact_metrics_id, "business_impact_metrics", "Impact Metrics", log_file)

        lf.write("\n[%s] [%s]: Deleted all components for Service: %s [id: %s]" % (datetime.now(), 'Info', api_logs[key]['service']['name'], service_id))
        lf.close()


def delete_pd_field(api_session, id, endpoint, field, log_file):
    lf = open(log_file, 'a+')
    try:
        lf.write("\n[%s] [%s]: Deleting %s with id: %s" % (datetime.now(), 'Info', field, id))
        if endpoint == "services":
            api_session.rdelete("/%s/%s" % (endpoint, id))
        else:
            api_session.delete("/%s/%s" % (endpoint, id))
        lf.write("\n[%s] [%s]: Deleted %s with id: %s" % (datetime.now(), 'Info', field, id))
    except PDClientError as e:
        lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
        lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
        lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
        lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))
    lf.close()
