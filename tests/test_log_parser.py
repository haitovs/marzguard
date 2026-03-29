import pytest

from src.core.log_parser import parse_log_line


class TestLogParser:
    def test_standard_accepted_line(self):
        line = (
            "2024/01/15 10:30:45 [Info] [accepted] "
            "email: testuser@vmess_tcp from 1.2.3.4:54321"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "testuser"
        assert entry.source_ip == "1.2.3.4"
        assert entry.email == "testuser@vmess_tcp"

    def test_accepted_with_source_keyword(self):
        line = (
            "2024/01/15 10:30:45 [Info] [accepted] "
            "email: user2@vless_tcp source: 10.0.0.1:12345"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "user2"
        assert entry.source_ip == "10.0.0.1"

    def test_ipv6_address(self):
        line = (
            "2024/01/15 10:30:45 [Info] [accepted] "
            "email: user3@trojan from [2001:db8::1]:54321"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "user3"
        assert entry.source_ip == "2001:db8::1"

    def test_non_connection_line_returns_none(self):
        line = "2024/01/15 10:30:45 [Warning] some other log message"
        assert parse_log_line(line) is None

    def test_empty_line_returns_none(self):
        assert parse_log_line("") is None

    def test_error_log_returns_none(self):
        line = "2024/01/15 10:30:45 [Error] failed to connect"
        assert parse_log_line(line) is None

    def test_email_without_at_sign(self):
        line = (
            "2024/01/15 10:30:45 [Info] [accepted] "
            "email: simpleuser from 192.168.1.1:9999"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "simpleuser"

    def test_established_keyword(self):
        line = (
            "2024/01/15 10:30:45 [Info] [established] "
            "email: estuser@ss from 172.16.0.1:8888"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "estuser"
        assert entry.source_ip == "172.16.0.1"
