#!/bin/bash

# Bei einem Fehler soll das Provisioning sofort abbrechen.
set -e

echo "[INFO] Provisioning log-client..."


# ============================================================
# PAKETLISTEN AKTUALISIEREN
# ============================================================

apt-get update


# ============================================================
# BENÖTIGTE SOFTWARE INSTALLIEREN
# ============================================================

# openssh-server:
#   Erzeugt die SSH-Logs, die unser Mini-SIEM analysiert.
#
# rsyslog:
#   Sendet die Logs zentral an den mini-siem Server.
apt-get install -y \
    openssh-server \
    rsyslog


# ============================================================
# SSH TESTBENUTZER ERSTELLEN
# ============================================================

# Prüfen, ob der Benutzer testuser bereits existiert.
# Dadurch kann das Provisioning mehrfach ausgeführt werden,
# ohne jedes Mal einen Fehler zu verursachen.
if ! id "testuser" >/dev/null 2>&1; then

    # Benutzer mit Home-Verzeichnis und Bash erstellen.
    useradd \
        --create-home \
        --shell /bin/bash \
        testuser

fi


# ============================================================
# TESTPASSWORT SETZEN
# ============================================================

# Dieses Passwort ist ausschließlich für das isolierte
# Cyber-Security-Labor gedacht.
#
# WICHTIG:
# Niemals so in einer produktiven Umgebung verwenden.
echo "testuser:MiniSIEM-Test-2026!" | chpasswd


# ============================================================
# SSH PASSWORTAUTHENTIFIZIERUNG AKTIVIEREN
# ============================================================

# Debian/OpenSSH unterstützt Konfigurationsdateien unter
# /etc/ssh/sshd_config.d/.
#
# Wir legen eine eigene Datei an, anstatt die originale
# sshd_config direkt zu verändern.
cat > /etc/ssh/sshd_config.d/99-mini-siem-lab.conf <<EOF
PasswordAuthentication yes
PubkeyAuthentication yes
EOF


# ============================================================
# SSH KONFIGURATION PRÜFEN
# ============================================================

# sshd -t überprüft die Syntax.
# Bei einer ungültigen Konfiguration bricht das Script ab.
sshd -t


# ============================================================
# SSH STARTEN
# ============================================================

systemctl enable ssh
systemctl restart ssh


# ============================================================
# RSYSLOG STARTEN
# ============================================================

systemctl enable rsyslog
systemctl restart rsyslog


echo "[INFO] log-client provisioning completed."