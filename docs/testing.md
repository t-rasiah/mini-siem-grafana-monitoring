# Tests und Validierung

## Ziel

Die Projektumgebung wurde mit automatisierten Tests sowie einem vollständigen End-to-End- und Reproduzierbarkeitstest überprüft.

Validiert wurden:

- automatisierter Aufbau der Umgebung
- Kommunikation zwischen den virtuellen Maschinen
- zentrale Übertragung der SSH-Logs
- Erkennung relevanter SSH-Ereignisse durch den Parser
- Auslösung der definierten Detection Rules
- persistente Speicherung erzeugter Security Alerts
- Übertragung der Alerts durch Grafana Alloy
- Speicherung und Abfrage der Alerts in Loki
- automatische Provisionierung der Loki-Datenquelle
- automatische Provisionierung des Grafana-Dashboards
- Visualisierung der Security Alerts in Grafana
- reproduzierbarer Aufbau aus einem frischen GitHub-Clone

## Automatisierte Tests

Für den Parser und die Detection Rules stehen automatisierte Tests mit `pytest` zur Verfügung.

Zuerst wird eine Verbindung zum Mini-SIEM-Server hergestellt:

```powershell
vagrant ssh projekt-mini-siem
```

Anschliessend werden die Tests innerhalb der VM ausgeführt:

```bash
cd /vagrant
pytest -v
```

Die Test-Suite überprüft den SSH-Parser sowie die implementierten Detection Rules.

Das Testergebnis:

```text
10 passed
```

![Erfolgreiche pytest-Tests](screenshots/06-pytest.png)

## End-to-End-Test

Zusätzlich zu den automatisierten Tests wurde die vollständige Verarbeitungskette mit real erzeugten SSH-Fehlversuchen getestet.

### SSH-Fehlversuche erzeugen

Auf dem Log-Client wurde eine SSH-Anmeldung mit absichtlich falschem Passwort durchgeführt:

```bash
ssh -o PreferredAuthentications=password \
    -o PubkeyAuthentication=no \
    -o StrictHostKeyChecking=no \
    testuser@127.0.0.1
```

Durch mehrere fehlgeschlagene Login-Versuche wurden reale SSH-Authentifizierungsereignisse erzeugt.

### Zentrale Logübertragung

Die SSH-Logs wurden über rsyslog an den Mini-SIEM-Server übertragen und dort zentral gespeichert:

```text
/var/log/remote/projekt-log-client/sshd.log
```

Die zentrale Übertragung wurde zusätzlich mit einem eindeutig identifizierbaren Testeintrag überprüft:

```bash
logger -p auth.info "MINI-SIEM-FINAL-TEST"
```

Der Eintrag konnte anschliessend auf dem Mini-SIEM unter `/var/log/remote/` nachgewiesen werden.

Damit wurde die tatsächliche Logübertragung zwischen:

```text
projekt-log-client
192.168.56.20
        ↓
      rsyslog
        ↓
projekt-mini-siem
192.168.56.10
```

erfolgreich validiert.

### Detection Engine

Anschliessend wurde die Detection Engine auf dem Mini-SIEM ausgeführt:

```bash
cd /vagrant
python3 src/mini_siem/main.py
```

Beim finalen End-to-End-Test wurden 12 relevante SSH-Ereignisse verarbeitet.

Dabei wurden unter anderem folgende Detection Rules ausgelöst:

| Rule ID | Severity | Ergebnis |
|---|---|---|
| `SIEM-SSH-001` | WARNING | Mehrere fehlgeschlagene SSH-Anmeldungen erkannt |
| `SIEM-SSH-002` | CRITICAL | Möglicher SSH-Brute-Force-Angriff erkannt |

Der folgende Screenshot dokumentiert einen durch die Detection Engine erkannten Security Alert:

![Erkannter Security Alert](screenshots/03-siem-alert.png)

Die erzeugten Alerts werden unter folgendem Pfad gespeichert:

```text
/var/log/mini-siem/alerts.log
```

Ein Alert enthält abhängig von der Detection Rule unter anderem:

```text
timestamp
rule_id
severity
source_ip
attempts
username
message
```

## Übertragung an Loki

Grafana Alloy überwacht die Alert-Datei und überträgt neue Einträge an die lokale Loki-Instanz.

Die in Loki gespeicherten Security Alerts wurden über Grafana Explore mit folgender LogQL-Abfrage überprüft:

```logql
{job="mini-siem"}
```

Beim finalen End-to-End-Test waren dort die real erzeugten Alerts sichtbar, unter anderem:

```text
SIEM-SSH-001
severity=WARNING
source_ip=127.0.0.1
```

sowie:

```text
SIEM-SSH-002
severity=CRITICAL
source_ip=127.0.0.1
```

Der folgende Screenshot zeigt die Abfrage der Mini-SIEM-Alerts über Grafana Explore:

![Security Alerts in Grafana Explore](screenshots/04-grafana-explore.png)

Damit wurde folgende Verarbeitungskette praktisch validiert:

```text
SSH-Fehlversuch
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
Grafana Alloy
      ↓
Loki
      ↓
Grafana
```

## Grafana Dashboard

Die von Loki bereitgestellten Security Alerts werden im Dashboard `Mini-SIEM Security Monitoring` visualisiert.

Das Dashboard enthält fünf Panels:

1. Total Security Alerts
2. Alerts by Severity
3. Alerts by Rule
4. Alerts by Source IP
5. Recent Security Alerts

Das Dashboard wird während der Provisionierung automatisch aus der im Repository enthaltenen JSON-Datei bereitgestellt.

Dadurch ist nach einem vollständigen Neuaufbau keine manuelle Erstellung des Dashboards erforderlich.

![Grafana Dashboard](screenshots/05-grafana-dashboard.png)

## Demo-Daten

Für eine aussagekräftige Visualisierung des Dashboards steht zusätzlich ein reproduzierbarer Demo-Datengenerator zur Verfügung.

Das Skript wird auf dem Mini-SIEM mit folgendem Befehl gestartet:

```bash
python3 /vagrant/scripts/generate-demo-alerts.py
```

Ein Durchlauf erzeugt 120 strukturierte Demo-Alerts.

Die Demo-Daten enthalten unterschiedliche:

- Detection Rules
- Severity-Stufen
- Source-IPs
- Benutzernamen

Dabei werden die vier bestehenden Detection Rules verwendet:

| Rule ID | Severity | Beschreibung |
|---|---|---|
| `SIEM-SSH-001` | WARNING | Mehrere fehlgeschlagene SSH-Anmeldungen |
| `SIEM-SSH-002` | CRITICAL | Möglicher SSH-Brute-Force-Angriff |
| `SIEM-SSH-003` | SUSPICIOUS | SSH-Anmeldung mit ungültigem Benutzer |
| `SIEM-SSH-004` | HIGH | Erfolgreiche SSH-Anmeldung nach mehreren Fehlversuchen |

Die Demo-Daten dienen ausschliesslich zur Demonstration und Visualisierung des Dashboards. Sie sind nicht als Nachweis eines realen Angriffs zu interpretieren.

Der Funktionsnachweis der eigentlichen Detection Pipeline erfolgt separat über den dokumentierten End-to-End-Test mit real erzeugten SSH-Fehlversuchen.

## Reproduzierbarkeitstest

Zum Abschluss wurde die Reproduzierbarkeit der gesamten Projektumgebung unabhängig vom bestehenden lokalen Arbeitsverzeichnis überprüft.

Dazu wurden zunächst die bestehenden Projekt-VMs entfernt.

Anschliessend wurde das Repository in ein neues Verzeichnis direkt von GitHub geklont.

Aus diesem frischen Clone wurde die komplette Umgebung ausschliesslich mit folgendem Befehl aufgebaut:

```powershell
vagrant up
```

Nach der Provisionierung wurden folgende Punkte überprüft:

- beide virtuellen Maschinen wurden erfolgreich erstellt
- `projekt-mini-siem` war unter `192.168.56.10` erreichbar
- `projekt-log-client` war unter `192.168.56.20` erreichbar
- die Kommunikation zwischen beiden Systemen funktionierte
- rsyslog übertrug Logeinträge zwischen beiden Systemen
- die automatisierten Tests ergaben `10 passed`
- reale SSH-Fehlversuche wurden zentral übertragen
- `SIEM-SSH-001` und `SIEM-SSH-002` wurden ausgelöst
- die erzeugten Alerts wurden in `alerts.log` gespeichert
- Grafana Alloy übertrug die Alerts an Loki
- die Alerts konnten über Grafana Explore abgefragt werden
- die Loki-Datenquelle wurde automatisch provisioniert
- das Dashboard `Mini-SIEM Security Monitoring` wurde automatisch provisioniert
- die Security Alerts wurden im Grafana-Dashboard dargestellt

Damit wurde nachgewiesen, dass die Projektumgebung aus den im Git-Repository enthaltenen Dateien reproduzierbar aufgebaut werden kann.

## Bekannte Einschränkungen

Die Detection Engine arbeitet derzeit zustandslos auf der vorhandenen SSH-Logdatei.

Wird sie mehrfach gegen denselben Logbestand ausgeführt, können bereits verarbeitete Ereignisse erneut erkannt und als Security Alert in `/var/log/mini-siem/alerts.log` geschrieben werden.

Für den definierten Projektumfang wurde bewusst auf eine persistente Zustandsverwaltung oder zusätzliche Datenbank verzichtet. In einer produktiven SIEM-Implementierung müsste der Verarbeitungsstand beispielsweise über Offsets, Event-IDs oder eine persistente Zustandsverwaltung nachvollzogen werden.

Der Demo-Datengenerator schreibt synthetische Security Alerts ebenfalls in `/var/log/mini-siem/alerts.log`. Wird das Skript mehrfach ausgeführt, werden entsprechend weitere Demo-Alerts angehängt.

Reale und synthetische Alerts werden in der aktuellen Implementierung nicht durch ein zusätzliches Herkunftslabel getrennt. Der reale End-to-End-Test wurde deshalb separat durchgeführt und dokumentiert, bevor die Demo-Daten für die vollständige Dashboard-Visualisierung verwendet wurden.