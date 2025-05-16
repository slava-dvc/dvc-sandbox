import pulumi_gcp as gcp


def make_cloud_run_backend(name: str, service: gcp.cloudrunv2.Service):
    cloud_run_neg = gcp.compute.RegionNetworkEndpointGroup(
        f"compute-neg-for-cloud-run-{name}",
        network_endpoint_type="SERVERLESS",
        region=gcp.config.region,
        cloud_run=gcp.compute.RegionNetworkEndpointGroupCloudRunArgs(
            service=service.name  # Use the extracted service name string
        )
    )

    compute_backend_service = gcp.compute.BackendService(
        f"compute-backend-service-for-cloud-run-{name}",
        protocol="HTTPS",
        port_name="http",
        timeout_sec=30,
        # health_checks=[health_check.id],  # Reference the health check
        backends=[
            gcp.compute.BackendServiceBackendArgs(
                group=cloud_run_neg.self_link,
            )],
        load_balancing_scheme="EXTERNAL_MANAGED"
    )
    return cloud_run_neg, compute_backend_service
