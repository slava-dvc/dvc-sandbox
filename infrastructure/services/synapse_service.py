import pulumi
import pulumi_gcp as gcp

from .defaults import REGION, PROJECT_ID
from .service_account import service_account
from .gcp_secrets import OPENAI_API_KEY, AIRTABLE_API_KEY, MONGODB_URI, SPECTR_API_KEY
from .gcp_secrets import create_cloud_run_secret_env
from .repo import short_sha

SYNC_DEALS_PATH = "v1/integrations/sync/deal"


# Cloud Run service for Synapse
synapse = gcp.cloudrunv2.Service(
    "synapse-cloud-run-service",  # Unique internal name
    name="synapse",  # Service name in cloud run
    location=REGION,
    ingress="INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "service_account": service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"us.gcr.io/{PROJECT_ID}/docker/synapse:{short_sha}",
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    ),
                    OPENAI_API_KEY, AIRTABLE_API_KEY, MONGODB_URI, SPECTR_API_KEY,
                ],
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={
                        "cpu": "1000m",
                        "memory": "1Gi",
                    }
                ),
            )
        ]
    }),
)
