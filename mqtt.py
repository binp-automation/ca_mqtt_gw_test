import paho.mqtt.client as mqtt
import traceback
import logging

from helper import *
from proto import Client, Manager

logger = create_logger("mqtt", stdout=False)

class MqttClient(Client):
    def __init__(self, config):
        super().__init__(config, config["mqtt"])
        self.mqtt = mqtt.Client(self.name)

    def connect(self, broker):
        self.mqtt.connect(broker)
        self.mqtt.loop_start()

    def drop(self):
        self.mqtt.disconnect()
        self.mqtt.loop_stop()

class MqttSender(MqttClient):
    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_publish = self.on_publish

    @hook(logger)
    def on_connect(self, *args):
        logger.info("%s .on_connect(rc=%s)" % (self.name, args[-1]))
        self.ready = True

    @hook(logger)
    def on_publish(self, *args):
        logger.info("%s .on_publish(%s)" % (self.name, args))

class MqttReceiver(MqttClient):
    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_subscribe = self.on_subscribe
        self.mqtt.on_message = self.on_message

    @hook(logger)
    def on_connect(self, *args):
        logger.info("%s .on_connect(rc=%s)" % (self.name, args[-1]))
        sub = self.config["mqtt"]
        if self.config["datatype"].startswith("wf"):
            if not sub.endswith("/"):
                sub += "/"
            sub += "#"
        logger.info("%s .subscribe(%s)" % (self.name, sub))
        self.mqtt.subscribe(sub)

    @hook(logger)
    def on_subscribe(self, *args):
        logger.info("%s .on_subscribe()" % self.name)
        self.ready = True

    @hook(logger)
    def on_message(self, *args):
        msg = args[-1]
        logger.info("%s .on_message(%s, %s)" % (self.name, msg.topic, msg.payload))

class MqttManager(Manager):
    def __init__(self, config):
        super().__init__(config)
        logger.info("init")

    def create_client(self, config):
        d = config["direction"]
        if d == "pm":
            client = MqttReceiver(config)
        elif d == "mp":
            client = MqttSender(config)
        else:
            msg = "%s: unknown direction: %s" % (self.name, self.d)
            logger.error(msg)
            raise Exception(msg)

        client.connect(self.config["mqtt_broker_address"])
        return client

    def enter(self):
        logger.info("enter")

    def exit(self, *args):
        logger.info("exit")
