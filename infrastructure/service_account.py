import pulumi_gcp as gcp


def get_service_account(account_id, domain=None):
    domain = domain or f"{gcp.config.project}.iam.gserviceaccount.com"
    return gcp.serviceaccount.Account.get(
        id=f"projects/{gcp.config.project}/serviceAccounts/{account_id}@{domain}",
        resource_name=f"{account_id}-service-account",
        account_id=f"{account_id}@{domain}",
    )


cloud_run_service_account = get_service_account("cloud-run")
deploy_service_account = get_service_account("deploy")
scheduler_service_account = get_service_account("scheduler")
