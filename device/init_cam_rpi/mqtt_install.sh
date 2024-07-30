#!/bin/bash

apt install -y mosquitto mosquitto-clients
systemctl enable mosquitto.service
mosquitto -v
pip install paho-mqtt