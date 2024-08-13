import pulumi
import pulumi_gcp as gcp

from .defaults import REGION, PROJECT_ID
from .service_account import service_account


SYNC_DEALS_PATH = "v1/integrations/sync/deal"

# Create or reference the secret for an Airtable API key
airtable_secret_for_ingainer = gcp.secretmanager.Secret(
    "airtable-secret",
    secret_id="AIRTABLE_INGAINER",
    replication=gcp.secretmanager.SecretReplicationArgs(
        auto=gcp.secretmanager.SecretReplicationAutoArgs()
    )
)

# Cloud Run service for Synapse
vcmate_synapse = gcp.cloudrunv2.Service(
    "synapse-cloud-run-service",  # Unique internal name
    name="synapse",  # Service name in cloud run
    location=REGION,
    ingress="INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "service_account": service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"us.gcr.io/{PROJECT_ID}/synapse:latest",
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="AIRTABLE_INGAINER",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=airtable_secret_for_ingainer.secret_id,
                                version="latest",
                            ),
                        ),
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    )
                ],
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={
                        "cpu": "1",
                        "memory": "1024Mi",
                    }
                ),
            )
        ]
    }),
)


# Export the servcie name as a stack output
pulumi.export("vcmate_synapse_cloud_run_name", vcmate_synapse.name)
