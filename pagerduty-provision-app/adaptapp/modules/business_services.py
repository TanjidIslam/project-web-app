from adaptapp.models.bizservice import BizService
from adaptapp.models.impactmetric import ImpactMetric
from time import time, gmtime, strftime


def biz_svc_get_payload(tags, customer_name, poi):
    biz_services = []

    for tag in tags[0]:
        if poi:
            point_of_contact = poi
        else:
            point_of_contact = "%s %s Ops Team" % (customer_name, tag)
        biz_service = {
            "name": "Business Service: %s" % tag,
            "point_of_contact": point_of_contact,
            "relationship": "supporting_services",
            "tech_name": tag
        }
        biz_services.append(biz_service)
    return biz_services


def impact_get_payload(tags):
    impact_metrics = []
    for tag in tags[0]:
        impact_metrics.append({
            "name": tag + ": Unique Sessions [count/min]"
        })
    return impact_metrics


def provision_business_services_metrics(service, hostname_parts, provision, hidden_session, chosen_combo):
    provision_biz_service = True
    if provision_biz_service:
        biz_service_name = service.provisioned_name

        all_biz_services = hidden_session.rget('/business_services?depth=all&offset=0&limit=100')

        for biz_service in all_biz_services:
            biz_service_exist = False
            existing_biz_name = biz_service['name']
            existing_biz_id = biz_service['id']

            if existing_biz_name == biz_service_name:
                biz_service_exist = True
                provision = False
            else:
                provision = True

        if provision:
            new_impact_metrics = provision_impact_metrics(service.provisioned_name)
            new_biz_service = provision_biz_associations(service, hostname_parts[chosen_combo[0]],
                                                         new_impact_metrics.id)


def provision_biz_associations(biz_name, biz_poc, biz_rel, company_name):
    new_biz_service = BizService(name=biz_name,
                                 description="[%s] Business Service provisioned by PagerDuty Expert Services ADAPT at " %
                                             company_name,
                                 point_of_contact=biz_poc,
                                 relationship=biz_rel)
    return new_biz_service


def provision_impact_metrics(is_name, company_name):
    time_now = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(int(time())))
    new_impact_metrics = ImpactMetric(name=is_name,
                                      aggregation_types=["average"],
                                      description="[%s] An example application KPI. Provisioned by PagerDuty Expert Services ADAPT at: %s" % (
                                          company_name, time_now),
                                      precision=0,
                                      unit_short="minutes",
                                      y_range_max=1500,
                                      y_range_min=1)
    return new_impact_metrics
