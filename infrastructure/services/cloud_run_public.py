import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha, create_cloud_run_with_monitoring

from .secrets import MONGODB_URI, OPENAI_API_KEY

# Cloud Run service for Public API with monitoring
public_cloud_run, public_alert_policy, allow_unauthenticated = create_cloud_run_with_monitoring(
    service_name="public",
    image=f"{docker_repository_url}/synapse:{repo_short_sha()}",
    args=["public"],
    envs=[
        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
            name="CLOUD",
            value="1",
        ),
        OPENAI_API_KEY, MONGODB_URI  # Only MongoDB access needed for public API
    ],
    resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
        limits={
            "cpu": "1",  # Lower resources for public API
            "memory": "512Mi",
        }
    ),
    service_account_email=cloud_run_service_account.email,
    allow_unauthenticated=True,
    ingress="INGRESS_TRAFFIC_ALL",
    max_instances=4
)