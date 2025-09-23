import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, create_cloud_run_with_monitoring


scrapers_cloud_run, scrapers_alert_policy, allow_unauthenticated = create_cloud_run_with_monitoring(
    service_name="scrapers-v2",
    image=f"{docker_repository_url}/scrapers:latest",
    envs=[
        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
            name="CLOUD",
            value="1",
        ),
    ] + [
        create_cloud_run_secret_env(secret_id, "scrapers")
        for secret_id in ['PERPLEXITY_API_KEY', 'SCRAPIN_API_KEY', 'SERP_API_KEY', 'MAILSLURP_API_KEY']
    ],
    resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
        limits={
            "cpu": "2",
            "memory": "4096Mi",
        }
    ),
    service_account_email=cloud_run_service_account.email,
    allow_unauthenticated=True,
    max_instances=2
)