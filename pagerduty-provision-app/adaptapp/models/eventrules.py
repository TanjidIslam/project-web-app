from pdpyras import APISession, PDClientError
from adaptapp.config.LoggingAPI import LoggerAPIConfig
from logging import basicConfig, debug, info, error, warning, DEBUG
from traceback import print_exc
from datetime import datetime

# log = LoggerAPIConfig.log


class EventRules(object):
    """ An Incident Object """

    def __init__(self, condition, actions, service_id):
        """ A new Incident with necessary fields """
        self.condition = condition
        self.actions = actions
        self.service_id = service_id
        self.payload = {}
        self.id = None

    def create(self, api_token, log_file):
        # basicConfig(filename=log_file, level=DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
        #             datefmt='%Y-%m-%d %H:%M:%S')

        lf = open(log_file, 'a+')
        data = {
            "condition": self.condition,
            "actions": [[self.actions, self.service_id]]
        }

        print("\n[%s] [%s]: Event Rules Before Payload: %s" % (datetime.now(), 'Info', data))
        # print(data)
        try:

            session = APISession(api_token)
            provision_event_rules = session.post("/event_rules", json=data)
            lf.write("\n[%s] [%s]: ===== The provisioned event rule was: =====" % (datetime.now(), 'Info'))

            self.payload = provision_event_rules.json()
            lf.write("\n[%s] [%s]: Event Rules Payload: %s" % (datetime.now(), 'Info', self.payload))
            print("\n[%s] [%s]: Event Rules Payload: %s" % (datetime.now(), 'Info', self.payload))
            self.id = self.payload["id"]
            lf.write("\n[%s] [%s]: EVent Rules ID: %s" % (datetime.now(), 'Info', self.id))

            lf.write("\n[%s] [%s]: =================== EVENT RULE CREATED ====================" % (datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))
        lf.close()

# def event_rules():
#     condition = ["and", ["contains", ["path", "payload","source"], 'website'], ["contains", ["path", 'payload', 'source'], 'api']]
#     action = "route"
#     service_id = 'PCX31Z5'
#     new_ger = EventRules(condition, action, service_id)
#     new_ger.create('ebzC6JE-yNT8JpCgrbyy', 'blah.log')
#
#
# event_rules()
# payload = {'condition': ['and', ['contains', ['path', 'client', ''], 'test']], 'actions': ['route', 'PCX31Z5']}
