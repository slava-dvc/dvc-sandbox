import pulumi
import pulumi_gcp as gcp

from globals import API_BASE_URL

from queues import llm_analysis_result, company_data
from tools.queue import create_subscription_with_push_and_dlq
from tools.scheduler import make_scheduled_job
from service_account import cloud_run_service_account, scheduler_service_account
from .cloud_run_synapse import synapse_cloud_run


# Push LLM result from backend to AirTable through Synapse.
SYNC_DEALS_PATH = "v1/integrations/sync/deal"
create_subscription_with_push_and_dlq(
    llm_analysis_result.llm_analysis_result_topic_name,
    "consume",
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

COMPANY_DATA_PULL = "v1/company_data/pull"
company_data_pull_linkedin = make_scheduled_job(
    "company-data-pull-linkedin",
    "Pull Company Data (LinkedIn)",
    "12 11 * * 7",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL}"),
    cloud_run_service_account,
    {
        "sources": ["linkedin"],
        "max_items": 50000
    }
)

company_data_pull_googleplay = make_scheduled_job(
    "company-data-pull-googleplay",
    "Pull Company Data (Google Play)",
    "45 14 * * 7",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL}"),
    cloud_run_service_account,
    {
        "sources": ["googleplay"],
        "max_items": 50000
    }
)

company_data_pull_appstore = make_scheduled_job(
    "company-data-pull-appstore",
    "Pull Company Data (Apple App Store)",
    "15 16 * * 7",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL}"),
    cloud_run_service_account,
    {
        "sources": ["appstore"],
        "max_items": 50000
    }
)

company_data_pull_google_jobs = make_scheduled_job(
    "company-data-pull-google-jobs",
    "Pull Company Data (Google Jobs)",
    "30 15 * * 7",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL}"),
    cloud_run_service_account,
    {
        "sources": ["google_jobs"],
        "max_items": 50000
    }
)

COMPANY_DATA_PULL_LINKEDIN = "v1/company_data/pull/linkedin"
create_subscription_with_push_and_dlq(
    company_data.linkedin_topic_name,
    "consume",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL_LINKEDIN}"),
    cloud_run_service_account
)

COMPANY_DATA_PULL_GOOGLEPLAY = "v1/company_data/pull/googleplay"
create_subscription_with_push_and_dlq(
    company_data.googleplay_topic_name,
    "consume",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL_GOOGLEPLAY}"),
    cloud_run_service_account
)

COMPANY_DATA_PULL_APPSTORE = "v1/company_data/pull/appstore"
create_subscription_with_push_and_dlq(
    company_data.appstore_topic_name,
    "consume",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL_APPSTORE}"),
    cloud_run_service_account
)

COMPANY_DATA_PULL_GOOGLE_JOBS = "v1/company_data/pull/google_jobs"
create_subscription_with_push_and_dlq(
    company_data.google_jobs_topic_name,
    "consume",
    synapse_cloud_run.uri.apply(lambda uri: f"{uri}/{COMPANY_DATA_PULL_GOOGLE_JOBS}"),
    cloud_run_service_account
)

