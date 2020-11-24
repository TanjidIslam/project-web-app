from datadog import initialize, api
from pdpyras import APISession, PDClientError


def is_token_valid(api_token):
    session = APISession(api_token)

    try:
        response = session.get("/users?limit-1&offset=0")

        if response.status_code == 200:
            return True
    except PDClientError:
        return False


def is_dd_token_valid(api_token, app_token):
    datadog_config = {
        # 'source': 'CLOUDWATCH', #https://docs.datadoghq.com/integrations/faq/list-of-api-source-attribute-value/
        'api_key': api_token,
        'app_key': app_token
    }
    try:
        initialize(**datadog_config)
        api.User.get_all()
    except Exception as e:
        return False
    return True


def is_service_valid(api_token, service_id):
    session = APISession(api_token)

    try:
        response = session.rget("/services/" + service_id)
        if response:
            return True
        return False
    except PDClientError:
        return False


def is_ep_valid(api_token, ep_id):
    session = APISession(api_token)

    try:
        response = session.rget("/escalation_policies/" + ep_id)
        if response:
            return True
        return False
    except PDClientError:
        return False


def get_subdomain(auth_token):
    account = APISession(auth_token)
    try:
        subdomain = account.subdomain
    except Exception as e:
        subdomain = None
    if subdomain is None:
        subdomain = 'NETWORK_ERR_OR_TOKEN_INVALID'
        print(subdomain)
    return subdomain

# print(is_service_valid('ebzC6JE-yNT8JpCgrbyy', 'PRJR2U8'))
# print(is_ep_valid('ebzC6JE-yNT8JpCgrbyy', 'P1Y3MTL'))
