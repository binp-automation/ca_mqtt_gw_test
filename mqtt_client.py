import time
import paho.mqtt.client as mqtt
import traceback
import logging

logger = logging.getLogger("mqtt")

def hook(func):
    def deco(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except:
            logger.error(traceback.format_exc())
    return deco

class MqttClient:
    def __init__(self, config):
        self.config = config
        self.name = config["mqtt"]
        self.d = config["direction"]

        self.mqtt = mqtt.Client(self.name)
        self.ready = False

class MqttSender(MqttClient):
    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_publish = self.on_publish

    @hook
    def on_connect(self, *args):
        logger.debug("%s .on_connect(rc=%s)" % (self.name, args[-1]))
        self.ready = True

    @hook
    def on_publish(self, *args):
        logger.debug("%s .on_publish(%s)" % (self.name, args))

class MqttReceiver(MqttClient):
    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_subscribe = self.on_subscribe
        self.mqtt.on_message = self.on_message

    @hook
    def on_connect(self, *args):
        logger.debug("%s .on_connect(rc=%s)" % (self.name, args[-1]))
        self.mqtt.subscribe(self.config["mqtt"])

    @hook
    def on_subscribe(self, *args):
        logger.debug("%s .on_subscribe()" % self.name)
        self.ready = True

    @hook
    def on_message(self, *args):
        msg = args[-1]
        logger.debug("%s .on_message(%s, %s)" % (self.name, msg.topic, msg.payload))

class MqttTest:
    def __init__(self, config):
        self.clients = {}
        self.config = config

        logger.info("init")

    def __enter__(self):
        logger.info("enter")
        for conn in self.config["connections"]:
            d = conn["direction"]
            if d == "pm":
                client = MqttReceiver(conn)
            elif d == "mp":
                client = MqttSender(conn)
            else:
                logger.error("%s: unknown direction: %s" % (self.name, self.d))
            client.mqtt.connect(self.config["mqtt_broker_address"])
            client.mqtt.loop_start()
            self.clients[conn["mqtt"]] = client
        while any([not c.ready for c in self.clients.values()]):
            time.sleep(0.1)
            logger.debug("sleep")

    def __exit__(self, *args):
        logger.info("exit")
        for client in self.clients.values():
            client.mqtt.disconnect()
            client.mqtt.loop_stop()
        self.clients = {}
