import pulumi_gcp as gcp

PROJECT_ID = gcp.config.project
REGION = gcp.config.region
DEFAULT_RETENTION_PERIOD = "604800s"  # 7 days, value must be in seconds

DEFAULT_SUBSCRIPTION_KWARGS = dict(
    project=PROJECT_ID,
    message_retention_duration=f"{DEFAULT_RETENTION_PERIOD}",
    retain_acked_messages=True,
    ack_deadline_seconds=600,  # 10 minutes
    expiration_policy={
        "ttl": "2592000s"  # 30 days, value must be in seconds
    }
)
