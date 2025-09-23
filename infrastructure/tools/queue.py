is_pulumi = False

try:
    import pulumi
    import pulumi_gcp as gcp
    is_pulumi = pulumi.runtime.is_dry_run() is not None  # Returns bool during pulumi run
except ImportError:
    pass


def make_topic(topic_name):
    if not is_pulumi:
        return None, None
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
    if not is_pulumi:
        return None, None, None, None
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

    # Create DLQ monitoring alert policy
    alert_policy = gcp.monitoring.AlertPolicy(
        f"{dlq_topic_name}-alert",
        display_name=f"DLQ Messages: {topic_name}-{subscription_name}",
        documentation=gcp.monitoring.AlertPolicyDocumentationArgs(
            content=f"Messages are accumulating in DLQ for {topic_name}-{subscription_name}. Check integration health and debug subscription for failed messages.",
            mime_type="text/markdown"
        ),
        conditions=[
            gcp.monitoring.AlertPolicyConditionArgs(
                display_name=f"DLQ message count > 0",
                condition_threshold=gcp.monitoring.AlertPolicyConditionConditionThresholdArgs(
                    filter=f'resource.type="pubsub_subscription" AND resource.labels.subscription_id="{dlq_topic_name}-debug" AND metric.type="pubsub.googleapis.com/subscription/num_undelivered_messages"',
                    comparison="COMPARISON_GT",
                    threshold_value=0,
                    duration="300s",  # 5 minutes
                    aggregations=[
                        gcp.monitoring.AlertPolicyConditionConditionThresholdAggregationArgs(
                            alignment_period="300s",
                            per_series_aligner="ALIGN_MAX",
                            cross_series_reducer="REDUCE_SUM"
                        )
                    ]
                )
            )
        ],
        combiner="OR",
        enabled=True,
        project=gcp.config.project
    )

    return dlq_topic, dlq_topic_debug_subscription, subscription, alert_policy


DEFAULT_SUBSCRIPTION_KWARGS = dict(
    project=gcp.config.project,
    message_retention_duration="604800s", # 7 days, value must be in seconds
    retain_acked_messages=True,
    ack_deadline_seconds=600,  # 10 minutes
    expiration_policy={
        "ttl": ""  # Empty means never
    }
)
