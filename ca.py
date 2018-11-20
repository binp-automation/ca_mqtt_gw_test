import epics

from helper import *
from proto import Client, Manager

logger = create_logger("ca", stdout=False)

class CaClient(Client):
    def __init__(self, config):
        super().__init__(config, config["pv"])
        self.pv = epics.pv.PV(
            self.name, 
            callback=self.on_value_change,
            connection_callback=self.on_connect,
            auto_monitor=epics.dbr.DBE_VALUE
        )
        logger.info("%s: init" % self.name)

    def drop(self, *args):
        self.pv.disconnect()

    @hook(logger)
    def on_connect(self, *args, **kwargs):
        conn = kwargs["conn"]
        if conn:
            self.ready = True
        logger.info("%s .on_connect(conn=%s)" % (self.name, conn))

    @hook(logger)
    def on_value_change(self, *args, **kwargs):
        logger.info("%s .on_value_change(%s)" % (self.name, kwargs["value"]))

class CaManager(Manager):
    def __init__(self, config):
        super().__init__(config)
        logger.info("init")

    def create_client(self, config):
        return CaClient(config)

    def enter(self):
        logger.info("enter")

    def exit(self, *args):
        logger.info("exit")
