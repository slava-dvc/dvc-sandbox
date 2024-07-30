import pulumi
import pulumi_gcp as gcp

from .defaults import REGION, PROJECT_ID
from .service_account import service_account
from topics import llm_analysis_result_topic, DEFAULT_SUBSCRIPTION_KWARGS


SYNC_DEALS_PATH = "v1/integrations/sync/deal"

# Create or reference the secret for an Airtable API key
airtable_secret_for_ingainer = gcp.secretmanager.Secret(
    "airtable-secret",
    secret_id="AIRTABLE_INGAINER",
    replication=gcp.secretmanager.SecretReplicationArgs(
        auto=gcp.secretmanager.SecretReplicationAutoArgs()
    )
)

# Cloud Run service for Synapse
vcmate_synapse = gcp.cloudrunv2.Service(
    "synapse-cloud-run-service",  # Unique internal name
    name="synapse",  # Service name in cloud run
    location=REGION,
    ingress="INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
    template=gcp.cloudrunv2.ServiceTemplateArgs(**{
        "service_account": service_account.email,
        "containers": [
            gcp.cloudrunv2.ServiceTemplateContainerArgs(
                image=f"us.gcr.io/{PROJECT_ID}/synapse:latest",
                envs=[
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="AIRTABLE_INGAINER",
                        value_source=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceArgs(
                            secret_key_ref=gcp.cloudrunv2.ServiceTemplateContainerEnvValueSourceSecretKeyRefArgs(
                                secret=airtable_secret_for_ingainer.secret_id,
                                version="latest",
                            ),
                        ),
                    ),
                    gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
                        name="CLOUD",
                        value="1",
                    )
                ],
                resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
                    limits={
                        "cpu": "1",
                        "memory": "1024Mi",
                    }
                ),
            )
        ]
    }),
)

# Create a Pub/Sub subscription that pushes llm analysis result to synapse
llm_analysis_result_subscription = gcp.pubsub.Subscription(
    "llm-analysis-result-subscription-sync-deal",
    name="llm-analysis-result-subscription-sync-deal",
    topic=llm_analysis_result_topic.name,
    push_config=gcp.pubsub.SubscriptionPushConfigArgs(
        push_endpoint=vcmate_synapse.uri.apply(lambda uri: f"{uri}/{SYNC_DEALS_PATH}"),
        oidc_token=gcp.pubsub.SubscriptionPushConfigOidcTokenArgs(
            service_account_email=service_account.email,
        ),
        no_wrapper=gcp.pubsub.SubscriptionPushConfigNoWrapperArgs(
            write_metadata=True
        )
    ),
    retry_policy=gcp.pubsub.SubscriptionRetryPolicyArgs(
        minimum_backoff="10s",
        maximum_backoff="600s",  # 10 minutes
    ),
    **DEFAULT_SUBSCRIPTION_KWARGS
)


# Export the servcie name as a stack output
pulumi.export("vcmate_synapse_cloud_run_name", vcmate_synapse.name)
