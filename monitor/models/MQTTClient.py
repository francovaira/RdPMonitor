import paho.mqtt.client as mqtt
import logging

class MQTTClient:
    def __init__(self, robotID, messageQueue):
        self.__robotID = robotID
        self.__msgQueue = messageQueue
        self.__topicRobotID = f'/topic/{robotID}'
        self.__topicPath = f'/topic/live/{robotID}'
        self.mqttc = mqtt.Client()

        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.message_callback_add(self.__topicRobotID, self.on_publish_common)
        # self.mqttc.on_message = self.on_message
        try:
            self.mqttc.connect('localhost', 1883, 60)
            self.mqttc.loop_start()
            self.mqttc.subscribe(self.__topicRobotID, 0)
        except:
            logging.error(f'[{__name__}] {self.__robotID} cant connect to the broker')

    def getClient(self):
        return self.mqttc

    def on_connect(self, mqttc, obj, flags, rc):
        pass

    def on_publish_common(self, mqttc, obj, msg):
        if self.__robotID == str(msg.payload, 'utf-8'):
            mqttc.message_callback_add(self.__topicPath, self.on_robot_message)
            mqttc.subscribe(self.__topicPath, 0)

    def on_robot_message(self, mqttc, obj, msg):
        logging.debug(f'[{__name__}] {self.__robotID} setpoint confirmation recived')
        self.__msgQueue.put(str(msg.topic))

    # def on_message(self, mqttc, obj, msg):
    #     print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
    #     self.__msgQueue.put(str(msg.topic))

    def on_publish(self, mqttc, obj, mid):
        logging.debug(f'[{__name__}] {self.__robotID} velocities sent')

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        logging.debug(f'[{__name__}] {self.__robotID} subscribed')

    def on_disconnect(self, client, userdata, rc):
        logging.warning(f'[{__name__}] {self.__robotID} unexpected disconnection')