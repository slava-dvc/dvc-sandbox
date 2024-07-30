import pulumi
import pulumi_gcp as gcp
from .defaults import PROJECT_ID, DEFAULT_RETENTION_PERIOD, DEFAULT_SUBSCRIPTION_KWARGS


__all__ = ["llm_analysis_result_topic"]


# Create a Pub/Sub topic named "llm.analysis.result"
llm_analysis_result_topic_name = 'llm-analysis-result'
llm_analysis_result_topic = gcp.pubsub.Topic(
    llm_analysis_result_topic_name,
    name=llm_analysis_result_topic_name,
    project=PROJECT_ID,
    message_retention_duration=f"{DEFAULT_RETENTION_PERIOD}s"  # 7 days retention
)

llm_analysis_result_debug_subscription = gcp.pubsub.Subscription(
    f"{llm_analysis_result_topic_name}-subscription-debug",
    name=f"{llm_analysis_result_topic_name}-subscription-debug",
    topic=llm_analysis_result_topic.name,
    **DEFAULT_SUBSCRIPTION_KWARGS
)

# Export the names as a stack output
pulumi.export("llm_analysis_result_topic_name", llm_analysis_result_topic.name)
pulumi.export("llm_analysis_result_debug_subscription_name", llm_analysis_result_debug_subscription.name)
