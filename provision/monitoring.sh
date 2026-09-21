#!/bin/bash
set -e

echo "[INFO] Provisioning Monitoring-Komponenten..."

# ============================================================
# Voraussetzungen
# ============================================================

apt-get update

apt-get install -y \
    wget \
    gpg \
    ca-certificates \
    acl

# ============================================================
# Offizielles Grafana-APT-Repository
# ============================================================

mkdir -p /etc/apt/keyrings

wget -q -O /etc/apt/keyrings/grafana.asc \
    https://apt.grafana.com/gpg-full.key

chmod 644 /etc/apt/keyrings/grafana.asc

echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" \
    > /etc/apt/sources.list.d/grafana.list

apt-get update

# ============================================================
# Loki
# ============================================================

echo "[INFO] Installiere Loki..."

apt-get install -y loki

systemctl enable loki
systemctl restart loki

# ============================================================
# Grafana Alloy
# ============================================================

echo "[INFO] Installiere Grafana Alloy..."

apt-get install -y alloy

# Alloy-Konfiguration aus dem Repository übernehmen.
cp /vagrant/config/alloy/config.alloy \
    /etc/alloy/config.alloy

chown root:alloy /etc/alloy/config.alloy
chmod 640 /etc/alloy/config.alloy

# ============================================================
# Mini-SIEM Alert-Datei vorbereiten
# ============================================================

mkdir -p /var/log/mini-siem
touch /var/log/mini-siem/alerts.log

chown vagrant:vagrant /var/log/mini-siem/alerts.log
chmod 640 /var/log/mini-siem/alerts.log

# ============================================================
# Berechtigungen für Grafana Alloy
# ============================================================

setfacl -m u:alloy:rx /var/log/mini-siem
setfacl -m u:alloy:r /var/log/mini-siem/alerts.log
setfacl -d -m u:alloy:rX /var/log/mini-siem

# ============================================================
# Alloy starten
# ============================================================

systemctl enable alloy
systemctl restart alloy

# ============================================================
# Grafana
# ============================================================

echo "[INFO] Installiere Grafana..."

apt-get install -y grafana

# ============================================================
# Grafana - Loki Data Source
# ============================================================

mkdir -p /etc/grafana/provisioning/datasources

cp \
    /vagrant/config/grafana/provisioning/datasources/loki.yml \
    /etc/grafana/provisioning/datasources/loki.yml

chown root:grafana \
    /etc/grafana/provisioning/datasources/loki.yml

chmod 640 \
    /etc/grafana/provisioning/datasources/loki.yml

# ============================================================
# Grafana - Dashboard Provisioning
# ============================================================

mkdir -p /etc/grafana/provisioning/dashboards
mkdir -p /var/lib/grafana/dashboards

# Dashboard-Provider installieren.
cp \
    /vagrant/config/grafana/provisioning/dashboards/mini-siem.yml \
    /etc/grafana/provisioning/dashboards/mini-siem.yml

chown root:grafana \
    /etc/grafana/provisioning/dashboards/mini-siem.yml

chmod 640 \
    /etc/grafana/provisioning/dashboards/mini-siem.yml

# Mini-SIEM-Dashboard installieren.
cp \
    /vagrant/config/grafana/dashboards/mini-siem-security-monitoring.json \
    /var/lib/grafana/dashboards/mini-siem-security-monitoring.json

chown grafana:grafana \
    /var/lib/grafana/dashboards/mini-siem-security-monitoring.json

chmod 640 \
    /var/lib/grafana/dashboards/mini-siem-security-monitoring.json

# ============================================================
# Grafana starten
# ============================================================

systemctl enable grafana-server
systemctl restart grafana-server

echo "[INFO] Monitoring-Komponenten wurden erfolgreich eingerichtet."