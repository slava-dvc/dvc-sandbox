import pulumi_gcp as gcp

PROJECT_ID = gcp.config.project or "vcmate"
REGION = gcp.config.region or "us-central1"
