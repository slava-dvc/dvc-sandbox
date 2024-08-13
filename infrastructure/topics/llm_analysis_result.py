import pulumi
import pulumi_gcp as gcp
from .defaults import PROJECT_ID, DEFAULT_RETENTION_PERIOD, DEFAULT_SUBSCRIPTION_KWARGS


__all__ = ["llm_analysis_result_topic", "llm_analysis_result_topic_name"]


# Create a Pub/Sub topic named "llm.analysis.result"
llm_analysis_result_topic_name = 'llm-analysis-result'
llm_analysis_result_topic = gcp.pubsub.Topic(
    llm_analysis_result_topic_name,
    name=llm_analysis_result_topic_name,
    project=PROJECT_ID,
)

llm_analysis_result_debug_subscription = gcp.pubsub.Subscription(
    f"{llm_analysis_result_topic_name}-subscription-debug",
    name=f"{llm_analysis_result_topic_name}-subscription-debug",
    topic=llm_analysis_result_topic_name,
    **DEFAULT_SUBSCRIPTION_KWARGS
)

pulumi.export("llm_analysis_result_topic_name", llm_analysis_result_topic_name)
