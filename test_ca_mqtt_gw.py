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
    proc_kwargs={
        "cwd": "./epicsTestApp/iocBoot/ioctest",
    },
    log="logs/ioc.log",
    stdout_print=False,
)

gw = Process(
    name="gw",
    proc_args=["../venv2.7/bin/python", "ca_mqtt_gw/ca_mqtt_gw.py", "test_config.json"],
    #must_kill=True,
    log="logs/gw.log",
    stdout_print=False,
)

ca = CaManager(config)
mqtt = MqttManager(config)

def scal_test(src, dst, ivs):
    dst.clear()
    for iv in ivs:
        src.send(iv)
    ovs = []
    for j in range(len(ivs)):
        try:
            ovs.append(dst.receive(timeout=5.0))
        except TimeoutError:
            return (
                False, 
                "\n".join([
                    "dst.receive() timeout at j == %s" % j,
                    "ivs: %s" % repr(ivs),
                    "ovs: %s" % repr(ovs),
                ])
            )
    if len(ivs) != len(ovs):
        return (
            False, 
            "\n".join([
                "Input and output length mismatch: %s != %s" % (len(ivs), len(ovs)),
                "ivs: %s" % repr(ivs),
                "ovs: %s" % repr(ovs),
            ])
        )
    match = [iv == ov for iv, ov in zip(ivs, ovs)]
    desc = "\n".join(["%s %s= %s" % (repr(iv), "!="[int(m)], repr(ov)) for m, iv, ov in zip(match, ivs, ovs)])
    return (all(match), desc)

def pm_int():
    return scal_test(
        ca["E_INT_O"],
        mqtt["m/int/i"],
        [0, 1, 1, 42, -1, -123, 0x7FFFFFFF, -0x80000000],
    )

def mp_int():
    return scal_test(
        mqtt["m/int/o"],
        ca["E_INT_I"],
        [0, 1, 1, 42, -1, -123, 0x7FFFFFFF, -0x80000000],
    )

def pm_str():
    return scal_test(
        ca["E_STR_O"],
        mqtt["m/str/i"],
        ["", "", "abcdef", "абвгдеё", "您好", "a b", "a ", "\n\t\r"],
    )

def mp_str():
    return scal_test(
        mqtt["m/str/o"],
        ca["E_STR_I"],
        ["", "", "abcdef", "абвгдеё", "您好", "a b", "a ", "\n\t\r"],
    )

tests = [
    (pm_int, "pm_int"),
    (mp_int, "mp_int"),
    (pm_str, "pm_str"),
    (mp_str, "mp_str"),
]
results = []

run = True
with ioc, ca, mqtt, gw:
    time.sleep(1.0)
    logger.info("start")
    it = iter(tests)
    try:
        while run:
            try:
                fn, fname = next(it)
            except StopIteration:
                break
            r = fn()
            results.append(r)
            s = ("fail", "ok")[int(r[0])]
            logger.info("[%s] %s:\n\t%s" % (s, fname, r[1].replace("\n", "\n\t")))

    except KeyboardInterrupt:
        logger.info("caught ^C, exiting")
        run = False

    for fn, fname in tests[len(results):]:
        logger.info("[skip] %s" % fname)
        results.append((None, ""))

    logger.info("completed")

if all(list(zip(*results))[0]):
    logger.info("[ok] passed")
    exit(0)
else:
    logger.error("[fail] some tests failed")
    exit(1)
