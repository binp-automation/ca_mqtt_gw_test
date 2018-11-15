#!/usr/bin/python3

####################
# WORK IN PROGRESS #
####################

import json
from threading import Thread
import paho.mqtt.client as mqtt


def create_mqttc(name, **kwargs):
    mqttc = mqtt.Client(name)
    for attr in ["on_connect", "on_disconnect", "on_message", "on_publish", "on_subscribe", "on_unsubscribe"]:
        def callback(*args, attr=attr, cb=kwargs.get(attr, None)):
            print("%s: %s: %s" % (name, attr, args[1:]))
            if cb is not None:
                cb(*args)
        setattr(mqttc, attr, callback)
    return mqttc

def thread_main():
    def on_message(mc, _, msg):
        print("message: %s: %s" % (msg.topic, msg.payload))
        mc.disconnect()

    mqttc = create_mqttc(
        "receiver",
        on_connect=lambda mc, *args: mc.subscribe(topic, qos=2),
        on_subscribe=lambda *args: sender_thread.start(),
        on_message=on_message,
    )
    mqttc.connect("localhost")
    mqttc.loop_forever()

def start(config_path):
    with open(config_path, "r") as f:
        config = json.loads(f.read())

    thread = Thread(target=thread_main)
    thread.start()
    thread.join()
