import pulumi
import pulumi_gcp as gcp

# Static IP for load balancer
external_ipv4_address = gcp.compute.GlobalAddress(
    "external-ipv4-address",
    address_type="EXTERNAL",
    description="Public IP address for the load balancer"
)

external_ipv6_address = gcp.compute.GlobalAddress(
    "external-ipv6-address",
    ip_version="IPV6",
    description="Public IPv6 address for the load balancer"
)


# Optionally, export the IP address as a stack output
pulumi.export(f"IPv4 Address", external_ipv4_address.address)
pulumi.export(f"IPv6 Address", external_ipv6_address.address)