import pulumi_gcp as gcp
from .cloud_run_synapse import synapse
from .cloud_run_dealflow import dealflow
from .cloud_run_portfolio import portfolio
from .integrations import *

__all__ = ['synapse']


allow_unauthenticated = gcp.cloudrun.IamMember(
    "allow-unauthenticated",
    service=synapse.name,
    location=synapse.location,
    role="roles/run.invoker",
    member="allUsers"
)
