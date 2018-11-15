from subprocess import Popen

proc_ioc = Popen(
	["../../bin/linux-x86_64/test", "./st.cmd"],
	cwd="./epicsTestApp/iocBoot/ioctest",
)

proc_gw = Popen(["sh", "./run_ca_mqtt_gw.sh"])

proc_gw.wait()
proc_ioc.wait()
