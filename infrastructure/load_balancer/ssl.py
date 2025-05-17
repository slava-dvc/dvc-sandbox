import pulumi_gcp as gcp
from globals import DOMAIN


ssl_certificate = gcp.compute.ManagedSslCertificate(
    f"dvcagent-ssl-certificate",
    managed=gcp.compute.ManagedSslCertificateManagedArgs(
        domains=[
            # f"api.{DOMAIN}",
            f'portfolio.{DOMAIN}',
            # f'app.{DOMAIN}'
        ],
    ),
)