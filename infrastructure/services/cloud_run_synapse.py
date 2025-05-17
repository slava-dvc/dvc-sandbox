import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha

from .secrets import AIRTABLE_API_KEY, MONGODB_URI, OPENAI_API_KEY, SPECTR_API_KEY

SYNC_DEALS_PATH = "v1/integrations/sync/deal"


# Cloud Run service for Synapse
synapse_cloud_run = gcp.cloudrunv2.Service(
    "synapse-cloud-run-service",  # Unique internal name
    name="synapse",  # Service name in cloud run
    location=gcp.config.region,
    ingress="INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "scaling": {
            "min_instance_count": 0,
            "max_instance_count": 2,
        },
        "service_account": cloud_run_service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"{docker_repository_url}/synapse:{repo_short_sha()}",
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    ),
                    OPENAI_API_KEY, AIRTABLE_API_KEY, MONGODB_URI, SPECTR_API_KEY,
                ],
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={
                        "cpu": "1",
                        "memory": "512Mi",
                    }
                ),
            )
        ]
    }),
)
