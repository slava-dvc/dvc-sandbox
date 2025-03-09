import pulumi_gcp as gcp

from .defaults import PROJECT_ID
from .service_account import service_account
from .repo import short_sha

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