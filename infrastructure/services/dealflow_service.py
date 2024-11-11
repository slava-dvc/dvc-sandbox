import pulumi
import pulumi_gcp as gcp

from .defaults import REGION, PROJECT_ID
from .service_account import service_account

from .gcp_secrets import ANTHROPIC_KEY, OPENAI_API_KEY, PERPLEXITY_KEY


# Cloud Run service
dealflow = gcp.cloudrunv2.Service(
    "dealflow-cloud-run-service",  # Unique internal name
    name="dealflow",  # Service name in cloud run
    location=REGION,
    ingress="INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "service_account": service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"us.gcr.io/{PROJECT_ID}/docker/dealflow:latest",
                envs=[
                    ANTHROPIC_KEY, OPENAI_API_KEY, PERPLEXITY_KEY,
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="RECORDING_BUCKET",
                        value="dvc-rivet-records",
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
