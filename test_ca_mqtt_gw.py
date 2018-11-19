#!/usr/bin/python3

import json
import time
from threading import Thread
from subprocess import Popen, PIPE, STDOUT
from mqtt_client import MqttTest

import traceback
import logging

def create_logger(name, stdout=True, file=True, path=None, level=True):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if level:
        ln = "%(levelname)s: "
    else:
        ln = ""

    if stdout:
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(logging.Formatter("[%(name)s] " + ln + "%(message)s"))
        logger.addHandler(sh)

    if file:
        if path is None:
            path = "logs/%s.log" % name
        fh = logging.FileHandler(path, mode="w")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(ln + "%(message)s"))
        logger.addHandler(fh)

    return logger

logger = create_logger("test")

with open("test_config.json") as f:
    config = json.loads(f.read())

class Proc:
    def fpipe(self):
        for line in self.proc.stdout:
            self.logger.info(line.decode("utf-8").rstrip())
            self.logfile.write(line)

    def __init__(self, name, log, proc_args, stdout=False, **proc_kwargs):
        self.name = name
        self.log = log
        self.proc_args = proc_args
        self.proc_kwargs = proc_kwargs
        self.stdout = stdout

        self.logfile = None
        self.proc = None
        self.tpipe = None

        self.logger = create_logger(
            self.name, 
            file=False, 
            stdout=stdout,
            level=False,
        )

    def __enter__(self):
        self.logfile = open(self.log, "wb")
        self.proc = Popen(
            self.proc_args,
            **self.proc_kwargs,
            stdout=PIPE,
            stderr=STDOUT,
        )
        self.tpipe = Thread(target=self.fpipe)
        self.tpipe.start()

    def __exit__(self, *args):
        self.proc.terminate()
        self.proc.wait()
        self.tpipe.join()
        self.logfile.close()

ioc = Proc(
    name="ioc",
    proc_args=["../../bin/linux-x86_64/test", "./st.cmd"],
    log="logs/ioc.log",
    cwd="./epicsTestApp/iocBoot/ioctest",
    stdout=True,
)

gw = Proc(
    name="gw",
    proc_args=["sh", "./run_ca_mqtt_gw.sh"],
    log="logs/gw.log",
    stdout=True,
)

create_logger("mqtt")
mqtt = MqttTest(config)

run = True
with ioc, mqtt, gw:
    logger.info("[test] started")
    try:
        while run:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("[test] caught ^C, exiting")
        run = False

