import pulumi_gcp as gcp

from .ip_addresses import external_ipv4_address, external_ipv6_address


# URLMap for HTTP to HTTPS redirect
redirect_url_map = gcp.compute.URLMap(
    "url-map-for-redirect",
    description="Redirect HTTP to HTTPS",
    default_url_redirect=gcp.compute.URLMapDefaultUrlRedirectArgs(
        strip_query=False,
        https_redirect=True,  # Enables HTTPS redirect
        redirect_response_code="MOVED_PERMANENTLY_DEFAULT",
    )
)


# Target HTTP Proxy for redirect
target_http_proxy = gcp.compute.TargetHttpProxy(
    "target-http-proxy-for-redirect",
    description="Redirect HTTP to HTTPS",
    url_map=redirect_url_map.id,  # This is described below.
)


global_http_forwarding_rule = gcp.compute.GlobalForwardingRule(
    "global-forwarding-rule-for-redirect",
    description="HTTP forwarding rule for HTTP to HTTPS",
    ip_protocol="TCP",
    load_balancing_scheme="EXTERNAL",
    port_range="80",  # HTTP port
    target=target_http_proxy.id,
    ip_address=external_ipv4_address.address
)

global_ipv6_forwarding_rule = gcp.compute.GlobalForwardingRule(
    "global-ipv6-forwarding-rule-for-redirect",
    description="IPv6 forwarding rule for HTTP to HTTPS",
    ip_protocol="TCP",
    load_balancing_scheme="EXTERNAL",
    port_range="80",
    target=target_http_proxy.id,
    ip_address=external_ipv6_address.address,
)