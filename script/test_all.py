#!/usr/bin/python3

import os
from subprocess import run

def test(path, name):
	print("\n*** %s TEST ***" % name)
	if run(["python3", path]).returncode == 0:
		print("*** PASSED ***\n")
		return True
	else:
		print("!!! FAILED !!!\n")
		return False

tests = [("./script/test_%s.py" % t, t.upper()) for t in ["ca", "mqtt", "ca_mqtt_gw"]]

if all([test(p, n) for p, n in tests]):
	print("\n*** ALL TESTS PASSED ***")
	exit(0)
else:
	print("\n!!! SOME TESTS FAILED !!!")
	exit(1)
