import pulumi_gcp as gcp

from service_account import cloud_run_service_account
from delivery import docker_repository_url
from tools.run import create_cloud_run_secret_env, repo_short_sha, create_cloud_run_with_monitoring

from .secrets import AIRTABLE_API_KEY, MONGODB_URI, OPENAI_API_KEY, SPECTR_API_KEY, SCRAPIN_API_KEY

SYNC_DEALS_PATH = "v1/integrations/sync/deal"


# Cloud Run service for Synapse with monitoring
synapse_cloud_run, synapse_5xx_alert, synapse_uptime_check, synapse_uptime_alert, _ = create_cloud_run_with_monitoring(
    service_name="synapse",
    image=f"{docker_repository_url}/synapse:{repo_short_sha()}",
    envs=[
        gcp.cloudrunv2.ServiceTemplateContainerEnvArgs(
            name="CLOUD",
            value="1",
        ),
        OPENAI_API_KEY, AIRTABLE_API_KEY, MONGODB_URI, SPECTR_API_KEY, SCRAPIN_API_KEY
    ] + [
        create_cloud_run_secret_env(secret_id, "synapce")
        for secret_id in ['SERPAPI_API_KEY']
    ],
    resources=gcp.cloudrunv2.ServiceTemplateContainerResourcesArgs(
        limits={
            "cpu": "1",
            "memory": "1024Mi",
        }
    ),
    service_account_email=cloud_run_service_account.email,
    enable_uptime_monitoring=True,  # Enable uptime monitoring for synapse (has /healthz endpoint)
    max_instances=8
)

# Data freshness monitoring
data_freshness_uptime_check = gcp.monitoring.UptimeCheckConfig(
    "synapse-data-freshness-check",
    display_name="Data Freshness: synapse",
    timeout="30s",
    period="900s",  # 15 minutes
    http_check=gcp.monitoring.UptimeCheckConfigHttpCheckArgs(
        path="/v1/company_data/freshness",
        port=443,
        use_ssl=True,
        validate_ssl=True
    ),
    monitored_resource=gcp.monitoring.UptimeCheckConfigMonitoredResourceArgs(
        type="uptime_url",
        labels={
            "host": synapse_cloud_run.uri.apply(lambda uri: uri.replace("https://", "").replace("http://", ""))
        }
    ),
    selected_regions=["usa"]
)

data_freshness_alert = gcp.monitoring.AlertPolicy(
    "synapse-data-freshness-alert",
    display_name="Data Freshness Issues: synapse",
    documentation=gcp.monitoring.AlertPolicyDocumentationArgs(
        content="Company data sources are stale or missing. Check /v1/company_data/freshness endpoint for details.",
        mime_type="text/markdown"
    ),
    conditions=[
        gcp.monitoring.AlertPolicyConditionArgs(
            display_name="Data freshness check failing",
            condition_threshold=gcp.monitoring.AlertPolicyConditionConditionThresholdArgs(
                filter=f'resource.type="uptime_url" AND metric.type="monitoring.googleapis.com/uptime_check/check_passed"',
                comparison="COMPARISON_LT",
                threshold_value=1,
                duration="900s",  # 15 minutes
                aggregations=[
                    gcp.monitoring.AlertPolicyConditionConditionThresholdAggregationArgs(
                        alignment_period="900s",
                        per_series_aligner="ALIGN_FRACTION_TRUE",
                        cross_series_reducer="REDUCE_MEAN"
                    )
                ]
            )
        )
    ],
    combiner="OR",
    enabled=True,
    project=gcp.config.project
)
