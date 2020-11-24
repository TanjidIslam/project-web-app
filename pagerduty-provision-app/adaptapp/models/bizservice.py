from datetime import datetime
from logging import basicConfig, info, DEBUG
# from adaptapp.config.LoggingAPI import LoggerAPIConfig
from time import time, gmtime, strftime
from traceback import print_exc

from pdpyras import APISession, PDClientError


# log = LoggerAPIConfig.log


class BizService(object):
    """ An Incident Object """

    def __init__(self, name, description, point_of_contact, relationship, response_play="", linked_services=""):
        """ A new Incident with necessary fields """
        self.name = name
        self.description = description
        self.point_of_contact = point_of_contact
        self.response_play = response_play
        self.linked_services = linked_services
        self.relationship = relationship
        self.id = None
        self.payload = None
        self.supporting_services = None
        self.dependent_services = None

    def create(self, user_token, log_file):
        basicConfig(filename=log_file, level=DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

        lf = open(log_file, 'a+')

        time_now = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(int(time())))

        data = {"name": self.name, "description": self.description + time_now,
                "point_of_contact": self.point_of_contact,
                "response_play": self.response_play, self.relationship: self.linked_services}
        try:
            lf.write(
                "\n[%s] [%s]: ===============Creating Business Services==================" % (datetime.now(), 'Info'))
            lf.write("\n[%s] [%s]: Payload before POST: %s" % (datetime.now(), 'Info', data))

            session = APISession(user_token)
            provision_biz_service = session.rpost("/business_services", json={'business_service': data})
            info("===== The provisioned business service was: =====")

            # print(provision_biz_service.json())
            self.payload = provision_biz_service
            self.id = self.payload["id"]

            lf.write("\n[%s] [%s]: Metrics value: %s" % (datetime.now(), 'Info', self.payload))
            # print("BIZ PAYLOAD:", self.payload)
            lf.write("\n[%s] [%s]: =================== BUSINESS SERVICE CREATED ====================" % (
                datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))

        lf.close()

    def assign_impact_metrics(self, user_token, impact_id, log_file):
        # basicConfig(filename=log_file, level=DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
        #             datefmt='%Y-%m-%d %H:%M:%S')

        lf = open(log_file, 'a+')

        try:
            session = APISession(user_token)
            data = {
                "business_services": [{
                    "id": self.id,
                    "type": "business_service_reference"
                }]
            }
            lf.write(
                "\n[%s] [%s]: ===============Associating Impact Metrics==================" % (datetime.now(), 'Info'))
            lf.write("\n[%s] [%s]: Payload before POST: %s" % (datetime.now(), 'Info', data))

            assign_impect_metric = session.put("business_services/impact_metrics_associations/" + impact_id, json=data)
            lf.write("\n[%s] [%s]: Metrics value: %s" % (datetime.now(), 'Info', assign_impect_metric.json()))
            self.payload = assign_impect_metric.json()
            lf.write("\n[%s] [%s]: =================== IMPACT METRIC ASSOCIATED ====================" % (
                datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))

        lf.close()

    def assign_supporting_services(self, user_token, service_id, log_file):
        lf = open(log_file, 'a+')

        try:
            session = APISession(user_token)
            data = {
                "relationships": [
                    {
                        "dependent_service": {
                            "id": self.id,
                            "type": "business_service"
                        },
                        "supporting_service": {
                            "id": service_id,
                            "type": "service"
                        }
                    }
                ]
            }
            lf.write("\n[%s] [%s]: ===============Associating Supporting Services==================" % (
                datetime.now(), 'Info'))
            lf.write("\n[%s] [%s]: TESTING TECH SVC: %s" % (datetime.now(), 'Info', data))
            assign_tech_services = session.post("/service_dependencies/associate", json=data)

            self.payload = assign_tech_services
            lf.write("\n[%s] [%s]: Payload: %s" % (datetime.now(), 'Info', self.payload))

            lf.write("\n[%s] [%s]: =================== SUPPORTING SERVICES ASSOCIATED ====================" % (
                datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))

    def assign_dependent_services(self, user_token, service_id, log_file):
        lf = open(log_file, 'a+')

        try:
            session = APISession(user_token)
            data = {
                "relationships": [
                    {
                        "supporting_service": {
                            "id": self.id,
                            "type": "business_service"
                        },
                        "dependent_service": {
                            "id": service_id,
                            "type": "service"
                        }
                    }
                ]
            }
            lf.write("\n[%s] [%s]: ===============Associating Dependent Services==================" % (
                datetime.now(), 'Info'))
            lf.write("\n[%s] [%s]: TESTING TECH SVC: %s" % (datetime.now(), 'Info', data))
            assign_tech_services = session.post("/service_dependencies/associate", json=data)

            self.payload = assign_tech_services
            lf.write("\n[%s] [%s]: Payload: %s" % (datetime.now(), 'Info', self.payload))

            lf.write("\n[%s] [%s]: =================== DEPENDENT SERVICES ASSOCIATED ====================" % (
                datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))

    def assign_supporting_services_old(self, user_token, supporting_services, log_file):
        # basicConfig(filename=log_file, level=DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
        #         #             datefmt='%Y-%m-%d %H:%M:%S')
        lf = open(log_file, 'a+')

        try:
            session = APISession(user_token)
            data = {
                "business_service": {
                    "supporting_services": supporting_services
                }
            }
            lf.write("\n[%s] [%s]: ===============Associating Supporting Services==================" % (
                datetime.now(), 'Info'))
            lf.write("\n[%s] [%s]: TESTING TECH SVC: %s" % (datetime.now(), 'Info', data))
            assign_tech_services = session.put("/business_services/" + self.id, json=data)
            # print(assign_tech_services.json())
            self.payload = assign_tech_services.json()
            lf.write("\n[%s] [%s]: Payload: %s" % (datetime.now(), 'Info', self.payload))
            # self.supporting_services = self.payload["supporting_services"]
            lf.write("\n[%s] [%s]: =================== SUPPORTING SERVICES ASSOCIATED ====================" % (
                datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))

    def assign_dependent_services_old(self, user_token, dependent_services, log_file):
        # basicConfig(filename=log_file, level=DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
        #             datefmt='%Y-%m-%d %H:%M:%S')

        lf = open(log_file, 'a+')

        try:
            session = APISession(user_token)
            data = {
                "business_service": {
                    "dependent_services": dependent_services
                }
            }
            lf.write("\n[%s] [%s]: ===============Associating Supporting Services==================" % (
                datetime.now(), 'Info'))
            lf.write("\n[%s] [%s]: TESTING TECH SVC: %s" % (datetime.now(), 'Info', data))
            assign_tech_services = session.rput("/business_services/" + self.id, json=data)
            # print(assign_tech_services.json())
            self.payload = assign_tech_services
            lf.write("\n[%s] [%s]: Payload: %s" % (datetime.now(), 'Info', self.payload))
            # self.dependent_services = self.payload["business_service"]["dependent_services"]
            lf.write("\n[%s] [%s]: =================== DEPENDENT SERVICES ASSOCIATED ====================" % (
                datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))
        lf.close()

# def test():
#     name = "Test BS Adapt"
#     description = "Test Description Adapt"
#     point_of_contact = "ACME Test POC"
#
#     user_token = "XLjZzxgQ2pGkds724d-7"
#     # impact_id = "PNW9P6Z"
#     # global_token = "ozhUyFftDxYFTR2rsVWQ"
#     global_token = "ebzC6JE-yNT8JpCgrbyy"
#
#     supporting_service = {"id": "PRJR2U8", "type": "service_reference"}
#     # dependent_service = [{"id": "PSS7ZUS", "type": "business_service_reference"}]
#     service_id = "PRJR2U8"
#
#     new_biz_service = BizService(name, description, point_of_contact, "supporting_services")
#     new_biz_service.create(global_token, 'test_file.log')
#     # new_biz_service.assign_impact_metrics(user_token, impact_id, 'test_file.log')
#     new_biz_service.assign_supporting_services(global_token, service_id, 'test_file.log')
#     # new_biz_service.assign_dependent_services(global_token, dependent_service, 'test_file.log')


# Keep it commented for the test
# test()
