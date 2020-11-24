from pdpyras import APISession, PDClientError


def ep_iter_all(api_key):
    api_session = APISession(api_key)
    all_ep = list(api_session.iter_all("escalation_policies"))

    return all_ep


def get_ep(api_token):
    while True:
        ep_id = input("Enter a default Escalation Policy ID: ")

        try:
            session = APISession(api_token)
            ep_object = session.rget("/escalation_policies/%s" % ep_id)
            break
        except PDClientError as e:
            print(e.response)
            print(e.response.url)
            print(e.response.text)

            print("Some errors happened. Try again.\n")
    return ep_object
