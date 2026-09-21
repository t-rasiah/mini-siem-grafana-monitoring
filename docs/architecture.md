# Architektur

## Übersicht

Die Projektarbeit erweitert ein bestehendes Mini-SIEM um eine zentrale Visualisierung und Auswertung der erkannten Security Alerts.

Die Umgebung besteht aus zwei virtuellen Debian-Systemen. Der `projekt-log-client` erzeugt SSH-Logs und überträgt diese über rsyslog an den zentralen `projekt-mini-siem`.

Auf dem Mini-SIEM-Server analysiert eine Python-basierte Detection Engine die zentral gesammelten SSH-Ereignisse. Erkannte Security Events werden als strukturierte Alerts gespeichert.

Grafana Alloy überwacht die Alert-Datei und überträgt neue Einträge an Loki. Grafana verwendet Loki als Datenquelle und stellt die Security Alerts in einem zentralen Dashboard dar.

## Systemarchitektur

Die folgende Abbildung zeigt den vollständigen Datenfluss vom Log-Client bis zur Visualisierung in Grafana.

![Systemarchitektur des Mini-SIEM](screenshots/02-systemarchitektur.png)

## Virtuelle Maschinen

Die Projektumgebung besteht aus zwei virtuellen Maschinen:

| VM | IP-Adresse | Komponenten |
|---|---|---|
| `projekt-mini-siem` | `192.168.56.10` | rsyslog Server, Python Mini-SIEM, Grafana Alloy, Loki, Grafana |
| `projekt-log-client` | `192.168.56.20` | SSH-Server, rsyslog Client |

Die virtuellen Maschinen werden mit Vagrant und VirtualBox erstellt. Als Betriebssystem wird Debian Bookworm verwendet.

## Zentrale Logübertragung

Der `projekt-log-client` erzeugt unter anderem SSH-Authentifizierungsereignisse.

rsyslog überträgt die Logs über das interne Lab-Netzwerk an den Mini-SIEM-Server.

Die empfangenen Logs werden dort nach Hostname und Programm gespeichert.

Für die SSH-Logs des Log-Clients wird beispielsweise folgende Datei verwendet:

```text
/var/log/remote/projekt-log-client/sshd.log
```

Dadurch kann die Detection Engine die zentral gesammelten SSH-Ereignisse unabhängig vom ursprünglichen System analysieren.

## Python Mini-SIEM

Das Mini-SIEM besteht aus mehreren Python-Komponenten.

Der Parser erkennt relevante SSH-Ereignisse und wandelt sie in eine strukturierte Form um. Die Detection Engine wertet diese Events anschliessend anhand definierter Security-Regeln aus.

Folgende Detection Rules sind implementiert:

| Rule ID | Severity | Beschreibung |
|---|---|---|
| `SIEM-SSH-001` | WARNING | Mehrere fehlgeschlagene SSH-Anmeldungen |
| `SIEM-SSH-002` | CRITICAL | Möglicher SSH-Brute-Force-Angriff |
| `SIEM-SSH-003` | SUSPICIOUS | SSH-Anmeldung mit ungültigem Benutzer |
| `SIEM-SSH-004` | HIGH | Erfolgreiche SSH-Anmeldung nach mehreren Fehlversuchen |

Erkannte Security Alerts werden persistent unter folgendem Pfad gespeichert:

```text
/var/log/mini-siem/alerts.log
```

Ein Alert enthält unter anderem folgende Informationen:

```text
timestamp
rule_id
severity
source_ip
attempts
message
```

Je nach Detection Rule kann zusätzlich beispielsweise ein Benutzername enthalten sein.

## Grafana Alloy

Grafana Alloy übernimmt die Weiterleitung der erzeugten Security Alerts an Loki.

Alloy überwacht folgende Datei:

```text
/var/log/mini-siem/alerts.log
```

Die Security Alerts werden mit dem Job-Label:

```text
job="mini-siem"
```

an Loki übertragen.

Die Konfiguration befindet sich im Repository unter:

```text
config/alloy/config.alloy
```

Durch diese Trennung bleibt die Python Detection Engine unabhängig von Loki und Grafana.

## Loki

Loki dient als zentraler Logspeicher für die Security Alerts.

Grafana Alloy überträgt die Alert-Einträge über die lokale Loki-Schnittstelle:

```text
http://127.0.0.1:3100
```

Grafana verwendet Loki anschliessend als Datenquelle für die LogQL-Abfragen des Dashboards.

## Grafana

Grafana stellt die in Loki gespeicherten Security Alerts grafisch dar.

Das Dashboard trägt den Namen:

```text
Mini-SIEM Security Monitoring
```

Es enthält fünf zentrale Panels:

1. Total Security Alerts
2. Alerts by Severity
3. Alerts by Rule
4. Alerts by Source IP
5. Recent Security Alerts

Damit können sowohl die Gesamtzahl der erkannten Ereignisse als auch Severity-Stufen, Detection Rules und beteiligte Source-IPs ausgewertet werden.

![Grafana Dashboard](screenshots/05-grafana-dashboard.png)

## Automatische Provisionierung

Die Projektumgebung wird mit Vagrant reproduzierbar aufgebaut.

Die Monitoring-Konfiguration befindet sich vollständig im Git-Repository. Dazu gehören unter anderem:

```text
config/alloy/config.alloy
config/grafana/dashboards/mini-siem-security-monitoring.json
config/grafana/provisioning/dashboards/mini-siem.yml
config/grafana/provisioning/datasources/loki.yml
```

Die Installation und Konfiguration der Monitoring-Komponenten erfolgt über:

```text
provision/monitoring.sh
```

Beim Aufbau der VM werden Loki, Grafana Alloy und Grafana installiert und gestartet. Zusätzlich werden die Loki-Datenquelle und das Mini-SIEM-Dashboard automatisch provisioniert.

Dadurch kann die gesamte Umgebung mit folgendem Befehl aufgebaut werden:

```powershell
vagrant up
```

Ein manueller Aufbau des Grafana-Dashboards ist nach der Provisionierung nicht erforderlich.

## Datenfluss

Zusammengefasst durchläuft ein Security Event folgende Verarbeitungsschritte:

```text
SSH-Ereignis
    ↓
rsyslog Client
    ↓
rsyslog Server
    ↓
zentrale SSH-Logdatei
    ↓
Python Parser
    ↓
Detection Rules
    ↓
Security Alert
    ↓
alerts.log
    ↓
Grafana Alloy
    ↓
Loki
    ↓
LogQL
    ↓
Grafana Dashboard
```