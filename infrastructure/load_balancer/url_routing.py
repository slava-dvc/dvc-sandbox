import pulumi
import pulumi_gcp as gcp

from globals import DOMAIN
from .ip_addresses import external_ipv4_address, external_ipv6_address
from .ssl import ssl_certificate
from .backend_service import (
    synapse_compute_backend,
    dealflow_compute_backend,
    web_app_bucket_backend,
    portfolio_compute_backend,
    scrapers_compute_backend,
    django_compute_backend
)

default_url_redirect = gcp.compute.URLMapDefaultUrlRedirectArgs(
    strip_query=True,
    host_redirect="localhost",
    redirect_response_code="SEE_OTHER"
)

portfolio_urlmap_matcher = gcp.compute.URLMapPathMatcherArgs(
    name='portfolio-path-matcher',
    default_service=portfolio_compute_backend.self_link,
)

portfolio_host_rule = gcp.compute.URLMapHostRuleArgs(
    hosts=[f'portfolio.{DOMAIN}'], path_matcher=portfolio_urlmap_matcher.name
)

app_web_urlmap_matcher = gcp.compute.URLMapPathMatcherArgs(
    name='url-map-app-web-path-matcher',
    default_service=web_app_bucket_backend.self_link,
)

app_web_host_rule = gcp.compute.URLMapHostRuleArgs(
    hosts=[f'app.{DOMAIN}'], path_matcher=app_web_urlmap_matcher.name
)

api_urlmap_matcher = gcp.compute.URLMapPathMatcherArgs(
    name='url-map-api-path-matcher',
    default_url_redirect=gcp.compute.URLMapPathMatcherDefaultUrlRedirectArgs(
        strip_query=True,
        host_redirect="localhost",
        redirect_response_code="SEE_OTHER"
    ),
    path_rules=[
        gcp.compute.URLMapPathMatcherPathRuleArgs(
            paths=["/dealflow/*"],
            service=dealflow_compute_backend.self_link,
        ),
        gcp.compute.URLMapPathMatcherPathRuleArgs(
            paths=["/docsend2pdf/*", "/perpexity/*", "/linkedin/*"],
            service=scrapers_compute_backend.self_link,
        ),
        gcp.compute.URLMapPathMatcherPathRuleArgs(
            paths=["/v1/*"],
            service=synapse_compute_backend.self_link,
        ),
        gcp.compute.URLMapPathMatcherPathRuleArgs(
            paths=["/pitch_decks/*", "/media/*"],
            service=django_compute_backend.self_link,
        )
    ],
)

api_host_rule = gcp.compute.URLMapHostRuleArgs(
    hosts=[f'api.{DOMAIN}'], path_matcher=api_urlmap_matcher.name,
)


# Main and single traffic routing
url_map = gcp.compute.URLMap(
    "load-balancer-url-map",
    default_url_redirect=default_url_redirect,
    host_rules=[
        portfolio_host_rule,
        app_web_host_rule,
        api_host_rule
        ],
    path_matchers=[
        portfolio_urlmap_matcher,
        app_web_urlmap_matcher,
        api_urlmap_matcher
    ],
)


target_https_proxy = gcp.compute.TargetHttpsProxy(
    "global-target-https-proxy",
    url_map=url_map.id,
    ssl_certificates=[ssl_certificate.id],
)


global_forwarding_rule = gcp.compute.GlobalForwardingRule(
    "global-forwarding-rule",
    ip_protocol="TCP",
    load_balancing_scheme="EXTERNAL",
    port_range="443",  # Port for HTTPS
    target=target_https_proxy.id,  # Target HTTPS proxy
    ip_address=external_ipv4_address.address
)


global_ip6_forwarding_rule = gcp.compute.GlobalForwardingRule(
    "global-pv6-forwarding-rule",
    ip_protocol="TCP",
    load_balancing_scheme="EXTERNAL",
    port_range="443",
    target=target_https_proxy.id,
    ip_address=external_ipv6_address.address,
)
