
import pulumi_gcp as gcp


def create_cloud_run_secret_env(secret_id):
    secret = gcp.secretmanager.Secret.get(
        secret_id,
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


OPENAI_API_KEY = create_cloud_run_secret_env("OPENAI_API_KEY")
ANTHROPIC_KEY = create_cloud_run_secret_env("ANTHROPIC_KEY")
PERPLEXITY_KEY = create_cloud_run_secret_env("PERPLEXITY_KEY")
AIRTABLE_API_KEY = create_cloud_run_secret_env("AIRTABLE_API_KEY")
MONGODB_URI = create_cloud_run_secret_env("MONGODB_URI")
