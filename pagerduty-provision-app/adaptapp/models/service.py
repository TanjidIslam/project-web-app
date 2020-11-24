from datetime import datetime
from traceback import print_exc

from pdpyras import APISession, PDClientError


# log = LoggerAPIConfig.log


class Service(object):
    """ A Service Object """

    def __init__(self, name, description, status, escalation_policy, alert_creation, alert_grouping,
                 time_grouping=None):
        """ A new Service instance with necessary fields """
        self.name = name
        self.description = description
        self.status = status
        self.escalation_policy = escalation_policy
        self.alert_creation = alert_creation
        self.alert_grouping = alert_grouping
        self.time_grouping = time_grouping
        self.provisioned_name = None
        self.id = None
        self.response_code = None
        self.html_url = None
        self.payload = None

    def create(self, api_token, log_file):
        """ (this, str, str) -> NoneType
        Given API token key and path to the log file Create a PagerDuty Service associated with the API token

        """

        # Logfile for writing service API logs
        lf = open(log_file, 'a+')

        data = {"name": self.name, "description": self.description, "status": self.status,
                "escalation_policy": {"id": self.escalation_policy, "type": "escalation_policy_reference"},
                "alert_creation": self.alert_creation, "alert_grouping": self.alert_grouping}

        if self.time_grouping:
            data["alert_grouping_timeout"] = self.time_grouping

            lf.write("\n[%s] [%s] ===== Provisioning Service =====" % (datetime.now(), 'Info'))
            lf.write("\n[%s] [%s] Payload before provisioning: %s" % (datetime.now(), 'Info', data))
        try:
            session = APISession(api_token)
            provision_service = session.rpost("/services", json={'service': data})

            lf.write("\n[%s] [%s] Provisioned Service: %s" % (datetime.now(), 'Info:', provision_service['name']))

            self.provisioned_name = provision_service['name']
            self.id = provision_service['id']
            self.html_url = provision_service['html_url']
            self.payload = provision_service

            lf.write("\n[%s] [%s] =================== SERVICE CREATED ====================" % (datetime.now(), 'Info'))

        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))

        lf.close()
