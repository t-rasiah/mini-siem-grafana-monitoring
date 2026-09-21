from collections import defaultdict
from datetime import timedelta


def detect_failed_login_threshold(
    events,
    threshold,
    timeframe_seconds,
    rule_id,
    severity,
    message,
):
    failed_logins = defaultdict(list)
    alerts = []

    for event in events:
        if event["event_type"] != "ssh_failed_login":
            continue

        source_ip = event["source_ip"]
        timestamp = event["timestamp"]

        if source_ip is None or timestamp is None:
            continue

        failed_logins[source_ip].append(timestamp)

    for source_ip, timestamps in failed_logins.items():
        timestamps.sort()

        for index, start_time in enumerate(timestamps):
            end_time = start_time + timedelta(seconds=timeframe_seconds)

            attempts = [
                timestamp
                for timestamp in timestamps[index:]
                if timestamp <= end_time
            ]

            if len(attempts) >= threshold:
                alerts.append(
                    {
                        "rule_id": rule_id,
                        "severity": severity,
                        "source_ip": source_ip,
                        "attempts": len(attempts),
                        "timeframe_seconds": timeframe_seconds,
                        "message": message,
                    }
                )

                break

    return alerts


def detect_invalid_user(events):
    alerts = []

    for event in events:
        if event["event_type"] != "ssh_invalid_user":
            continue

        alerts.append(
            {
                "rule_id": "SIEM-SSH-003",
                "severity": "SUSPICIOUS",
                "source_ip": event["source_ip"],
                "username": event["username"],
                "message": "SSH login attempt with invalid user detected",
            }
        )

    return alerts


def detect_success_after_failures(
    events,
    threshold=5,
    timeframe_seconds=300,
):
    alerts = []

    valid_events = [
        event
        for event in events
        if event["timestamp"] is not None
    ]

    valid_events.sort(
        key=lambda event: event["timestamp"]
    )

    for index, event in enumerate(valid_events):
        if event["event_type"] != "ssh_successful_login":
            continue

        source_ip = event["source_ip"]
        username = event["username"]
        success_time = event["timestamp"]

        if source_ip is None:
            continue

        failed_events = []

        for previous_event in valid_events[:index]:
            if previous_event["event_type"] != "ssh_failed_login":
                continue

            if previous_event["source_ip"] != source_ip:
                continue

            failed_time = previous_event["timestamp"]

            seconds_before_success = (
                success_time - failed_time
            ).total_seconds()

            if 0 <= seconds_before_success <= timeframe_seconds:
                failed_events.append(previous_event)

        if len(failed_events) >= threshold:
            alerts.append(
                {
                    "rule_id": "SIEM-SSH-004",
                    "severity": "HIGH",
                    "source_ip": source_ip,
                    "username": username,
                    "attempts": len(failed_events),
                    "message": (
                        "Successful SSH login after "
                        "multiple failed attempts"
                    ),
                }
            )

    return alerts