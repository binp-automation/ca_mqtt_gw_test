#!/usr/bin/python3

# simple mqtt test
# you need to have some mqtt broker (e.g. mosquitto) running on localhost
# also you heed to have paho.mqtt python package installed

from threading import Thread
import paho.mqtt.client as mqtt

from lib.process import Process

mosquitto = Process(
    name="mosquitto",
    proc_args=["./mosquitto/src/mosquitto"],
    log="logs/mosquitto.log",
    stdout_print=False,
)

topic = "hello"
payload = "Hello, MQTT!".encode("utf-8")

passed = False

def create_mqttc(name, **kwargs):
    mqttc = mqtt.Client(name)
    for attr in ["on_connect", "on_disconnect", "on_message", "on_publish", "on_subscribe", "on_unsubscribe"]:
        def callback(*args, attr=attr, cb=kwargs.get(attr, None)):
            print("%s: %s: %s" % (name, attr, args[1:]))
            if cb is not None:
                cb(*args)
        setattr(mqttc, attr, callback)
    return mqttc

def send():
    mqttc = create_mqttc(
        "sender",
        on_connect=lambda mc, *args: mc.publish(topic, payload, qos=2),
        on_publish=lambda mc, *args: mc.disconnect(),
    )
    mqttc.connect("localhost")
    mqttc.loop_forever()

def receive():
    def on_message(mc, _, msg):
        print("message: %s: %s" % (msg.topic, msg.payload))
        if msg.topic == topic and msg.payload == payload:
            global passed
            passed = True
        mc.disconnect()

    sender_thread = Thread(target=send)
    mqttc = create_mqttc(
        "receiver",
        on_connect=lambda mc, *args: mc.subscribe(topic, qos=2),
        on_subscribe=lambda *args: sender_thread.start(),
        on_message=on_message,
    )
    mqttc.connect("localhost")
    mqttc.loop_forever()
    sender_thread.join()

with mosquitto:
    receiver_thread = Thread(target=receive)
    receiver_thread.start()
    receiver_thread.join()

    if passed:
        print("[ok] test passed")
        exit(0)
    else:
        print("[error] test failed")
        exit(1)
