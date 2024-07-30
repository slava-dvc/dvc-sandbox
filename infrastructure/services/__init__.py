import pulumi_gcp as gcp
from .synapse_service import vcmate_synapse


__all__ = ['vcmate_synapse']


allow_unauthenticated = gcp.cloudrun.IamMember(
    "allow-unauthenticated",
    service=vcmate_synapse.name,
    location=vcmate_synapse.location,
    role="roles/run.invoker",
    member="allUsers"
)
