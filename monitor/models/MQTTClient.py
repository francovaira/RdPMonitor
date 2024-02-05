import paho.mqtt.client as mqtt
import threading
import queue
import time
import json
import traceback
import logging

class MQTTClient:
    def __init__(self, robotID, messageQueue):
        self.__robotID = robotID
        self.__msgQueue = messageQueue

    def createClient(self):
        mqttc = mqtt.Client()
        mqttc.on_message = self.on_message
        mqttc.on_connect = self.on_connect
        mqttc.on_publish = self.on_publish
        mqttc.on_subscribe = self.on_subscribe
        mqttc.on_disconnect = self.on_disconnect

        try:
            mqttc.connect("localhost", 1883, 60)
            mqttc.loop_start()
            mqttc.subscribe("/topic/robot", 0)
        except:
            print("No se pudo conectar al broker.")

        return mqttc

    def on_connect(self, mqttc, obj, flags, rc):
        pass

    def on_message(self, mqttc, obj, msg):
        print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
        self.__msgQueue.put(str(msg.topic))

    def on_publish(self, mqttc, obj, mid):
        pass

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")