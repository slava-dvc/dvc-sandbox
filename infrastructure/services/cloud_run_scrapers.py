import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env


scrapers_cloud_run = gcp.cloudrunv2.Service(
    "scrapers-cloud-run-service",  # Unique internal name
    name="scrapers-v2",  # Service name in cloud run
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
            )
        ]
    }),
)
