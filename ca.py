import epics

from helper import *
from proto import Client, Manager

import logging

logger = create_logger("ca", level=logging.INFO)

class CaClient(Client):
    def __init__(self, config):
        super().__init__(config, config["pv"])
        self.pv = epics.pv.PV(
            self.name, 
            callback=self.on_value_change,
            connection_callback=self.on_connect,
            auto_monitor=epics.dbr.DBE_VALUE
        )
        logger.debug("%s: init" % self.name)

    def drop(self, *args):
        self.pv.disconnect()

    @hook(logger)
    def on_connect(self, *args, **kwargs):
        conn = kwargs["conn"]
        logger.debug("%s .on_connect(conn=%s)" % (self.name, conn))

    @hook(logger)
    def on_value_change(self, *args, **kwargs):
        value = kwargs["value"]
        if self.d == "mp":
            self.queue_recv(value)
        self.ready = True
        logger.debug("%s .on_value_change(%s)" % (self.name, repr(value)))

    def send(self, data):
        self.pv.put(data, wait=True, callback=self.on_put_complete)

    @hook(logger)
    def on_put_complete(self, *args, **kwargs):
        logger.debug("%s .on_put_complete" % (self.name))

class CaManager(Manager):
    def __init__(self, config):
        super().__init__(config)
        logger.debug("init")

    def create_client(self, config):
        return CaClient(config)

    def enter(self):
        logger.debug("enter")

    def exit(self, *args):
        logger.debug("exit")
