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

# Pattern for "from [tcp:|udp:]<IP>:<port>"
_FROM_IP = re.compile(
    r"from\s+(?:tcp:|udp:)?" + _IPV4 + r"[:\s]"
)
_FROM_IPV6 = re.compile(
    r"from\s+(?:tcp:|udp:)?\[?" + r"([0-9a-fA-F]*:[0-9a-fA-F:]+)" + r"\]?[:\s]"
)

# Email field: "email: <value>"
_EMAIL_RE = re.compile(r"email:\s*(\S+)")


def _extract_username(email: str) -> str:
    """Extract username from email field.

    Handles formats like:
    - "120.koko_rahman"  -> "koko_rahman"
    - "user@vmess_tcp"   -> "user"
    - "simpleuser"       -> "simpleuser"
    """
    # Strip numeric prefix like "120."
    if re.match(r"^\d+\.", email):
        email = email.split(".", 1)[1]

    # Strip protocol suffix like "@vmess_tcp"
    if "@" in email:
        email = email.split("@")[0]

    return email


def parse_log_line(line: str) -> Optional[ParsedLogEntry]:
    """Parse an Xray access log line to extract user and IP.

    Supports two formats:
    1. New: "from <IP> accepted ... email: <num>.<user>"
    2. Old: "accepted ... email: <user>@<proto> from <IP>"

    Returns None if the line doesn't match a connection event.
    """
    line_lower = line.lower()
    if "accepted" not in line_lower and "established" not in line_lower:
        return None

    # Extract email
    email_match = _EMAIL_RE.search(line)
    if not email_match:
        return None

    email = email_match.group(1)
    username = _extract_username(email)

    # Extract timestamp if present
    ts_match = re.match(r"(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})", line)
    timestamp = ts_match.group(1) if ts_match else ""

    # Strategy 1: Look for IP BEFORE the email (new Xray format)
    # "from [tcp:]<IP>:<port> accepted ..."
    before_email = line[:email_match.start()]

    from_match = _FROM_IP.search(before_email)
    if from_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=from_match.group(1),
            email=email,
            username=username,
        )

    from_match = _FROM_IPV6.search(before_email)
    if from_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=from_match.group(1),
            email=email,
            username=username,
        )

    # Strategy 2: Look for IP AFTER the email (old format)
    # "email: user@proto from <IP>:<port>"
    after_email = line[email_match.end():]

    from_match = re.search(r"(?:from|source:?)\s+" + _IPV4, after_email)
    if from_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=from_match.group(1),
            email=email,
            username=username,
        )

    from_match = re.search(r"(?:from|source:?)\s+" + _IPV6, after_email)
    if from_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=from_match.group(1),
            email=email,
            username=username,
        )

    # Fallback: any IPv4 anywhere in the line before email
    ipv4_match = re.search(_IPV4, before_email)
    if ipv4_match:
        return ParsedLogEntry(
            timestamp=timestamp,
            source_ip=ipv4_match.group(1),
            email=email,
            username=username,
        )

    return None
