import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha, create_cloud_run_with_monitoring

from .secrets import AIRTABLE_API_KEY, MONGODB_URI


portfolio_cloud_run, portfolio_5xx_alert, _, _, _ = create_cloud_run_with_monitoring(
    service_name="portfolio",
    image=f"{docker_repository_url}/synapse:{repo_short_sha()}",
    args=['portfolio'],
    envs=[
        AIRTABLE_API_KEY, MONGODB_URI,
        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
            name="CLOUD",
            value="1",
        ),
    ] + [
        create_cloud_run_secret_env(secret_id, "portfolio")
        for secret_id in ['COOKIE_SECRET', 'OAUTH_CLIENT_ID', 'OAUTH_SECRET']
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
