#!/bin/bash

echo("Instalando dependencias...")
echo("[ Mosquitto - VSFTPD")
apt-get install --yes mosquitto=2.0.11-1+deb11u1 \
                      vsftpd=3.0.3-12
echo("Configurando broker...")
cp mosquitto_valentin.conf /etc/mosquitto/valentin.conf
sed -i 's/mosquitto.conf/valentin.conf/g' /usr/lib/systemd/system/mosquitto.service
systemctl daemon-reload
systemctl restart mosquitto.service
