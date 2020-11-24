from adaptapp.models.service import Service


def service_test():
    name = "[Test] Service"
    description = "Test Description"
    status = "active"

    # Enter your EP ID
    escalation_policy = "P1Y3MTL"
    alert_creation = "create_alerts_and_incidents"
    alert_grouping = "time"

    global_token = "`"

    new_service = Service(name, description, status, escalation_policy, alert_creation, alert_grouping)
    new_service.create(global_token, 'test.log')

# Uncomment it to test and input your own global token/ep id
# service_test()
