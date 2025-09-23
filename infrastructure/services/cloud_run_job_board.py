import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import repo_short_sha, create_cloud_run_with_monitoring

from .secrets import MONGODB_URI

job_board_cloud_run, job_board_5xx_alert, _, _, allow_unauthenticated_job_board = create_cloud_run_with_monitoring(
    service_name="job-board",
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
    service_account_email=cloud_run_service_account.email,
    allow_unauthenticated=True,
    ingress="INGRESS_TRAFFIC_ALL",
    max_instances=2
)