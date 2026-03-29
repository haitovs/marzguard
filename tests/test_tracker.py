import time
import threading

import pytest

from src.core.tracker import IPTracker


class TestIPTracker:
    def test_record_and_get(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "1.2.3.4")
        tracker.record("user1", "5.6.7.8")
        assert sorted(tracker.get_active_ips("user1")) == ["1.2.3.4", "5.6.7.8"]

    def test_ttl_expiry(self):
        tracker = IPTracker(ttl_seconds=1)
        tracker.record("user1", "1.2.3.4")
        assert tracker.get_active_count("user1") == 1
        time.sleep(1.1)
        assert tracker.get_active_count("user1") == 0

    def test_cleanup(self):
        tracker = IPTracker(ttl_seconds=1)
        tracker.record("user1", "1.2.3.4")
        tracker.record("user2", "5.6.7.8")
        time.sleep(1.1)
        removed = tracker.cleanup()
        assert removed == 2
        assert tracker.get_all_active() == {}

    def test_ipv6_normalization(self):
        tracker = IPTracker(ttl_seconds=300)
        # Two IPs in the same /64 should be counted as one
        tracker.record("user1", "2001:db8:85a3::8a2e:370:7334")
        tracker.record("user1", "2001:db8:85a3::1")
        assert tracker.get_active_count("user1") == 1

    def test_ipv6_different_subnets(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "2001:db8:85a3::1")
        tracker.record("user1", "2001:db8:85a4::1")
        assert tracker.get_active_count("user1") == 2

    def test_get_all_active(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "1.2.3.4")
        tracker.record("user2", "5.6.7.8")
        tracker.record("user2", "9.10.11.12")
        all_active = tracker.get_all_active()
        assert len(all_active) == 2
        assert len(all_active["user2"]) == 2

    def test_clear_user(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "1.2.3.4")
        tracker.clear_user("user1")
        assert tracker.get_active_count("user1") == 0

    def test_thread_safety(self):
        tracker = IPTracker(ttl_seconds=300)
        errors = []

        def writer(user_id):
            try:
                for i in range(100):
                    tracker.record(f"user{user_id}", f"10.0.{user_id}.{i % 256}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        all_active = tracker.get_all_active()
        assert len(all_active) == 10

    def test_get_snapshot(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "1.2.3.4")
        snapshot = tracker.get_snapshot()
        assert "user1" in snapshot
        assert "1.2.3.4" in snapshot["user1"]
        assert isinstance(snapshot["user1"]["1.2.3.4"], float)

    def test_duplicate_ip_updates_timestamp(self):
        tracker = IPTracker(ttl_seconds=300)
        tracker.record("user1", "1.2.3.4")
        snap1 = tracker.get_snapshot()
        ts1 = snap1["user1"]["1.2.3.4"]

        time.sleep(0.05)
        tracker.record("user1", "1.2.3.4")
        snap2 = tracker.get_snapshot()
        ts2 = snap2["user1"]["1.2.3.4"]

        assert ts2 > ts1
        assert tracker.get_active_count("user1") == 1
