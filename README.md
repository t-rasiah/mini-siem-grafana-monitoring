# Mini-SIEM mit Grafana Monitoring


**Autor:** Thines Rasiah

**Klasse:** B-TIP-24-T-a

**Modul:** Cyber Security

**Dozent:** Christian Locher

**Schule:** TEKO Schweizerische Fachschule Bern


Dieses Projekt erweitert ein bestehendes Mini-SIEM um eine zentrale Logvisualisierung und Security-Monitoring-Lösung mit Grafana, Loki und Grafana Alloy.

## Ziel und Umfang

Ausgangspunkt der Arbeit ist ein bestehendes Python-basiertes Mini-SIEM zur Analyse von SSH-Logs. Ziel dieser Erweiterung ist der Aufbau einer reproduzierbaren zentralen Monitoring-Pipeline für die vom Mini-SIEM erzeugten Security Alerts.

Der Log-Client überträgt SSH-Logs zentral über rsyslog. Die Python-basierte Detection Engine analysiert die Ereignisse anhand definierter Detection Rules und schreibt erkannte Security Alerts in eine strukturierte Logdatei. Grafana Alloy übernimmt die Weiterleitung an Loki. Die Auswertung und Visualisierung erfolgt mit LogQL und Grafana.

Der Fokus liegt bewusst auf der Log- und Monitoring-Pipeline. Nicht Bestandteil des Projektumfangs sind eine zusätzliche Datenbank, ein eigenes Web-Frontend, Benutzerverwaltung oder externe Benachrichtigungssysteme.

## Architektur

Die Umgebung besteht aus zwei Debian-VMs:

| System | IP-Adresse | Aufgabe |
|---|---|---|
| `projekt-mini-siem` | `192.168.56.10` | Mini-SIEM, rsyslog, Grafana Alloy, Loki und Grafana |
| `projekt-log-client` | `192.168.56.20` | SSH-Server und rsyslog-Client |

Der zentrale Datenfluss vom Log-Client bis zur Visualisierung der Security Alerts:

![Datenfluss des Mini-SIEM](docs/screenshots/datenfluss.png)

Eine detaillierte Beschreibung der Architektur und der einzelnen Komponenten befindet sich in der [Architekturdokumentation](docs/architecture.md).

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
- LogQL
- Vagrant
- VirtualBox
- Debian Bookworm

## Voraussetzungen

Auf dem Host werden benötigt:

- Git
- Vagrant
- VirtualBox

Die innerhalb der virtuellen Maschinen benötigten Komponenten werden automatisch provisioniert.

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

Die Loki-Datenquelle und das Dashboard **Mini-SIEM Security Monitoring** werden automatisch provisioniert.

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

Die Tests überprüfen den SSH-Parser und die implementierten Detection Rules.

Aktueller Testumfang:

```text
10 passed
```

## Demo-Daten

Für die Visualisierung des Dashboards können reproduzierbare Demo-Alerts erzeugt werden.

Innerhalb der Mini-SIEM-VM:

```bash
python3 /vagrant/scripts/generate-demo-alerts.py
```

Ein Durchlauf erzeugt 120 Demo-Alerts mit unterschiedlichen Detection Rules, Severity-Stufen und Source-IPs.

Die Demo-Daten dienen ausschliesslich der Visualisierung und Demonstration des Dashboards. Der Funktionsnachweis der Detection Pipeline erfolgt separat über einen dokumentierten End-to-End-Test mit real erzeugten SSH-Fehlversuchen.

## Dashboard

Das Grafana-Dashboard visualisiert:

- Gesamtzahl der Security Alerts
- Alerts nach Severity
- Alerts nach Detection Rule
- Alerts nach Source IP
- aktuelle Security Alerts

![Grafana Dashboard](docs/screenshots/05-grafana-dashboard.png)

## Dokumentation

Weiterführende technische Dokumentation:

- [Architektur](docs/architecture.md)
- [Installation und Inbetriebnahme](docs/installation.md)
- [Tests und Validierung](docs/testing.md)