import time
import threading
from typing import Optional

from src.core.ipv6 import normalize_ip


class IPTracker:
    """Thread-safe in-memory IP tracker with TTL-based expiry."""

    def __init__(self, ttl_seconds: int = 300):
        self._data: dict[str, dict[str, float]] = {}
        self._lock = threading.RLock()
        self._ttl = ttl_seconds

    @property
    def ttl(self) -> int:
        return self._ttl

    def record(self, username: str, ip: str) -> None:
        """Record an IP connection for a user."""
        normalized = normalize_ip(ip)
        now = time.time()
        with self._lock:
            if username not in self._data:
                self._data[username] = {}
            self._data[username][normalized] = now

    def get_active_ips(self, username: str) -> list[str]:
        """Get list of active (non-expired) IPs for a user."""
        cutoff = time.time() - self._ttl
        with self._lock:
            user_ips = self._data.get(username, {})
            return [ip for ip, ts in user_ips.items() if ts > cutoff]

    def get_active_count(self, username: str) -> int:
        """Get count of active IPs for a user."""
        return len(self.get_active_ips(username))

    def get_all_active(self) -> dict[str, list[str]]:
        """Get all users and their active IPs."""
        cutoff = time.time() - self._ttl
        result = {}
        with self._lock:
            for username, ips in self._data.items():
                active = [ip for ip, ts in ips.items() if ts > cutoff]
                if active:
                    result[username] = active
        return result

    def get_snapshot(self) -> dict[str, dict[str, float]]:
        """Get full snapshot with timestamps for the live dashboard."""
        cutoff = time.time() - self._ttl
        result = {}
        with self._lock:
            for username, ips in self._data.items():
                active = {ip: ts for ip, ts in ips.items() if ts > cutoff}
                if active:
                    result[username] = active
        return result

    def cleanup(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        cutoff = time.time() - self._ttl
        removed = 0
        with self._lock:
            empty_users = []
            for username, ips in self._data.items():
                expired = [ip for ip, ts in ips.items() if ts <= cutoff]
                for ip in expired:
                    del ips[ip]
                    removed += 1
                if not ips:
                    empty_users.append(username)
            for username in empty_users:
                del self._data[username]
        return removed

    def clear_user(self, username: str) -> None:
        """Clear all tracked IPs for a user."""
        with self._lock:
            self._data.pop(username, None)
