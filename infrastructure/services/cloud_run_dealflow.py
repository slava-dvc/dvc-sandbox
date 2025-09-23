import pulumi
import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha, create_cloud_run_with_monitoring
from .secrets import ANTHROPIC_KEY, OPENAI_API_KEY, PERPLEXITY_KEY


# Cloud Run service with monitoring
dealflow_cloud_run, dealflow_alert_policy, _ = create_cloud_run_with_monitoring(
    service_name="dealflow",
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
    service_account_email=cloud_run_service_account.email,
    max_instances=2
)
