import pulumi
import pulumi_gcp as gcp

from defaults import REGION, PROJECT_ID


vcmate_synapse = gcp.cloudrunv2.Service(
    "synapse-cloud-run-service",  # Unique internal name
    name="synapse",  # Service name in cloud run
    location=REGION,
    ingress="INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER",
    template={
        "containers":  [
            {
                "image": f"us.gcr.io/{PROJECT_ID}/docker/synapse:latest",
                "resources": {
                    "limits": {
                        "cpu": "1",
                        "memory": "1024Mi",
                    },
                },
            }
        ]
    },
)
