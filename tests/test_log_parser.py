import pytest

from src.core.log_parser import parse_log_line


class TestLogParser:
    """Test the old format: email before IP."""

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


class TestNewLogFormat:
    """Test the new Xray format: IP before email, numeric prefix."""

    def test_new_format_basic(self):
        line = (
            "2026/03/29 19:54:39.164745 from tcp:185.69.186.224:0 "
            "accepted udp:1.1.1.1:53 [VLESS WS TLS >> DIRECT] email: 120.koko_rahman"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "koko_rahman"
        assert entry.source_ip == "185.69.186.224"

    def test_new_format_without_tcp_prefix(self):
        line = (
            "2026/03/29 19:54:30.385379 from 95.85.104.49:0 "
            "accepted tcp:57.144.223.33:5222 [VLESS FASTLY XHTTP >> DIRECT] email: 834.Fidel_Own"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "Fidel_Own"
        assert entry.source_ip == "95.85.104.49"

    def test_new_format_udp_prefix(self):
        line = (
            "2026/03/29 19:54:32.158207 from 185.69.185.148:0 "
            "accepted udp:us-central1-gcp.api.snapchat.com:443 "
            "[VLESS WS TLS >> DIRECT] email: 1268.nashoto_orazmyrat"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "nashoto_orazmyrat"
        assert entry.source_ip == "185.69.185.148"

    def test_numeric_prefix_stripped(self):
        line = (
            "2026/03/29 19:54:41.242507 from 93.171.220.14:0 "
            "accepted tcp:some.host:443 [VLESS >> DIRECT] email: 963.koko_nazik"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "koko_nazik"
        assert entry.email == "963.koko_nazik"

    def test_new_format_with_brackets(self):
        line = (
            "2026/03/29 19:54:41.802960 from 85.239.53.126:4374 "
            "accepted udp:216.239.32.223:443 "
            "[VLESS TCP France >> DIRECT] email: 1177.Zakiraga"
        )
        entry = parse_log_line(line)
        assert entry is not None
        assert entry.username == "Zakiraga"
        assert entry.source_ip == "85.239.53.126"
