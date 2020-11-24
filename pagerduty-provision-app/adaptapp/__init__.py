from flask import Flask

app = Flask(__name__, static_url_path='')

# import after app is declared
from adaptapp.views import data_collection, service_discovery, event_discovery, field_discovery, provision_configuration, \
    provision_execution, deprovision_execution
