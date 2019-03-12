#!/bin/bash

source venv2/bin/activate
pip2 install -r ./ca_mqtt_gw/requirements.txt
deactivate

source venv3/bin/activate
pip3 install numpy paho-mqtt pyepics
deactivate
