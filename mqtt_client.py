import paho.mqtt.client as mqtt


def on_message(mc, _, msg):
    print("message: %s: %s" % (msg.topic, msg.payload))
    if msg.topic == topic and msg.payload == payload:
        global passed
        passed = True
    mc.disconnect()

class MqttClient(mqtt.Client):
    def __init__(self, config):
        super().__init__(config["mqtt"])
        self.config = config

        for attr in ["on_connect", "on_disconnect", "on_message", "on_publish", "on_subscribe", "on_unsubscribe"]:
            def callback(*args, attr=attr):
                print("%s: %s: %s" % (name, attr, args[1:]))
                getattr(self, "_" + attr)(*args);
            setattr(self, attr, callback)

    def _on_connect(self, *args):
        d = self.config["direction"]
        if d == "pm":
            self.subscribe(self.config["mqtt"])
        elif d == "mp":
            if self.config["datatype"] == "int":
                self.publish(self.config["mqtt"], b"0123")
        else:
            raise Exception("unknown direction: " % d)

    def _on_disconnect(self, *args):
        pass

    def _on_message(self, *args):
        pass

    def _on_publish(self, *args):
        pass

    def _on_subscribe(self, *args):
        pass

    def _on_unsubscribe(self, *args):
        pass

mqttcs = {}

def start(config):
    for conn in config["connections"]:
        mqttc = MqttClient(conn)
        mqttc.connect(config["mqtt_broker_address"])
        mqttc.loop_start()
        mqttcs[conn["mqtt"]] = mqttc

def stop():
    for mqttc in mqttcs.values():
        mqttc.loop_stop()
