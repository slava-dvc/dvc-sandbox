import pulumi
import pulumi_gcp as gcp
from globals import DOMAIN
from services import synapse_cloud_run, dealflow_cloud_run, portfolio_cloud_run, scrapers_cloud_run
from tools.load_balancer import make_cloud_run_backend


synapse_cloud_run_neg, synapse_compute_backend = make_cloud_run_backend(
    "synapse",
    synapse_cloud_run
)


dealflow_cloud_run_neg, dealflow_compute_backend = make_cloud_run_backend(
    "dealflow",
    dealflow_cloud_run
)


portfolio_cloud_run_neg, portfolio_compute_backend = make_cloud_run_backend(
    "portfolio",
    portfolio_cloud_run
)


scrapers_cloud_run_neg, scrapers_compute_backend = make_cloud_run_backend(
    "scrapers",
    scrapers_cloud_run
)


web_app_bucket_backend = gcp.compute.BackendBucket(
    "compute-backend-service-for-web-app-bucket",
    description="Backend bucket for static website content",
    bucket_name="dvc-web-app",
    enable_cdn=False,
)


django_instance_neg = gcp.compute.GlobalNetworkEndpointGroup(
    "compute-neg-for-django-instance",
    network_endpoint_type="INTERNET_FQDN_PORT",
    default_port=443
)

django_instance_endpoint = gcp.compute.GlobalNetworkEndpoint(
    "compute-ne-for-django-instance",
    global_network_endpoint_group=django_instance_neg.id,
    fqdn=f"backend.{DOMAIN}",
    port=django_instance_neg.default_port
)

django_compute_backend = gcp.compute.BackendService(
    "compute-backend-service-for-django-instance",
    timeout_sec=10,
    protocol="HTTPS",
    connection_draining_timeout_sec=10,
    load_balancing_scheme="EXTERNAL_MANAGED",
    custom_request_headers=[django_instance_endpoint.fqdn.apply(lambda fqdn: f"host: {fqdn}")],
    backends=[
        gcp.compute.BackendServiceBackendArgs(
            group=django_instance_neg.self_link,
        )
    ],
)
