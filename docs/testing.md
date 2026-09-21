# Tests und Validierung

## Ziel

Die Projektumgebung wurde mit automatisierten Tests sowie einem vollständigen End-to-End-Test überprüft.

Dabei wurde kontrolliert, dass:

- SSH-Logs zentral übertragen werden
- der Parser relevante SSH-Ereignisse erkennt
- die Detection Rules Security Alerts erzeugen
- Alerts persistent gespeichert werden
- Grafana Alloy die Alerts an Loki überträgt
- die Alerts über LogQL abgefragt werden können
- Grafana die Alerts im Dashboard visualisiert
- die Umgebung nach einem vollständigen Neuaufbau weiterhin funktioniert

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

Zusätzlich zu den automatisierten Tests wurde die vollständige Verarbeitungskette mit echten SSH-Fehlversuchen getestet.

### SSH-Fehlversuche erzeugen

Auf dem Log-Client wurde eine SSH-Anmeldung mit absichtlich falschem Passwort durchgeführt:

```bash
ssh -o PreferredAuthentications=password \
    -o PubkeyAuthentication=no \
    -o StrictHostKeyChecking=no \
    testuser@127.0.0.1
```

Mehrere fehlgeschlagene Login-Versuche erzeugen entsprechende Einträge im SSH-Log des Log-Clients.

### Zentrale Logübertragung

Die SSH-Logs werden über rsyslog an den Mini-SIEM-Server übertragen und dort zentral gespeichert:

```text
/var/log/remote/projekt-log-client/sshd.log
```

Damit wird geprüft, dass die zentrale Logübertragung vom `projekt-log-client` zum `projekt-mini-siem` funktioniert.

### Detection Engine

Anschliessend wird die Detection Engine auf dem Mini-SIEM ausgeführt:

```bash
cd /vagrant
python3 src/mini_siem/main.py
```

Bei Überschreitung des definierten Schwellwerts wird beispielsweise die Detection Rule `SIEM-SSH-001` ausgelöst.

Der folgende Screenshot zeigt einen durch die Detection Engine erkannten Security Alert:

![Erkannter Security Alert](screenshots/03-siem-alert.png)

Der erzeugte Alert wird persistent in folgender Datei gespeichert:

```text
/var/log/mini-siem/alerts.log
```

Die Alert-Einträge enthalten unter anderem:

```text
timestamp
rule_id
severity
source_ip
attempts
message
```

## Übertragung an Loki

Grafana Alloy überwacht die Alert-Datei und überträgt neue Einträge an die lokale Loki-Instanz.

Die in Loki gespeicherten Security Alerts können über Grafana Explore mit LogQL abgefragt werden.

Verwendete Abfrage:

```logql
{job="mini-siem"}
```

Der folgende Screenshot zeigt die in Loki verfügbaren Mini-SIEM-Alerts:

![Security Alerts in Grafana Explore](screenshots/04-grafana-explore.png)

Damit wurde folgende vollständige Verarbeitungskette erfolgreich getestet:

```text
SSH-Fehlversuch
      ↓
rsyslog Client
      ↓
rsyslog Server
      ↓
Python Mini-SIEM
      ↓
Security Alert
      ↓
Grafana Alloy
      ↓
Loki
      ↓
Grafana Dashboard
```

## Demo-Daten

Für eine aussagekräftigere Visualisierung des Dashboards steht zusätzlich ein Demo-Datengenerator zur Verfügung.

Das Skript wird auf dem Mini-SIEM mit folgendem Befehl gestartet:

```bash
python3 /vagrant/scripts/generate-demo-alerts.py
```

Bei einem Durchlauf werden 120 strukturierte Demo-Alerts erzeugt.

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

Die Demo-Daten dienen ausschliesslich zur Visualisierung und Demonstration des Dashboards. Sie sind vom End-to-End-Test mit echten SSH-Fehlversuchen zu unterscheiden.

## Grafana Dashboard

Die von Loki bereitgestellten Security Alerts werden im Dashboard `Mini-SIEM Security Monitoring` visualisiert.

Das Dashboard enthält fünf Panels:

1. Total Security Alerts
2. Alerts by Severity
3. Alerts by Rule
4. Alerts by Source IP
5. Recent Security Alerts

Durch die Demo-Daten können unterschiedliche Detection Rules, Severity-Stufen und Source-IPs gleichzeitig dargestellt werden.

![Grafana Dashboard](screenshots/05-grafana-dashboard.png)

## Reproduzierbarkeit

Vor Abschluss der Projektarbeit wurde ein vollständiger Clean Build durchgeführt.

Dazu wurden die beiden Projekt-VMs entfernt:

```powershell
vagrant destroy -f
```

Anschliessend wurde die gesamte Umgebung ausschliesslich anhand der im Git-Repository vorhandenen Dateien neu aufgebaut:

```powershell
vagrant up
```

Nach dem Neuaufbau wurden erneut überprüft:

- Status der beiden virtuellen Maschinen
- rsyslog
- Loki
- Grafana Alloy
- Grafana
- automatisierte Tests
- zentrale Logübertragung
- Detection Engine
- Alert-Übertragung an Loki
- Grafana-Dashboard

Das folgende Bild zeigt die beiden laufenden Projekt-VMs nach dem Aufbau:

![Vagrant Status](screenshots/01-vagrant-status.png)

Die Loki-Datenquelle und das Dashboard werden automatisch aus den im Repository enthaltenen Konfigurationsdateien provisioniert.

Dadurch kann die Projektumgebung mit `vagrant up` reproduzierbar aufgebaut werden.

## Bekannte Einschränkung

Die Detection Engine verarbeitet beim manuellen Start die vorhandene SSH-Logdatei erneut.

Wird die Detection Engine mehrfach gegen denselben Logbestand ausgeführt, können bereits erkannte Ereignisse erneut als Security Alert in `/var/log/mini-siem/alerts.log` geschrieben werden.

Für den Umfang dieser Projektarbeit wurde bewusst auf eine zusätzliche Zustandsverwaltung oder Datenbank zur Vermeidung solcher Duplikate verzichtet.