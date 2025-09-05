import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import repo_short_sha

from .secrets import MONGODB_URI

job_board_cloud_run = gcp.cloudrunv2.Service(
    "job-board-cloud-run-service",  # Unique internal name
    name="job-board",  # Service name in cloud run
    location=gcp.config.region,
    ingress="INGRESS_TRAFFIC_ALL",  # Public access
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "scaling": {
            "min_instance_count": 0,
            "max_instance_count": 2,
        },
        "service_account": cloud_run_service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"{docker_repository_url}/synapse:{repo_short_sha()}",
                args=["job-board"],
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    ),
                    MONGODB_URI  # MongoDB access for job data
                ],
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={
                        "cpu": "1",
                        "memory": "512Mi",
                    }
                ),
            )
        ]
    }),
)

allow_unauthenticated_job_board = gcp.cloudrun.IamMember(
    "allow-unauthenticated-job-board-cloud-run-service",
    service=job_board_cloud_run.name,
    location=job_board_cloud_run.location,
    role="roles/run.invoker",
    member="allUsers"
)