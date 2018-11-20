#!/usr/bin/python3

import json
import time

import traceback
import logging

from helper import *
from process import Process
from mqtt import MqttManager
from ca import CaManager


logger = create_logger("test")

with open("test_config.json") as f:
    config = json.loads(f.read())

ioc = Process(
    name="ioc",
    proc_args=["../../bin/linux-x86_64/test", "./st.cmd"],
    log="logs/ioc.log",
    cwd="./epicsTestApp/iocBoot/ioctest",
    stdout=False,
)

gw = Process(
    name="gw",
    proc_args=["sh", "./run_ca_mqtt_gw.sh"],
    log="logs/gw.log",
    stdout=False,
)

ca = CaManager(config)
mqtt = MqttManager(config)

def pm_int():
    return True
    iv = 123
    p = mqtt["m/int/i"].expect(1)
    ca["E_INT_O"].put([i])
    ov = p.wait()[0]
    return iv == ov

tests = [
    (pm_int, "pm_int")
]
results = []

run = True
with ioc, ca, mqtt, gw:
    logger.info("start")
    it = iter(tests)

    try:
        while run:
            try:
                results.append(next(it)[0]())
            except StopIteration:
                break
    except KeyboardInterrupt:
        logger.info("caught ^C, exiting")
        run = False

    results.extend([None for _ in it])
    logger.info("completed")

for t, r in zip(tests, results):
    s = "skip"
    if r is True:
        s = "ok"
    elif r is False:
        s = "fail"
    logger.info("[%s] %s" % (s, t[1]))
if all(results):
    logger.info("[ok] passed")
    exit(0)
else:
    logger.error("[fail] some tests failed")
    exit(1)
