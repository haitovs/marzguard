import ipaddress


def normalize_ip(ip: str) -> str:
    """Normalize an IP address. IPv6 addresses are collapsed to /64 prefix."""
    try:
        addr = ipaddress.ip_address(ip)
        if isinstance(addr, ipaddress.IPv6Address):
            network = ipaddress.IPv6Network(f"{addr}/64", strict=False)
            return str(network.network_address)
        return str(addr)
    except ValueError:
        return ip
