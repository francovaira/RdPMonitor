import paho.mqtt.client as mqtt
import logging

class MQTTClient:
    def __init__(self, robotID, messageQueue):
        self.__robotID = robotID
        self.__msgQueue = messageQueue
        self.__topicRobotID = f'/topic/{robotID}'
        self.__topicPath = f'/topic/live/{robotID}'

    def createClient(self):
        mqttc = mqtt.Client()
        mqttc.on_connect = self.on_connect
        mqttc.on_publish = self.on_publish
        mqttc.on_subscribe = self.on_subscribe
        mqttc.on_disconnect = self.on_disconnect
        mqttc.message_callback_add(self.__topicRobotID, self.on_publish_common)
        # mqttc.on_message = self.on_message
        try:
            mqttc.connect('localhost', 1883, 60)
            mqttc.loop_start()
            mqttc.subscribe(self.__topicRobotID, 0)
        except:
            logging.error(f'[{__name__}] {self.__robotID} cant connect to the broker')

        return mqttc

    def on_connect(self, mqttc, obj, flags, rc):
        pass

    def on_publish_common(self, mqttc, obj, msg):
        if self.__robotID == str(msg.payload, 'utf-8'):
            mqttc.message_callback_add(self.__topicPath, self.on_robot_message)
            mqttc.subscribe(self.__topicPath, 0)

    def on_robot_message(self, mqttc, obj, msg):
        logging.debug(f'[{__name__}] {self.__robotID} confirmation recived')
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