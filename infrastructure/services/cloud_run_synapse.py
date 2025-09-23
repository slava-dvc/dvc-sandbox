import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha, create_cloud_run_with_monitoring

from .secrets import AIRTABLE_API_KEY, MONGODB_URI, OPENAI_API_KEY, SPECTR_API_KEY, SCRAPIN_API_KEY

SYNC_DEALS_PATH = "v1/integrations/sync/deal"


# Cloud Run service for Synapse with monitoring
synapse_cloud_run, synapse_5xx_alert, synapse_uptime_check, synapse_uptime_alert, _ = create_cloud_run_with_monitoring(
    service_name="synapse",
    image=f"{docker_repository_url}/synapse:{repo_short_sha()}",
    envs=[
        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
            name="CLOUD",
            value="1",
        ),
        OPENAI_API_KEY, AIRTABLE_API_KEY, MONGODB_URI, SPECTR_API_KEY, SCRAPIN_API_KEY
    ] + [
        create_cloud_run_secret_env(secret_id, "synapce")
        for secret_id in ['SERPAPI_API_KEY']
    ],
    resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
        limits={
            "cpu": "1",
            "memory": "1024Mi",
        }
    ),
    service_account_email=cloud_run_service_account.email,
    enable_uptime_monitoring=True,  # Enable uptime monitoring for synapse (has /healthz endpoint)
    max_instances=8
)
