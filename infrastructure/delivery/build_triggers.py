import pulumi_gcp as gcp
from pulumi_gcp import cloudbuild
from service_account import deploy_service_account

# Define the Build Trigger
build_trigger = cloudbuild.Trigger(
    "github-synapse-deploy-trigger",
    name="synapse-repo-delivery",
    location=gcp.config.region,
    description="Triggers make -j4",
    repository_event_config={
        "push": {
            "branch": "^master$"
        },
        "repository": f"projects/{gcp.config.project}/locations/{gcp.config.region}/connections/GitHub/repositories/DVC-Agent-synapse",
    },
    filename="cloudbuild.yaml",
    service_account=deploy_service_account
)