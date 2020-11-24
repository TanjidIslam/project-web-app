from flask import render_template
from requests import get

from config import WaveAppsConfig
from solution import app
from solution.product import ObjectProduct


@app.route('/')
def run_app():
    url = WaveAppsConfig.URL
    token = WaveAppsConfig.ACCESS_TOKEN
    b_id = WaveAppsConfig.BUSINESS_ID

    # Get access to the API and return response 200 if succeeds
    get(url + 'user/', headers={'Authorization': "Bearer " + token})

    # Get business product data as a json->dictionary
    products = get(url + 'businesses/' + b_id + '/products/', headers={'Authorization': "Bearer " + token}).json()

    # Convert each entry into an object
    for i in range(len(products)):
        products[i] = ObjectProduct(**products[i])

    return render_template('index.html', welcome="Hello, Welcome", products=products)


