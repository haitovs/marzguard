import pytest

from src.core.tracker import IPTracker
from src.models.user import UserIPConfig
from src.models.policy import Policy


class TestLimitResolution:
    """Test the 3-tier cascade: user > policy > global."""

    def test_user_override(self):
        config = UserIPConfig(username="test", ip_limit=5)
        assert config.get_effective_limit(global_default=2) == 5

    def test_policy_fallback(self):
        policy = Policy(name="test_policy", default_ip_limit=3)
        config = UserIPConfig(username="test", ip_limit=None)
        config.policy = policy
        assert config.get_effective_limit(global_default=2) == 3

    def test_global_fallback(self):
        config = UserIPConfig(username="test", ip_limit=None)
        assert config.get_effective_limit(global_default=2) == 2

    def test_user_overrides_policy(self):
        policy = Policy(name="test_policy", default_ip_limit=3)
        config = UserIPConfig(username="test", ip_limit=10)
        config.policy = policy
        assert config.get_effective_limit(global_default=2) == 10

    def test_policy_overrides_global(self):
        policy = Policy(name="test_policy", default_ip_limit=7)
        config = UserIPConfig(username="test", ip_limit=None)
        config.policy = policy
        assert config.get_effective_limit(global_default=2) == 7

    def test_exempt_user_skipped(self):
        config = UserIPConfig(username="test", is_exempt=True)
        assert config.is_exempt is True

    def test_unmonitored_user_skipped(self):
        config = UserIPConfig(username="test", is_monitored=False)
        assert config.is_monitored is False


class TestTrackerEnforcementIntegration:
    """Test tracker + limit resolution together."""

    def test_user_over_limit(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "1.1.1.1")
        tracker.record("user1", "2.2.2.2")
        tracker.record("user1", "3.3.3.3")

        config = UserIPConfig(username="user1", ip_limit=2)
        active = tracker.get_active_count("user1")
        limit = config.get_effective_limit(global_default=5)
        assert active > limit

    def test_user_within_limit(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "1.1.1.1")
        tracker.record("user1", "2.2.2.2")

        config = UserIPConfig(username="user1", ip_limit=3)
        active = tracker.get_active_count("user1")
        limit = config.get_effective_limit(global_default=5)
        assert active <= limit
