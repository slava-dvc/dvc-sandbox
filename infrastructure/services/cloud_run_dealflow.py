import pulumi
import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha
from .secrets import ANTHROPIC_KEY, OPENAI_API_KEY, PERPLEXITY_KEY


# Cloud Run service
dealflow = gcp.cloudrunv2.Service(
    "dealflow-cloud-run-service",  # Unique internal name
    name="dealflow",  # Service name in cloud run
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
                image=f"{docker_repository_url}/dealflow:latest",
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
