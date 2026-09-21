import re
from datetime import datetime


FAILED_LOGIN_PATTERN = re.compile(
    r"Failed password for (?P<username>\S+) from "
    r"(?P<source_ip>\d+\.\d+\.\d+\.\d+)"
)

INVALID_USER_PATTERN = re.compile(
    r"Invalid user (?P<username>\S+) from "
    r"(?P<source_ip>\d+\.\d+\.\d+\.\d+)"
)

SUCCESS_LOGIN_PATTERN = re.compile(
    r"Accepted password for (?P<username>\S+) from "
    r"(?P<source_ip>\d+\.\d+\.\d+\.\d+)"
)


def parse_timestamp(line):
    first_field = line.split(" ", 1)[0]

    try:
        return datetime.fromisoformat(first_field)
    except ValueError:
        return None


def parse_line(line):
    event = {
        "timestamp": parse_timestamp(line),
        "event_type": "unknown",
        "username": None,
        "source_ip": None,
        "message": line.strip(),
    }

    match = FAILED_LOGIN_PATTERN.search(line)

    if match:
        event["event_type"] = "ssh_failed_login"
        event["username"] = match.group("username")
        event["source_ip"] = match.group("source_ip")
        return event

    match = INVALID_USER_PATTERN.search(line)

    if match:
        event["event_type"] = "ssh_invalid_user"
        event["username"] = match.group("username")
        event["source_ip"] = match.group("source_ip")
        return event

    match = SUCCESS_LOGIN_PATTERN.search(line)

    if match:
        event["event_type"] = "ssh_successful_login"
        event["username"] = match.group("username")
        event["source_ip"] = match.group("source_ip")
        return event

    return event