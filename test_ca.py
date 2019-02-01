#!/usr/bin/python3

# CA (channel acces) simple test
# uses pyepics library

import numpy as np
import epics
import time

state = 0

values_old = {
	"E_INT_O": 0,
	"E_STR_O": "initial",
	"E_WAVE_O": np.zeros(100, dtype=np.int32),
}

values_new = {
	"E_INT_O": 1,
	"E_STR_O": "changed",
	"E_WAVE_O": np.arange(100, dtype=np.int32),
}

def test(val):
	if not val:
		raise Exception()

pvnames = ["E_INT_O", "E_STR_O", "E_WAVE_O"]
pvs = {}
for pvname in pvnames:
	def callback(*args, pvname=pvname, **kwargs):
		print("callback %s: %s, %s" % (pvname, args, kwargs))
		global state
		if state == 1:
			global values_old
			test(np.all(kwargs["value"] == values_old[pvname]))
		elif state == 2:
			global values_new
			test(np.all(kwargs["value"] == values_new[pvname]))

	pvs[pvname] = epics.pv.PV(pvname, callback=callback, auto_monitor=epics.dbr.DBE_VALUE)

state = 0
for pvname in pvnames:
	pvs[pvname].put(values_old[pvname], wait=True)
state = 1
for pvname in pvnames:
	pvs[pvname].put(values_old[pvname], wait=True)
for pvname in pvnames:
	test(np.all(pvs[pvname].get() == values_old[pvname]))

state = 2
for pvname in pvnames:
	pvs[pvname].put(values_new[pvname], wait=True)
for pvname in pvnames:
	test(np.all(pvs[pvname].get() == values_new[pvname]))

print("[ok] passed")
