# Installation und Inbetriebnahme

## Voraussetzungen

Für die lokale Ausführung werden benötigt:

- Git
- Vagrant
- VirtualBox

Die Installation der benötigten Software innerhalb der virtuellen Maschinen erfolgt automatisch über die Vagrant-Provisionierung.

## Repository klonen

In Windows PowerShell:

```powershell
git clone https://github.com/t-rasiah/mini-siem-grafana-monitoring.git
cd mini-siem-grafana-monitoring
```

## Virtuelle Maschinen starten

```powershell
vagrant up
```

Vagrant erstellt zwei Debian-VMs:

| VM | IP-Adresse |
|---|---|
| `projekt-mini-siem` | `192.168.56.10` |
| `projekt-log-client` | `192.168.56.20` |

Während der Provisionierung werden die benötigten Komponenten automatisch installiert und konfiguriert.

## Status prüfen

Auf dem Windows-Host:

```powershell
vagrant status
```

Beide Systeme sollten den Status `running` besitzen.

![Vagrant Status](screenshots/01-vagrant-status.png)

## Mini-SIEM-Server öffnen

Die Verbindung zum Mini-SIEM-Server erfolgt über Vagrant:

```powershell
vagrant ssh projekt-mini-siem
```

Die wichtigsten Services können anschliessend innerhalb der VM überprüft werden:

```bash
sudo systemctl is-active rsyslog
sudo systemctl is-active loki
sudo systemctl is-active alloy
sudo systemctl is-active grafana-server
```

Alle vier Services sollten `active` zurückgeben.

Die VM kann anschliessend mit folgendem Befehl verlassen werden:

```bash
exit
```

## Grafana öffnen

Grafana ist vom Windows-Host unter folgender Adresse erreichbar:

http://192.168.56.10:3000

Die Loki-Datenquelle und das Dashboard `Mini-SIEM Security Monitoring` werden automatisch provisioniert.

Das Dashboard befindet sich in Grafana im Ordner:

```text
Mini-SIEM
```

Eine manuelle Einrichtung der Loki-Datenquelle oder des Dashboards ist nicht erforderlich.

## Umgebung stoppen

Die virtuellen Maschinen können auf dem Windows-Host gestoppt werden:

```powershell
vagrant halt
```

## Umgebung erneut starten

Eine bereits vorhandene Umgebung kann wieder gestartet werden:

```powershell
vagrant up
```

## Umgebung vollständig neu aufbauen

Falls die virtuellen Maschinen vollständig neu aufgebaut werden sollen:

```powershell
vagrant destroy -f
vagrant up
```

Die Projektkonfiguration bleibt im Git-Repository erhalten und wird beim erneuten Aufbau automatisch angewendet.