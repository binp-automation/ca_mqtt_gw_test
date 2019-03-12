#!/usr/bin/python3

import json
import time
import numpy as np

import traceback
import logging

from lib.helper import *
from lib.process import Process
from lib.mqtt import MqttManager
from lib.ca import CaManager


logger = create_logger("test")

with open("./config/ca_mqtt_gw.json") as f:
    config = json.loads(f.read())

mosquitto = Process(
    name="mosquitto",
    proc_args=["./mosquitto/src/mosquitto"],
    log="logs/mosquitto.log",
    stdout_print=False,
)

repeater = Process(
    name="repeater",
    proc_args=["caRepeater"],
    log="logs/repeater.log",
    stdout_print=False,
)

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
    proc_args=["./venv2/bin/python", "ca_mqtt_gw/ca_mqtt_gw.py", "./config/ca_mqtt_gw.json"],
    #must_kill=True,
    log="logs/gw.log",
    stdout_print=False,
)

ca = CaManager(config)
mqtt = MqttManager(config)

def test_seq(src, dst, ivs, rvs=None, cmp=lambda a, b: a == b):
    dst.clear()
    for iv in ivs:
        src.send(iv)
    if rvs is None:
        rvs = ivs
    ovs = []
    for j in range(len(rvs)):
        try:
            ovs.append(dst.receive(timeout=10.0))
        except TimeoutError:
            return (
                False, 
                "\n".join([
                    "dst.receive() timeout at j == %s" % j,
                    "rvs: %s" % repr(rvs),
                    "ovs: %s" % repr(ovs),
                ])
            )
    if len(rvs) != len(ovs):
        return (
            False, 
            "\n".join([
                "Input and output length mismatch: %s != %s" % (len(rvs), len(ovs)),
                "rvs: %s" % repr(rvs),
                "ovs: %s" % repr(ovs),
            ])
        )
    match = [cmp(iv, ov) for iv, ov in zip(rvs, ovs)]
    desc = "\n".join(["%s %s= %s" % (repr(iv), "!="[int(m)], repr(ov)) for m, iv, ov in zip(match, rvs, ovs)])
    return (all(match), desc)

tests = []
iwfid = 1
owfid = 1

def test(fn):
    tests.append(fn)
    return fn

@test
def pm_int():
    return test_seq(
        ca["E_INT_O"],
        mqtt["m/int/i"],
        [0, 1, 1, 42, -1, -123, 0x7FFFFFFF, -0x80000000],
    )

@test
def mp_int():
    return test_seq(
        mqtt["m/int/o"],
        ca["E_INT_I"],
        [0, 1, 1, 42, -1, -123, 0x7FFFFFFF, -0x80000000],
    )

@test
def pm_str():
    return test_seq(
        ca["E_STR_O"],
        mqtt["m/str/i"],
        ["", "", "abcdef", "абвгдеё", "您好"],
    )

@test
def mp_str():
    return test_seq(
        mqtt["m/str/o"],
        ca["E_STR_I"],
        ["", "", "abcdef", "абвгдеё", "您好"],
    )

@test
def pm_str_ws():
    return test_seq(
        ca["E_STR_O"],
        mqtt["m/str/i"],
        [" a", "a b", "a ", " ", "\n\t\r"],
    )

@test
def mp_str_ws():
    return test_seq(
        mqtt["m/str/o"],
        ca["E_STR_I"],
        [" a", "a b"] #, "a ", " ", "\n\t\r"],
        # TODO: fix whitespace loss
    )

@test
def pm_wf():
    global iwfid
    res = test_seq(
        ca["E_WAVE_O"],
        mqtt["m/wave/i/"],
        [np.arange(10)],
        [(0, np.concatenate(([iwfid, 10], np.arange(10))))],
        cmp=lambda a, b: a[0] == b[0] and np.array_equal(a[1], b[1]),
    )
    iwfid += 1
    return res

@test
def mp_wf():
    global owfid
    res = test_seq(
        mqtt["m/wave/o/"],
        ca["E_WAVE_I"],
        [(0, np.concatenate(([owfid, 10], np.arange(10))))],
        [np.arange(10)],
        cmp=lambda a, b: np.array_equal(a, b)
    )
    owfid += 1
    return res

@test
def pm_wf_l():
    global iwfid
    res = test_seq(
        ca["E_WAVE_O"],
        mqtt["m/wave/i/"],
        [np.arange(600)],
        [
            (0, np.concatenate(([iwfid, 600], np.arange(0, 300)))),
            (1, np.concatenate(([iwfid, 600], np.arange(300, 600)))),
        ],
        cmp=lambda a, b: a[0] == b[0] and np.array_equal(a[1], b[1]),
    )
    iwfid += 1
    return res

@test
def mp_wf_l():
    global owfid
    res = test_seq(
        mqtt["m/wave/o/"],
        ca["E_WAVE_I"],
        [
            (0, np.concatenate(([owfid, 600], np.arange(0, 300)))),
            (1, np.concatenate(([owfid, 600], np.arange(300, 600)))),
        ],
        [np.arange(600)],
        cmp=lambda a, b: np.array_equal(a, b)
    )
    owfid += 1
    return res

@test
def mp_wf_cat():
    global owfid
    res = test_seq(
        mqtt["m/wave/o/"],
        ca["E_WAVE_I"],
        [
            (0, np.concatenate(([owfid, 20], np.arange(0, 10)))),
            (1, np.concatenate(([owfid, 20], np.arange(10, 20)))),
        ],
        [np.arange(20)],
        cmp=lambda a, b: np.array_equal(a, b)
    )
    owfid += 1
    return res

@test
def mp_wf_1212():
    global owfid
    res = test_seq(
        mqtt["m/wave/o/"],
        ca["E_WAVE_I"],
        [
            (0, np.concatenate(([owfid, 20], np.arange(0, 10)))),
            (0, np.concatenate(([owfid + 1, 20], np.arange(-20, -10)))),
            (1, np.concatenate(([owfid, 20], np.arange(10, 20)))),
            (1, np.concatenate(([owfid + 1, 20], np.arange(-10, 0)))),
        ],
        [np.arange(20), np.arange(-20, 0)],
        cmp=lambda a, b: np.array_equal(a, b)
    )
    owfid += 2
    return res

@test
def mp_wf_1221():
    global owfid
    res = test_seq(
        mqtt["m/wave/o/"],
        ca["E_WAVE_I"],
        [
            (0, np.concatenate(([owfid, 20], np.arange(0, 10)))),
            (0, np.concatenate(([owfid + 1, 20], np.arange(-20, -10)))),
            (1, np.concatenate(([owfid + 1, 20], np.arange(-10, 0)))),
            (1, np.concatenate(([owfid, 20], np.arange(10, 20)))),
        ],
        [np.arange(-20, 0)],
        cmp=lambda a, b: np.array_equal(a, b)
    )
    owfid += 2
    return res

results = []

run = True
with mosquitto, repeater, ioc, ca, mqtt, gw:
    time.sleep(1.0)
    logger.info("start")
    it = iter(tests)
    try:
        while run:
            try:
                fn = next(it)
            except StopIteration:
                break
            r = fn()
            results.append(r)
            s = ("fail", "ok")[int(r[0])]
            logger.info("[%s] %s" % (s, fn.__name__))
            logger.debug("description:\n\t%s" % r[1].replace("\n", "\n\t"))

    except KeyboardInterrupt:
        logger.info("caught ^C, exiting")
        run = False

    for fn, fname in tests[len(results):]:
        logger.info("[skip] %s" % fname)
        results.append((None, ""))

    logger.info("completed")
    time.sleep(1.0)

if all(list(zip(*results))[0]):
    logger.info("[ok] all tests passed")
    exit(0)
else:
    logger.info("[fail] some tests failed")
    exit(1)
