def impact_get_payload(tags):
    impact_metrics = []
    for tag in tags:
        impact_metrics.append({
            "name": tag + ": Unique Sessions [count/min]"
        })
    return impact_metrics
