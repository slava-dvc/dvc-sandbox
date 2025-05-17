import pulumi
import pulumi_gcp as gcp

DOCKER_REGISTRY_LOCATION = "us"
DOCKER_REGISTRY_NAME = "docker"

# Create a Docker Artifact Registry repository
docker_repository = gcp.artifactregistry.Repository(
    "synapse-docker-repo",
    description="Docker repository for Synapse services",
    format="DOCKER",
    location=DOCKER_REGISTRY_LOCATION,
    repository_id=DOCKER_REGISTRY_NAME
)

# us-docker.pkg.dev/dvc-agent/docker
docker_repository_url = f"{DOCKER_REGISTRY_LOCATION}-docker.pkg.dev/{gcp.config.project}/{DOCKER_REGISTRY_NAME}"
