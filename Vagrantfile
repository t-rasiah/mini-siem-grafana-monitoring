Vagrant.configure("2") do |config|

  # ============================================
  # Gemeinsame Konfiguration
  # ============================================

  # Debian als Basisbetriebssystem
  config.vm.box = "debian/bookworm64"


  # ============================================
  # VM 1: Mini-SIEM Server
  # ============================================

  config.vm.define "projekt-mini-siem" do |siem|

    siem.vm.hostname = "projekt-mini-siem"

    # Internes Lab-Netzwerk
    siem.vm.network "private_network",
      ip: "192.168.56.10"

    # VirtualBox Ressourcen
    siem.vm.provider "virtualbox" do |vb|
      vb.name = "projekt-mini-siem"
      vb.memory = 2048
      vb.cpus = 2
    end

    # Basis-Provisionierung des Mini-SIEM
    siem.vm.provision "shell", path: "provision/siem.sh"

    # rsyslog-Serverkonfiguration übertragen
    siem.vm.provision "file",
      source: "config/rsyslog-server.conf",
      destination: "/tmp/rsyslog-server.conf"

    siem.vm.provision "shell", inline: <<-SHELL
      sudo cp /tmp/rsyslog-server.conf /etc/rsyslog.d/10-remote.conf
      sudo systemctl restart rsyslog
    SHELL

    # Monitoring-Komponenten installieren
    # Zuerst Loki, später zusätzlich Alloy und Grafana
    siem.vm.provision "shell", path: "provision/monitoring.sh"

  end


  # ============================================
  # VM 2: Log Client
  # ============================================

  config.vm.define "projekt-log-client" do |client|

    client.vm.hostname = "projekt-log-client"

    # Internes Lab-Netzwerk
    client.vm.network "private_network",
      ip: "192.168.56.20"

    # VirtualBox Ressourcen
    client.vm.provider "virtualbox" do |vb|
      vb.name = "projekt-log-client"
      vb.memory = 1024
      vb.cpus = 1
    end

    # Basis-Provisionierung des Log-Clients
    client.vm.provision "shell", path: "provision/log-client.sh"

    # rsyslog-Clientkonfiguration übertragen
    client.vm.provision "file",
      source: "config/rsyslog-client.conf",
      destination: "/tmp/rsyslog-client.conf"

    client.vm.provision "shell", inline: <<-SHELL
      sudo cp /tmp/rsyslog-client.conf /etc/rsyslog.d/90-forward.conf
      sudo systemctl restart rsyslog
    SHELL

  end

end