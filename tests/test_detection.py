import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))

from mini_siem.detection import (
    detect_failed_login_threshold,
    detect_invalid_user,
    detect_success_after_failures,
)


def make_failed_login(timestamp, source_ip="192.168.56.30"):
    return {
        "timestamp": timestamp,
        "event_type": "ssh_failed_login",
        "username": "testuser",
        "source_ip": source_ip,
        "message": "Failed SSH login",
    }


def test_rule_001_warning_is_triggered():
    events = [
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 1, tzinfo=timezone.utc)
        ),
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 10, tzinfo=timezone.utc)
        ),
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 20, tzinfo=timezone.utc)
        ),
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 30, tzinfo=timezone.utc)
        ),
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 40, tzinfo=timezone.utc)
        ),
    ]

    alerts = detect_failed_login_threshold(
        events=events,
        threshold=5,
        timeframe_seconds=60,
        rule_id="SIEM-SSH-001",
        severity="WARNING",
        message="Multiple failed SSH login attempts detected",
    )

    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "SIEM-SSH-001"
    assert alerts[0]["severity"] == "WARNING"
    assert alerts[0]["source_ip"] == "192.168.56.30"


def test_rule_001_warning_is_not_triggered():
    events = [
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 1, tzinfo=timezone.utc)
        ),
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 10, tzinfo=timezone.utc)
        ),
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 20, tzinfo=timezone.utc)
        ),
        make_failed_login(
            datetime(2026, 8, 21, 19, 0, 30, tzinfo=timezone.utc)
        ),
    ]

    alerts = detect_failed_login_threshold(
        events=events,
        threshold=5,
        timeframe_seconds=60,
        rule_id="SIEM-SSH-001",
        severity="WARNING",
        message="Multiple failed SSH login attempts detected",
    )

    assert len(alerts) == 0


def test_rule_002_critical_is_triggered():
    base_time = datetime(
        2026,
        8,
        21,
        19,
        0,
        0,
        tzinfo=timezone.utc,
    )

    events = [
        make_failed_login(
            base_time + timedelta(seconds=index * 10)
        )
        for index in range(10)
    ]

    alerts = detect_failed_login_threshold(
        events=events,
        threshold=10,
        timeframe_seconds=300,
        rule_id="SIEM-SSH-002",
        severity="CRITICAL",
        message="Possible SSH brute-force attack detected",
    )

    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "SIEM-SSH-002"
    assert alerts[0]["severity"] == "CRITICAL"


def test_rule_002_critical_is_not_triggered():
    events = []

    for index in range(9):
        events.append(
            make_failed_login(
                datetime(
                    2026,
                    8,
                    21,
                    19,
                    0,
                    index * 5,
                    tzinfo=timezone.utc,
                )
            )
        )

    alerts = detect_failed_login_threshold(
        events=events,
        threshold=10,
        timeframe_seconds=300,
        rule_id="SIEM-SSH-002",
        severity="CRITICAL",
        message="Possible SSH brute-force attack detected",
    )

    assert len(alerts) == 0


def test_rule_003_invalid_user_is_triggered():
    events = [
        {
            "timestamp": datetime(
                2026,
                8,
                21,
                19,
                10,
                0,
                tzinfo=timezone.utc,
            ),
            "event_type": "ssh_invalid_user",
            "username": "administrator",
            "source_ip": "192.168.56.40",
            "message": "Invalid user administrator",
        }
    ]

    alerts = detect_invalid_user(events)

    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "SIEM-SSH-003"
    assert alerts[0]["severity"] == "SUSPICIOUS"
    assert alerts[0]["username"] == "administrator"
    assert alerts[0]["source_ip"] == "192.168.56.40"


def test_rule_004_success_after_failures_is_triggered():
    base_time = datetime(
        2026,
        8,
        21,
        19,
        0,
        0,
        tzinfo=timezone.utc,
    )

    events = [
        make_failed_login(
            base_time + timedelta(seconds=index * 10),
            source_ip="192.168.56.70",
        )
        for index in range(5)
    ]

    events.append(
        {
            "timestamp": base_time + timedelta(seconds=60),
            "event_type": "ssh_successful_login",
            "username": "testuser",
            "source_ip": "192.168.56.70",
            "message": "Accepted password",
        }
    )

    alerts = detect_success_after_failures(
        events=events,
        threshold=5,
        timeframe_seconds=300,
    )

    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "SIEM-SSH-004"
    assert alerts[0]["severity"] == "HIGH"
    assert alerts[0]["source_ip"] == "192.168.56.70"

def test_rule_004_success_after_failures_is_not_triggered():
    base_time = datetime(
        2026,
        8,
        21,
        19,
        0,
        0,
        tzinfo=timezone.utc,
    )

    events = [
        make_failed_login(
            base_time + timedelta(seconds=index * 10),
            source_ip="192.168.56.70",
        )
        for index in range(4)
    ]

    events.append(
        {
            "timestamp": base_time + timedelta(seconds=60),
            "event_type": "ssh_successful_login",
            "username": "testuser",
            "source_ip": "192.168.56.70",
            "message": "Accepted password",
        }
    )

    alerts = detect_success_after_failures(
        events=events,
        threshold=5,
        timeframe_seconds=300,
    )

    assert len(alerts) == 0