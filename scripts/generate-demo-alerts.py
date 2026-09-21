#!/usr/bin/env python3

"""
Mini-SIEM Demo Alert Generator

Erzeugt reproduzierbare Demo-Alerts für die Visualisierung
in Grafana.

Die Alerts verwenden dasselbe Format wie die echten Alerts
des Mini-SIEM und werden nach /var/log/mini-siem/alerts.log
geschrieben.

Das Skript dient ausschliesslich zur Demonstration und
Visualisierung der vorhandenen Detection Rules.
"""

import random
from datetime import datetime, timezone


ALERT_LOG = "/var/log/mini-siem/alerts.log"
NUMBER_OF_ALERTS = 120

# Fester Seed sorgt dafür, dass die Demo reproduzierbar bleibt.
random.seed(42)


SOURCE_IPS = [
    "192.168.56.101",
    "192.168.56.102",
    "192.168.56.103",
    "192.168.56.104",
    "192.168.56.105",
    "10.10.10.21",
    "10.10.10.22",
    "172.16.20.15",
]


RULES = [
    {
        "rule_id": "SIEM-SSH-001",
        "severity": "WARNING",
        "message": "Multiple failed SSH login attempts detected",
    },
    {
        "rule_id": "SIEM-SSH-002",
        "severity": "CRITICAL",
        "message": "Possible SSH brute force attack detected",
    },
    {
        "rule_id": "SIEM-SSH-003",
        "severity": "SUSPICIOUS",
        "message": "SSH login attempt with invalid user detected",
    },
    {
        "rule_id": "SIEM-SSH-004",
        "severity": "HIGH",
        "message": "Successful SSH login after multiple failed attempts",
    },
]


USERNAMES = [
    "admin",
    "root",
    "testuser",
    "backup",
    "administrator",
    "oracle",
]


def create_alert():
    """Erzeugt einen einzelnen Demo-Alert."""

    rule = random.choice(RULES)
    source_ip = random.choice(SOURCE_IPS)
    attempts = random.randint(5, 25)

    timestamp = datetime.now(timezone.utc).isoformat()

    fields = [
        f"timestamp={timestamp}",
        f"rule_id={rule['rule_id']}",
        f"severity={rule['severity']}",
        f"source_ip={source_ip}",
    ]

    # Die Regeln 003 und 004 enthalten zusätzlich einen Benutzernamen.
    if rule["rule_id"] in ("SIEM-SSH-003", "SIEM-SSH-004"):
        username = random.choice(USERNAMES)
        fields.append(f"username={username}")

    fields.append(f"attempts={attempts}")
    fields.append(f"message={rule['message']}")

    return " | ".join(fields)


def main():
    print("=" * 60)
    print("Mini-SIEM Demo Alert Generator")
    print("=" * 60)
    print(f"Erzeuge {NUMBER_OF_ALERTS} Demo-Alerts...")
    print()

    with open(ALERT_LOG, "a", encoding="utf-8") as log_file:
        for _ in range(NUMBER_OF_ALERTS):
            alert = create_alert()
            log_file.write(alert + "\n")

    print(f"[OK] {NUMBER_OF_ALERTS} Demo-Alerts wurden erzeugt.")
    print(f"[OK] Zieldatei: {ALERT_LOG}")
    print()
    print("Grafana Alloy übernimmt die neuen Einträge automatisch.")


if __name__ == "__main__":
    main()
