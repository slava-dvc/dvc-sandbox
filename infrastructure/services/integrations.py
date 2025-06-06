import pulumi
import pulumi_gcp as gcp

from globals import API_BASE_URL

from queues import llm_analysis_result_topic, llm_analysis_result_topic_name
from tools.queue import create_subscription_with_push_and_dlq
from tools.scheduler import make_scheduled_job
from service_account import cloud_run_service_account, scheduler_service_account
from .cloud_run_synapse import synapse_cloud_run


# Push LLM result from backend to AirTable through Synapse.
SYNC_DEALS_PATH = "v1/integrations/sync/deal"
create_subscription_with_push_and_dlq(
    llm_analysis_result_topic_name,
    "subscription-sync-deal",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{SYNC_DEALS_PATH}"),
    cloud_run_service_account
)

PULL_COMPANIES_PATH = "v1/integrations/airtable/pull_companies"
pull_companies_from_airtable = make_scheduled_job(
    "airtable-pull-companies",
    "Pull Companies from AirTable",
    "5 10 * * 7",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{PULL_COMPANIES_PATH}"),
    scheduler_service_account
)

SYNC_COMPANIES_PATH = "v1/integrations/spectr/sync_companies"
sync_companies_from_spectr = make_scheduled_job(
    "spectr-pull-companies",
    "Pull Companies from Spectr",
    "13 17 5 * *",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{SYNC_COMPANIES_PATH}"),
    cloud_run_service_account
)