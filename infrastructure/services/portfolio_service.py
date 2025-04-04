import pulumi_gcp as gcp

from .defaults import PROJECT_ID
from .service_account import service_account
from .repo import short_sha
from .gcp_secrets import create_cloud_run_secret_env, AIRTABLE_API_KEY, MONGODB_URI


portfolio = gcp.cloudrunv2.Service(
    "portfolio-cloud-run-service",  # Unique internal name
    name="portfolio",  # Service name in cloud run
    location=gcp.config.region,
    ingress="INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "scaling": {
            "min_instance_count": 0,
            "max_instance_count": 2,
        },
        "service_account": service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"us.gcr.io/{PROJECT_ID}/docker/synapse:{short_sha}",
                args=['portfolio'],
                envs=[
                    AIRTABLE_API_KEY, MONGODB_URI,
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    ),
                ] + [
                    create_cloud_run_secret_env(secret_id = secret_id)
                    for secret_id in ['COOKIE_SECRET', 'OAUTH_CLIENT_ID', 'OAUTH_SECRET']
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
