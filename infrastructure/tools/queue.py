import pulumi_gcp as gcp


def make_topic(topic_name):
    topic = gcp.pubsub.Topic(
        f'{topic_name}',
        name=topic_name,
        project=gcp.config.project,
    )

    debug_subscription = gcp.pubsub.Subscription(
        f"{topic_name}-debug",
        name=f"{topic_name}-debug",
        topic=topic.name,
        **DEFAULT_SUBSCRIPTION_KWARGS
    )
    return topic, debug_subscription


def create_subscription_with_push_and_dlq(
        topic_name: str,
        subscription_name: str,
        http_endpoint: str,
        service_account: gcp.serviceaccount.Account
):
    # Create a Dead Letter Queue (DLQ) topic for the subscription
    dlq_topic_name = f"{topic_name}-{subscription_name}-dlq"
    dlq_topic = gcp.pubsub.Topic(
        dlq_topic_name,
        name=dlq_topic_name,
        project=gcp.config.project,
    )

    # Create a debug pull subscription for failed messages in the DLQ topic
    dlq_topic_debug_subscription = gcp.pubsub.Subscription(
        f"{dlq_topic_name}-debug",
        name=f"{dlq_topic_name}-debug",
        topic=dlq_topic.name,
        **DEFAULT_SUBSCRIPTION_KWARGS
    )

    # Create the subscription to push to the provided HTTP endpoint with a DLQ
    subscription = gcp.pubsub.Subscription(
        f"{topic_name}-{subscription_name}",
        name=f"{topic_name}-{subscription_name}",
        topic=topic_name,
        push_config=gcp.pubsub.SubscriptionPushConfigArgs(
            push_endpoint=http_endpoint,
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
        dead_letter_policy=gcp.pubsub.SubscriptionDeadLetterPolicyArgs(
            max_delivery_attempts=5,
            dead_letter_topic=f"projects/{gcp.config.project}/topics/{dlq_topic_name}"
        ),
        **DEFAULT_SUBSCRIPTION_KWARGS
    )

    return dlq_topic, dlq_topic_debug_subscription, subscription


DEFAULT_SUBSCRIPTION_KWARGS = dict(
    project=gcp.config.project,
    message_retention_duration="604800s", # 7 days, value must be in seconds
    retain_acked_messages=True,
    ack_deadline_seconds=600,  # 10 minutes
    expiration_policy={
        "ttl": ""  # Empty means never
    }
)
