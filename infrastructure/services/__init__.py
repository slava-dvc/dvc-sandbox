import pulumi_gcp as gcp
from .synapse_service import synapse
from .dealflow_service import dealflow
from .sync_deal_subscription import *

__all__ = ['synapse']


allow_unauthenticated = gcp.cloudrun.IamMember(
    "allow-unauthenticated",
    service=synapse.name,
    location=synapse.location,
    role="roles/run.invoker",
    member="allUsers"
)
