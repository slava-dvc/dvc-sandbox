import pulumi
import pulumi_gcp as gcp

from topics import llm_analysis_result_topic, llm_analysis_result_topic_name, DEFAULT_SUBSCRIPTION_KWARGS
from service_account import cloud_run_service_account
from .cloud_run_synapse import synapse

SYNC_DEALS_PATH = "v1/integrations/sync/deal"


# Deal letter queue for the push endpoint
llm_analysis_result_subscription_dlq_topic_name = f"{llm_analysis_result_topic_name}-dlq-sync-deal"
llm_analysis_result_subscription_dlq_topic = gcp.pubsub.Topic(
    llm_analysis_result_subscription_dlq_topic_name,
    name=llm_analysis_result_subscription_dlq_topic_name,
    project=gcp.config.project,
)


# Debug pull subscription to analyze failed messages in the DLQ
llm_analysis_result_subscription_dlq_subscription = gcp.pubsub.Subscription(
    f"{llm_analysis_result_subscription_dlq_topic_name}-subscription-debug",
    name=f"{llm_analysis_result_subscription_dlq_topic_name}-subscription-debug",
    topic=llm_analysis_result_subscription_dlq_topic.name,
    ** DEFAULT_SUBSCRIPTION_KWARGS
)


# Subscription to push llm analysis results to synapse
llm_analysis_result_subscription = gcp.pubsub.Subscription(
    f"{llm_analysis_result_topic_name}-subscription-sync-deal",
    name=f"{llm_analysis_result_topic_name}-subscription-sync-deal",
    topic=llm_analysis_result_topic.name,
    push_config=gcp.pubsub.SubscriptionPushConfigArgs(
        push_endpoint=synapse.uri.apply(lambda uri: f"{uri}/{SYNC_DEALS_PATH}"),
        oidc_token=gcp.pubsub.SubscriptionPushConfigOidcTokenArgs(
            service_account_email=cloud_run_service_account.email,
        ),
        no_wrapper=gcp.pubsub.SubscriptionPushConfigNoWrapperArgs(
            write_metadata=True
        )
    ),
    retry_policy=gcp.pubsub.SubscriptionRetryPolicyArgs(
        minimum_backoff="10s",
        maximum_backoff="600s",  # 10 minutes
    ),
    dead_letter_policy=gcp.pubsub.SubscriptionDeadLetterPolicyArgs(
        max_delivery_attempts=5,
        dead_letter_topic=f"projects/{gcp.config.project}/topics/{llm_analysis_result_subscription_dlq_topic_name}"
    ),
    **DEFAULT_SUBSCRIPTION_KWARGS
)
