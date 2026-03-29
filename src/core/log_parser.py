import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedLogEntry:
    timestamp: str
    source_ip: str
    email: str
    username: str


# IPv4 pattern
_IPV4 = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
# IPv6 pattern (in brackets or bare, must have at least one colon)
_IPV6 = r"\[?([0-9a-fA-F]*:[0-9a-fA-F:]+)\]?"


def parse_log_line(line: str) -> Optional[ParsedLogEntry]:
    """Parse an Xray access log line to extract user and IP.

    Returns None if the line doesn't match a connection event.
    """
    line_lower = line.lower()
    if "accepted" not in line_lower and "established" not in line_lower:
        return None

    # Extract email
    email_match = re.search(r"email:\s*(\S+)", line)
    if not email_match:
        return None

    email = email_match.group(1)
    username = email.split("@")[0] if "@" in email else email

    # Extract timestamp if present
    ts_match = re.match(r"(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})", line)
    timestamp = ts_match.group(1) if ts_match else ""

    # Look for IP after the email field — search for "from" or "source:" followed by IP
    after_email = line[email_match.end():]

    # Try "from <IP>" or "source: <IP>" patterns first
    from_match = re.search(
        r"(?:from|source:?)\s+" + _IPV4, after_email
    )
    if from_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=from_match.group(1),
            email=email,
            username=username,
        )

    from_match = re.search(
        r"(?:from|source:?)\s+" + _IPV6, after_email
    )
    if from_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=from_match.group(1),
            email=email,
            username=username,
        )

    # Fallback: any IPv4 after email
    ipv4_match = re.search(_IPV4, after_email)
    if ipv4_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=ipv4_match.group(1),
            email=email,
            username=username,
        )

    # Fallback: any IPv6 after email
    ipv6_match = re.search(_IPV6, after_email)
    if ipv6_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=ipv6_match.group(1),
            email=email,
            username=username,
        )

    return None
