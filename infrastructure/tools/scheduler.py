import pulumi_gcp as gcp
import json
import base64
from service_account import scheduler_service_account


def make_scheduled_job(
        name: str,
        description: str,
        schedule: str,
        uri: str,
        service_account: gcp.serviceaccount.Account,
        body: None = None,
):
    time_zone = "America/Los_Angeles"  # PDT timezone

    http_target = {
        "httpMethod": "POST",
        "uri": uri,
        "headers": {
            "Content-Type": "application/json",
        },
        "oidc_token": {
            "service_account_email": scheduler_service_account.email,
            "audience": uri,
        },
    }
    if isinstance(body, dict):
        json_string = json.dumps(body).strip()
        http_target["body"] = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

    job = gcp.cloudscheduler.Job(
        f"cloud-scheduler-job-{name}",
        name=name,
        description=description,
        schedule=schedule,
        time_zone=time_zone,
        http_target=http_target,
        attempt_deadline="1800s",
    )

    return job
