#!/usr/bin/python3

import json
from subprocess import Popen
import mqtt_client as mqtt

with open("test_config.json") as f:
	config = json.loads(f.read())

proc_ioc = Popen(
	["../../bin/linux-x86_64/test", "./st.cmd"],
	cwd="./epicsTestApp/iocBoot/ioctest",
)

proc_gw = Popen(["sh", "./run_ca_mqtt_gw.sh"])

mqtt.start(config)

proc_gw.wait()
proc_ioc.wait()
mqtt.stop()
