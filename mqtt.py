import struct
import numpy as np
import paho.mqtt.client as mqtt
import traceback
import logging

from helper import *
from proto import Client, Manager

logger = create_logger("mqtt", level=logging.INFO)

def encode(value, dtype):
    if dtype == "int":
        payload = struct.pack(">i", value)
    elif dtype == "string":
        payload = value.encode("utf-8")
    elif dtype == "wfint":
        payload = value.astype(">i4").tobytes()
    else:
        msg = "unknown datatype: %s" % dtype
        logger.error(msg)
        raise Exception(msg)
    return payload

def decode(payload, dtype):
    if dtype == "int":
        value = struct.unpack(">i", payload)[0]
    elif dtype == "string":
        value = payload.decode("utf-8")
    elif dtype == "wfint":
        value = np.ndarray(shape=(-1,), dtype='>i4', buffer=payload).astype(np.int32)
    else:
        msg = "unknown datatype: %s" % dtype
        logger.error(msg)
        raise Exception(msg)
    return value

class MqttClient(Client):
    def __init__(self, config):
        super().__init__(config, config["mqtt"])
        self.mqtt = mqtt.Client(self.name)
        self.qos = config["qos"]
        self.dtype = config["datatype"]

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
        logger.debug("%s .on_connect(rc=%s)" % (self.name, args[-1]))
        self.ready = True

    @hook(logger)
    def on_publish(self, *args):
        logger.debug("%s .on_publish(mid=%s)" % (self.name, args[-1]))

    def send(self, data):
        topic = self.config["mqtt"]
        if self.dtype.startswith("wf"):
            idx, data = data
            if not topic.endswith("/"):
                topic += "/"
            topic += str(idx).zfill(3)
        payload = encode(data, self.dtype)
        mi = self.mqtt.publish(topic, payload, qos=self.qos)
        mi.wait_for_publish()
        logger.debug("%s .publish(%s, %s) -> (rc=%s, mid=%s)" % (self.name, topic, payload, mi.rc, mi.mid))

class MqttReceiver(MqttClient):
    def __init__(self, *args):
        super().__init__(*args)
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_subscribe = self.on_subscribe
        self.mqtt.on_message = self.on_message

    @hook(logger)
    def on_connect(self, *args):
        logger.debug("%s .on_connect(rc=%s)" % (self.name, args[-1]))
        topic = self.config["mqtt"]
        if self.config["datatype"].startswith("wf"):
            if not topic.endswith("/"):
                topic += "/"
            topic += "#"
        logger.debug("%s .subscribe(%s)" % (self.name, topic))
        self.mqtt.subscribe(topic, qos=self.qos)

    @hook(logger)
    def on_subscribe(self, *args):
        logger.debug("%s .on_subscribe()" % self.name)
        self.ready = True

    @hook(logger)
    def on_message(self, *args):
        msg = args[-1]
        logger.debug("%s : %s .on_message(%s, %s)" % (self.name, self.dtype, msg.topic, msg.payload))
        value = decode(msg.payload, self.dtype) 
        if self.dtype.startswith("wf"):
            try:
                idx = int(msg.topic.split("/")[-1])
            except ValueError:
                return
            self.queue_recv((idx, value))
        else:
            self.queue_recv(value)

class MqttManager(Manager):
    def __init__(self, config):
        super().__init__(config)
        logger.debug("init")

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
        logger.debug("enter")

    def exit(self, *args):
        logger.debug("exit")
