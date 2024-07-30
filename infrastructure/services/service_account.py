import pulumi_gcp as gcp
from .defaults import PROJECT_ID

# Create or reference the service account for Cloud Run
service_account = gcp.serviceaccount.Account.get(
    id=f"projects/{PROJECT_ID}/serviceAccounts/cloud-run@vcmate.iam.gserviceaccount.com",
    resource_name="cloud-run-service-account",
    account_id="cloud-run@vcmate.iam.gserviceaccount.com",
    display_name="Cloud Run Service Account"
)