# Mini-SIEM mit Grafana Monitoring

| | |
|---|---|
| **Autor** | Thines Rasiah |
| **Klasse** | B-TIP-24-T-a |
| **Modul** | Cyber Security |
| **Dozent** | Christian Locher |
| **Schule** | TEKO Schweizerische Fachschule Bern |

Dieses Projekt erweitert ein bestehendes Mini-SIEM um eine zentrale Logvisualisierung und Security-Monitoring-Lösung mit Grafana, Loki und Grafana Alloy.

## Projektübersicht

Das Projekt sammelt SSH-Logs eines separaten Log-Clients zentral über rsyslog. Eine Python-basierte Detection Engine analysiert die Logs anhand definierter Security-Regeln und schreibt erkannte Security Alerts in eine strukturierte Logdatei.

Grafana Alloy überträgt diese Alerts an Loki. Grafana verwendet Loki anschliessend als Datenquelle und visualisiert die Security Alerts in einem zentralen Dashboard.

## Architektur

Die Umgebung besteht aus zwei Debian-VMs:

| System | IP-Adresse | Aufgabe |
|---|---|---|
| `projekt-mini-siem` | `192.168.56.10` | Mini-SIEM, rsyslog, Grafana Alloy, Loki und Grafana |
| `projekt-log-client` | `192.168.56.20` | SSH-Server und rsyslog-Client |

Der zentrale Datenfluss:

```text
projekt-log-client
        │
        │ rsyslog
        ▼
projekt-mini-siem
        │
        │ Python Detection Engine
        ▼
Security Alerts
        │
        │ Grafana Alloy
        ▼
      Loki
        │
        ▼
     Grafana
```

Eine detaillierte Darstellung befindet sich in der [Architekturdokumentation](docs/architecture.md).

## Security Detection Rules

Das Mini-SIEM implementiert vier Detection Rules:

| Rule ID | Severity | Erkennung |
|---|---|---|
| `SIEM-SSH-001` | WARNING | Mehrere fehlgeschlagene SSH-Anmeldungen |
| `SIEM-SSH-002` | CRITICAL | Möglicher SSH-Brute-Force-Angriff |
| `SIEM-SSH-003` | SUSPICIOUS | SSH-Anmeldung mit ungültigem Benutzer |
| `SIEM-SSH-004` | HIGH | Erfolgreiche SSH-Anmeldung nach mehreren Fehlversuchen |

## Technologien

- Python 3
- pytest
- rsyslog
- Grafana Alloy
- Grafana Loki
- Grafana
- Vagrant
- VirtualBox
- Debian Bookworm

## Voraussetzungen

Auf dem Host werden benötigt:

- Git
- Vagrant
- VirtualBox

## Quick Start

Repository klonen:

```powershell
git clone https://github.com/t-rasiah/mini-siem-grafana-monitoring.git
cd mini-siem-grafana-monitoring
```

Virtuelle Maschinen erstellen:

```powershell
vagrant up
```

Status prüfen:

```powershell
vagrant status
```

Nach erfolgreicher Provisionierung ist Grafana unter folgender Adresse erreichbar:

http://192.168.56.10:3000

Das Dashboard **Mini-SIEM Security Monitoring** wird automatisch provisioniert.

## Automatisierte Tests

Auf den Mini-SIEM-Server verbinden:

```powershell
vagrant ssh projekt-mini-siem
```

Tests innerhalb der VM ausführen:

```bash
cd /vagrant
pytest -v
```

Die Tests prüfen den SSH-Parser und die implementierten Detection Rules.

Aktueller Testumfang:

```text
10 passed
```

## Demo-Daten

Für eine aussagekräftige Visualisierung können reproduzierbare Demo-Alerts erzeugt werden.

Innerhalb der Mini-SIEM-VM:

```bash
python3 /vagrant/scripts/generate-demo-alerts.py
```

Das Skript erzeugt 120 Demo-Alerts mit unterschiedlichen Detection Rules, Severity-Stufen und Source-IPs.

Die Demo-Daten dienen ausschliesslich der Visualisierung und ersetzen nicht den durchgeführten End-to-End-Test mit echten SSH-Fehlversuchen.

## Dashboard

Das Grafana-Dashboard visualisiert:

- Gesamtzahl der Security Alerts
- Alerts nach Severity
- Alerts nach Detection Rule
- Alerts nach Source IP
- aktuelle Security Alerts

![Grafana Dashboard](docs/screenshots/05-grafana-dashboard.png)

## Dokumentation

Weitere technische Informationen:

- [Architektur](docs/architecture.md)
- [Installation und Inbetriebnahme](docs/installation.md)
- [Tests und Validierung](docs/testing.md)