import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha

from .secrets import MONGODB_URI

# Cloud Run service for Public API
public_cloud_run = gcp.cloudrunv2.Service(
    "public-cloud-run-service",  # Unique internal name
    name="public",  # Service name in cloud run
    location=gcp.config.region,
    ingress="INGRESS_TRAFFIC_ALL",  # Public access
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "scaling": {
            "min_instance_count": 0,
            "max_instance_count": 4,
        },
        "service_account": cloud_run_service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"{docker_repository_url}/synapse:{repo_short_sha()}",
                args=["public"],
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    ),
                    MONGODB_URI  # Only MongoDB access needed for public API
                ],
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={
                        "cpu": "1",  # Lower resources for public API
                        "memory": "512Mi",
                    }
                ),
            )
        ]
    }),
)

allow_unauthenticated = gcp.cloudrun.IamMember(
    "allow-unauthenticated-public-cloud-run-service",
    service=public_cloud_run.name,
    location=public_cloud_run.location,
    role="roles/run.invoker",
    member="allUsers"
)