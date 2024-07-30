import pulumi_gcp as gcp

PROJECT_ID = gcp.config.project or "vcmate"
REGION = gcp.config.region or "us-central1"
DEFAULT_RETENTION_PERIOD = 604800  # 7 days

DEFAULT_SUBSCRIPTION_KWARGS = dict(
    project=PROJECT_ID,
    message_retention_duration=f"{DEFAULT_RETENTION_PERIOD}s",  # 1 hour retention
    retain_acked_messages=True,
    ack_deadline_seconds=600,  # 10 minutes
    expiration_policy={
        "ttl": "2592000s"  # 30 days
    }
)
