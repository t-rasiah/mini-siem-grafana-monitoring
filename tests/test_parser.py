import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from mini_siem.parser import parse_line


def test_failed_ssh_login():
    line = (
        "2026-08-21T18:50:01+00:00 log-client sshd[1201]: "
        "Failed password for testuser from 192.168.56.30 port 50101 ssh2"
    )

    event = parse_line(line)

    assert event["event_type"] == "ssh_failed_login"
    assert event["username"] == "testuser"
    assert event["source_ip"] == "192.168.56.30"


def test_invalid_user():
    line = (
        "2026-08-21T18:51:01+00:00 log-client sshd[1301]: "
        "Invalid user administrator from 192.168.56.40 port 50201"
    )

    event = parse_line(line)

    assert event["event_type"] == "ssh_invalid_user"
    assert event["username"] == "administrator"
    assert event["source_ip"] == "192.168.56.40"


def test_successful_login():
    line = (
        "2026-08-21T18:52:01+00:00 log-client sshd[1401]: "
        "Accepted password for testuser from 192.168.56.50 port 50301 ssh2"
    )

    event = parse_line(line)

    assert event["event_type"] == "ssh_successful_login"
    assert event["username"] == "testuser"
    assert event["source_ip"] == "192.168.56.50"