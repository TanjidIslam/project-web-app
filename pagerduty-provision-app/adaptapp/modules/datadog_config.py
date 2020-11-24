from datadog import initialize, api


def get_all_tags(dd_api_key, dd_app_key):
    print(dd_api_key)
    print(dd_app_key)
    dd_config = {
        # 'source': 'CLOUDWATCH', #https://docs.datadoghq.com/integrations/faq/list-of-api-source-attribute-value/
        'api_key': dd_api_key,
        'app_key': dd_app_key
    }
    tags = {}
    try:
        initialize(**dd_config)
        all_tags = api.Tag.get_all()["tags"]
        for tag in all_tags:
            key_value =tag.split(":")
            if len(key_value) > 1:
                key = key_value[0]
                value = key_value[1]
            else:
                key = "untagged"
                value = tag
            if key in tags:
                if value not in tags[key]:
                    tags[key].append(value)
            else:
                tags[key] = [value]

    except Exception as e:
        print("Caught Error", e)
    return tags


def mass_update_tags(api_key, app_key, dd_hosts):
    dd_config = {
        # 'source': 'CLOUDWATCH', #https://docs.datadoghq.com/integrations/faq/list-of-api-source-attribute-value/
        'api_key': api_key,
        'app_key': app_key
    }
    response = None
    try:
        initialize(**dd_config)
        for host_name in dd_hosts:
            hostname = host_name
            hosts = api.Hosts.search(q='hosts:')

            for host in hosts['host_list']:
                if host['name'] == hostname:
                    tags = []
                    for key in dd_hosts[host_name]:
                        tags.append('%s:%s' % (key, dd_hosts[host_name][key]))
                    response = api.Tag.create(host['name'], tags=tags)
                    print(response)
    except Exception as e:
        print("Caught Error", e)
    return response


# if __name__ == "__main__":
#     api_key = '9ebd8d6fb06ddd405ed0fb90bde0f0cd'
#     app_key = '42c707c74a71977d154b88399c5cce5170a32da3'
#
#     dd_hosts = {
#         "CentOS-Nagios-PROD": {
#             "platform": "bff_web",
#             "env": "prod",
#             "integration": "nagios",
#             "reason": "kafka_events_consumed",
#             "region": "us-west",
#             "os": "CentOS"
#         },
#         "CentOS-Nagios-DEV": {
#             "platform": "bff_web",
#             "env": "dev",
#             "integration": "nagios",
#             "reason": "unexpected_failure_while_authenticating",
#             "region": "us-west",
#             "os": "CentOS"
#         },
#         "Ubuntu-Zabbix-PROD": {
#             "platform": "bff_mobile",
#             "env": "prod",
#             "integration": "zabbix",
#             "reason": "server_error",
#             "region": "us-east",
#             "os": "Ubuntu"
#         },
#         "Ubuntu-Prometheus-PROD": {
#             "platform": "bff_public_api",
#             "env": "prod",
#             "integration": "zabbix",
#             "reason": "proxy_error",
#             "region": "us-east",
#             "os": "Ubuntu"
#         }
#     }
#
#     # mass_update_tags(api_key, app_key, dd_hosts)
#     print(str(get_all_tags(api_key, app_key)).replace('\'','\"'))
