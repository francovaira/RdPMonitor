import paho.mqtt.client as mqtt
import logging

class MQTTClient:
    def __init__(self, robotID, messageQueue):
        self.__robotID = robotID
        self.__msgQueue = messageQueue
        self.__topicRobotID = None

    def createClient(self):
        mqttc = mqtt.Client()
        mqttc.on_connect = self.on_connect
        mqttc.on_publish = self.on_publish
        mqttc.on_subscribe = self.on_subscribe
        mqttc.on_disconnect = self.on_disconnect
        mqttc.message_callback_add('/topic/robot', self.on_publish_common)
        # mqttc.on_message = self.on_message
        try:
            mqttc.connect('localhost', 1883, 60)
            mqttc.loop_start()
            mqttc.subscribe('/topic/robot', 0)
        except:
            logging.error('No se pudo conectar al broker')

        return mqttc

    def on_connect(self, mqttc, obj, flags, rc):
        pass

    def on_publish_common(self, mqttc, obj, msg):
        if self.__robotID == str(msg.payload, 'utf-8'):
            self.__topicRobotID = f'/topic/{self.__robotID}'
            mqttc.subscribe(self.__topicRobotID, 0)
            mqttc.message_callback_add(self.__topicRobotID, self.on_robot_message)
            mqttc.unsubscribe('/topic/robot')

    def on_robot_message(self, mqttc, obj, msg):
        print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
        self.__msgQueue.put(str(msg.topic))

    # def on_message(self, mqttc, obj, msg):
    #     print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
    #     self.__msgQueue.put(str(msg.topic))

    def on_publish(self, mqttc, obj, mid):
        pass

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_disconnect(self, client, userdata, rc):
        # if rc != 0:
        print("Unexpected disconnection.")