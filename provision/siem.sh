#!/bin/bash

# ============================================================
# Mini-SIEM Provisioning
# ============================================================

# Script bei einem Fehler sofort abbrechen.
set -e

echo "[INFO] Provisioning mini-siem..."


# ============================================================
# PAKETQUELLEN AKTUALISIEREN
# ============================================================

apt-get update


# ============================================================
# BENÖTIGTE SOFTWARE INSTALLIEREN
# ============================================================

apt-get install -y \
    rsyslog \
    python3 \
    python3-pip \
    python3-venv \
    python3-pytest \
    python3-yaml


# ============================================================
# MINI-SIEM GRUPPE
# ============================================================

# Gruppe erstellen.
#
# -f bedeutet:
# Kein Fehler, wenn die Gruppe bereits existiert.
groupadd -f mini-siem


# Benutzer vagrant zur Gruppe mini-siem hinzufügen.
#
# Dadurch darf der Analyzer später die zentralen Logs lesen.
usermod -aG mini-siem vagrant


# ============================================================
# REMOTE LOG VERZEICHNIS
# ============================================================

# Hauptverzeichnis für zentral empfangene Logs erstellen.
mkdir -p /var/log/remote

# Besitzer:
#
# Benutzer = root
# Gruppe   = mini-siem
chown root:mini-siem /var/log/remote

# Rechte:
#
# root       = rwx
# mini-siem  = r-x
# andere     = ---
chmod 750 /var/log/remote


# ============================================================
# MINI-SIEM ALERT VERZEICHNIS
# ============================================================

# Verzeichnis für erkannte Security Alerts erstellen.
mkdir -p /var/log/mini-siem

# Der Benutzer vagrant führt unseren Python Analyzer aus.
# Deshalb darf er hier schreiben.
chown vagrant:vagrant /var/log/mini-siem

# Nur vagrant und seine Gruppe erhalten Zugriff.
chmod 750 /var/log/mini-siem


# ============================================================
# RSYSLOG
# ============================================================

# rsyslog beim Systemstart automatisch starten.
systemctl enable rsyslog

# rsyslog neu starten.
systemctl restart rsyslog


echo "[INFO] mini-siem provisioning completed."
