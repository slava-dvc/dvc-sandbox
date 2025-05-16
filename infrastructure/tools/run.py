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
