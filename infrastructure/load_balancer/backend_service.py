import pulumi
import pulumi_gcp as gcp

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
