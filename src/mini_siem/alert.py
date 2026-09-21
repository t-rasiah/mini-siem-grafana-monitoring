from datetime import datetime
from pathlib import Path


def write_alert(alert, logfile="/var/log/mini-siem/alerts.log"):
    path = Path(logfile)

    path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().astimezone().isoformat()

    lines = [
        f"timestamp={timestamp}",
        f"rule_id={alert['rule_id']}",
        f"severity={alert['severity']}",
        f"source_ip={alert['source_ip']}",
    ]

    if "username" in alert:
        lines.append(f"username={alert['username']}")

    if "attempts" in alert:
        lines.append(f"attempts={alert['attempts']}")

    lines.append(f"message={alert['message']}")

    with path.open("a", encoding="utf-8") as file:
        file.write(" | ".join(lines) + "\n")