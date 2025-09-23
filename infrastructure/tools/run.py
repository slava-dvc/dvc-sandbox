import git
import pulumi_gcp as gcp


def create_cloud_run_secret_env(secret_id, service_name):
    secret = gcp.secretmanager.Secret.get(
        f"{service_name}_secret_{secret_id}",
        secret_id,
    )

    secret_env = gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
        name=secret_id,
        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                secret=secret.secret_id,
                version="latest",
            ),
        ),
    )
    return secret_env


def repo_sha():
    repo = git.Repo('../')  # Initialize the repo object. Replace '.' with your repo path if needed
    head_commit = repo.head.commit
    sha = head_commit.hexsha
    return sha


def repo_short_sha():
    return repo_sha()[:7]


def _create_5xx_alert_policy(service_name: str):
    """Create monitoring alert policy for Cloud Run 5xx errors"""
    return gcp.monitoring.AlertPolicy(
        f"{service_name}-5xx-alert",
        display_name=f"5xx Errors: {service_name}",
        documentation=gcp.monitoring.AlertPolicyDocumentationArgs(
            content=f"5xx errors detected in Cloud Run service {service_name}. Check application logs and investigate user impact.",
            mime_type="text/markdown"
        ),
        conditions=[
            gcp.monitoring.AlertPolicyConditionArgs(
                display_name=f"5xx error count > 0",
                condition_threshold=gcp.monitoring.AlertPolicyConditionConditionThresholdArgs(
                    filter=f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service_name}" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"',
                    comparison="COMPARISON_GT",
                    threshold_value=0,
                    duration="60s",  # 1 minute
                    aggregations=[
                        gcp.monitoring.AlertPolicyConditionConditionThresholdAggregationArgs(
                            alignment_period="60s",
                            per_series_aligner="ALIGN_RATE",
                            cross_series_reducer="REDUCE_SUM"
                        )
                    ]
                )
            )
        ],
        combiner="OR",
        enabled=True,
        project=gcp.config.project
    )


def create_cloud_run_with_monitoring(
        service_name: str,
        image: str,
        envs: list,
        resources: gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs,
        service_account_email: str,
        args: list = None,
        allow_unauthenticated: bool = False,
        location: str = None,
        ingress: str = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
        min_instances: int = 0,
        max_instances: int = 8
):
    """Create a Cloud Run service with automatic 5xx error monitoring"""

    # Create container args
    container_args = gcp.cloudrunv2.ServiceTemplateContainerArgs(
        image=image,
        args=args,
        envs=envs,
        resources=resources
    )

    # Create the Cloud Run service
    service = gcp.cloudrunv2.Service(
        f"{service_name}-cloud-run-service",
        name=service_name,
        location=location or gcp.config.region,
        ingress=ingress,
        template=gcp.cloudrunv2.ServiceTemplateArgs(
            scaling={
                "min_instance_count": min_instances,
                "max_instance_count": max_instances,
            },
            service_account=service_account_email,
            containers=[container_args]
        )
    )

    # Create IAM member for public access if requested
    iam_member = None
    if allow_unauthenticated:
        iam_member = gcp.cloudrun.IamMember(
            f"allow-unauthenticated-{service_name}-cloud-run-service",
            service=service.name,
            location=service.location,
            role="roles/run.invoker",
            member="allUsers"
        )

    # Create 5xx error monitoring alert policy
    alert_policy = _create_5xx_alert_policy(service_name)

    return service, alert_policy, iam_member
