#!/usr/bin/python3

import os
from subprocess import run

def check(result):
	if result.returncode == 0:
		print("*** PASSED ***\n")
		return True
	else:
		print("!!! FAILED !!!\n")
		return False

def unittest():
	print("\n*** UNITTEST ***")
	return check(run(["bash", "-c", "./script/unittest.sh"]))

def test(path, name):
	print("\n*** %s TEST ***" % name)
	return check(run(["python3", path]))

tests = [("./script/test_%s.py" % t, t.upper()) for t in ["ca", "mqtt", "ca_mqtt_gw"]]

if all([unittest()] + [test(p, n) for p, n in tests]):
	print("\n*** ALL TESTS PASSED ***")
	exit(0)
else:
	print("\n!!! SOME TESTS FAILED !!!")
	exit(1)
