# Integration-specific event routing paths are defined here

INTEGRATION_PATH = {
    'zabbix': ["path", 'details', 'hostname'],
    'nagios': ["path", 'details', 'HOSTNAME'],
    'checkmk': ["path", 'details', 'HOSTNAME'],
    'datadog': ["path", "details", "tags"],
    'dynatrace': ["path", "details", "Tags"],
    'custom': ["path",""]
}
