from pdpyras import APISession, PDClientError
from adaptapp.config.LoggingAPI import LoggerAPIConfig
from logging import basicConfig, debug, info, error, warning, DEBUG
from traceback import print_exc
from datetime import datetime

# log = LoggerAPIConfig.log


class ImpactMetric(object):
    """ An Incident Object """

    def __init__(self, name, description, aggregation_types, precision, unit_short, y_range_max, y_range_min):
        """ A new Incident with necessary fields """
        self.name = name
        self.description = description
        self.aggregation_types = aggregation_types
        self.precision = precision
        self.unit_short = unit_short
        self.y_range_max = y_range_max
        self.y_range_min = y_range_min
        self.payload = {}
        self.id = ""
        self.provisioned_name = ""

    def create(self, user_token, log_file):
        # basicConfig(filename=log_file, level=DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
        #             datefmt='%Y-%m-%d %H:%M:%S')

        lf = open(log_file, 'a+')

        data = {"name": self.name, "description": self.description, "aggregation_types": self.aggregation_types,
                "precision": self.precision, "unit_short": self.unit_short, "y_range_max": self.y_range_max,
                "y_range_min": self.y_range_min}
        try:
            session = APISession(user_token)
            provision_impact_metric = session.post("/business_impact_metrics", json={'business_impact_metric': data})
            lf.write("\n[%s] [%s]: ===== The provisioned business impact metric was: =====" % (datetime.now(), 'Info'))
            lf.write("\n[%s] [%s]: Business Impact Metrics response: %s" % (datetime.now(), 'Info', str(provision_impact_metric.json())))
            self.payload = provision_impact_metric.json()
            self.id = provision_impact_metric.json()["business_impact_metric"]["id"]
            self.provisioned_name = provision_impact_metric.json()["business_impact_metric"]["name"]
            lf.write("\n[%s] [%s]: =================== BUSINESS IMPACT METRIC CREATED ====================" % (datetime.now(), 'Info'))
        except PDClientError as e:
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.url))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', e.response.text))
            lf.write("\n[%s] [%s]: %s" % (datetime.now(), 'Error', print_exc()))
        lf.close()

# def test2():
#     name = "TJ Impact Metric"
#     description = "Test Metric Services Description and Stuff yo"
#     aggregation_types = ["average"]
#     precision = 0
#     unit_short = "minutes"
#     y_range_max = 1500
#     y_range_min = 1
#     new_impact_metric = ImpactMetric(name, description, aggregation_types, precision, unit_short, y_range_max, y_range_min)
#     new_impact_metric.create("XLjZzxgQ2pGkds724d-7")
#
# # Keep it commented for the test
# test2()
