import pulumi
import pulumi_gcp as gcp


from queues import llm_analysis_result_topic, llm_analysis_result_topic_name
from tools.queue import create_subscription_with_push_and_dlq
from service_account import cloud_run_service_account
from .cloud_run_synapse import synapse_cloud_run


# Push LLM result from backend to AirTable through Synapse.
SYNC_DEALS_PATH = "v1/integrations/sync/deal"
create_subscription_with_push_and_dlq(
    llm_analysis_result_topic_name,
    "subscription-sync-deal",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{SYNC_DEALS_PATH}"),
    cloud_run_service_account
)
