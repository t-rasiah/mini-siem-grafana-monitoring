# pathlib.Path ermöglicht einen sauberen Umgang mit Datei- und Verzeichnispfaden.
from pathlib import Path

# PyYAML wird verwendet, um unsere Datei config/siem.yaml einzulesen.
import yaml

# write_alert speichert erkannte Security Alerts dauerhaft in alerts.log.
from alert import write_alert

# Hier importieren wir unsere Detection-Funktionen.
from detection import (
    detect_failed_login_threshold,
    detect_invalid_user,
    detect_success_after_failures,
)

# parse_line analysiert eine einzelne SSH-Logzeile
# und wandelt sie in ein strukturiertes Event um.
from parser import parse_line


# ============================================================
# LOGDATEI EINLESEN
# ============================================================

def load_events(logfile):
    """
    Liest eine Logdatei ein und wandelt erkannte Logzeilen
    mit unserem Parser in strukturierte Events um.
    """

    # Aus dem übergebenen Dateinamen wird ein Path-Objekt.
    path = Path(logfile)

    # Prüfen, ob die Logdatei überhaupt existiert.
    if not path.exists():
        print(f"[ERROR] Logfile not found: {path}")
        return []

    # Hier sammeln wir alle erkannten Events.
    events = []

    # Logdatei im Lesemodus öffnen.
    with path.open("r", encoding="utf-8") as file:

        # Jede Logzeile einzeln verarbeiten.
        for line in file:

            # Die Zeile durch unseren SSH-Parser schicken.
            event = parse_line(line)

            # Unbekannte Logeinträge benötigen wir für unsere
            # aktuellen Detection Rules nicht.
            if event["event_type"] != "unknown":
                events.append(event)

    # Alle erkannten Events zurückgeben.
    return events


# ============================================================
# YAML-KONFIGURATION EINLESEN
# ============================================================

def load_config(configfile):
    """
    Liest die zentrale Mini-SIEM-Konfiguration aus einer
    YAML-Datei ein.
    """

    # Pfad zur Konfigurationsdatei erstellen.
    path = Path(configfile)

    # Prüfen, ob die Datei vorhanden ist.
    if not path.exists():
        print(f"[ERROR] Config file not found: {path}")
        return {}

    # YAML-Datei öffnen.
    with path.open("r", encoding="utf-8") as file:

        # YAML in ein Python-Dictionary umwandeln.
        return yaml.safe_load(file)


# ============================================================
# ALERT IM TERMINAL AUSGEBEN
# ============================================================

def print_alert(alert):
    """
    Gibt einen erkannten Security Alert lesbar im Terminal aus.
    """

    print()
    print("=" * 50)
    print("[SECURITY ALERT]")

    # ID der Detection Rule.
    print(f"Rule:     {alert['rule_id']}")

    # Schweregrad des Alerts.
    print(f"Severity: {alert['severity']}")

    # IP-Adresse, von der das Ereignis ausging.
    print(f"Source:   {alert['source_ip']}")

    # Nicht jeder Alert besitzt einen Benutzernamen.
    # Deshalb prüfen wir zuerst, ob das Feld existiert.
    if "username" in alert:
        print(f"User:     {alert['username']}")

    # Dasselbe gilt für die Anzahl der Loginversuche.
    if "attempts" in alert:
        print(f"Attempts: {alert['attempts']}")

    # Beschreibung des Alerts.
    print(f"Message:  {alert['message']}")

    print("=" * 50)


# ============================================================
# HAUPTPROGRAMM
# ============================================================

def main():

    # --------------------------------------------------------
    # Pfade
    # --------------------------------------------------------

    # Hier liegen die echten SSH-Logs des log-client,
    # die über rsyslog an mini-siem übertragen werden.
    logfile = "/var/log/remote/projekt-log-client/sshd.log"

    # Zentrale Konfigurationsdatei für unsere Detection Rules.
    configfile = "/vagrant/config/siem.yaml"

    print("[INFO] Mini-SIEM Security Log Analyzer")
    print(f"[INFO] Reading: {logfile}")
    print(f"[INFO] Config:  {configfile}")

    # --------------------------------------------------------
    # Logs laden
    # --------------------------------------------------------

    events = load_events(logfile)

    print(f"[INFO] Parsed events: {len(events)}")

    # --------------------------------------------------------
    # Konfiguration laden
    # --------------------------------------------------------

    config = load_config(configfile)

    # Sicherheitsprüfung:
    # Ohne gültige Konfiguration soll das Programm abbrechen.
    if not config or "rules" not in config:
        print("[ERROR] Invalid configuration.")
        return

    # Alle Detection Rules aus YAML laden.
    rules = config["rules"]

    # Diese Liste sammelt später alle gefundenen Alerts.
    alerts = []

    # ========================================================
    # RULE 1 - Mehrere fehlgeschlagene SSH-Logins
    # ========================================================

    rule_001 = rules["SIEM-SSH-001"]

    # Die Regel wird nur ausgeführt, wenn enabled=true ist.
    if rule_001["enabled"]:

        warning_alerts = detect_failed_login_threshold(
            events=events,

            # Diese Werte kommen jetzt aus siem.yaml.
            threshold=rule_001["threshold"],
            timeframe_seconds=rule_001["timeframe_seconds"],

            rule_id="SIEM-SSH-001",
            severity=rule_001["severity"],
            message=rule_001["message"],
        )

        # Gefundene Alerts zur Gesamtliste hinzufügen.
        alerts.extend(warning_alerts)

    # ========================================================
    # RULE 2 - SSH Brute Force
    # ========================================================

    rule_002 = rules["SIEM-SSH-002"]

    if rule_002["enabled"]:

        critical_alerts = detect_failed_login_threshold(
            events=events,

            # Auch diese Werte kommen aus YAML.
            threshold=rule_002["threshold"],
            timeframe_seconds=rule_002["timeframe_seconds"],

            rule_id="SIEM-SSH-002",
            severity=rule_002["severity"],
            message=rule_002["message"],
        )

        alerts.extend(critical_alerts)

    # ========================================================
    # RULE 3 - Invalid User
    # ========================================================

    rule_003 = rules["SIEM-SSH-003"]

    if rule_003["enabled"]:

        # Diese Detection benötigt momentan keinen Threshold.
        invalid_user_alerts = detect_invalid_user(events)

        alerts.extend(invalid_user_alerts)

    # ========================================================
    # RULE 4 - Erfolgreicher Login nach Fehlversuchen
    # ========================================================

    rule_004 = rules["SIEM-SSH-004"]

    if rule_004["enabled"]:

        success_after_failures_alerts = detect_success_after_failures(
            events=events,

            # Threshold und Zeitraum kommen ebenfalls aus YAML.
            threshold=rule_004["threshold"],
            timeframe_seconds=rule_004["timeframe_seconds"],
        )

        alerts.extend(success_after_failures_alerts)

    # ========================================================
    # ERGEBNIS
    # ========================================================

    # Wenn keine Detection Rule ausgelöst wurde:
    if not alerts:
        print("[INFO] No security alerts detected.")
        return

    # Alle gefundenen Alerts verarbeiten.
    for alert in alerts:

        # Alert im Terminal anzeigen.
        print_alert(alert)

        # Alert zusätzlich dauerhaft in alerts.log speichern.
        write_alert(alert)


# ============================================================
# PROGRAMMSTART
# ============================================================

# Dieser Block sorgt dafür, dass main() nur ausgeführt wird,
# wenn main.py direkt gestartet wird.
if __name__ == "__main__":
    main()
    