import paho.mqtt.client as mqtt
import logging

class MQTTClient:
    def __init__(self, robotID, robotFeedbackQueue):
        self.__robotID = robotID
        self.__robotFeedbackQueue = robotFeedbackQueue
        self.__topicRobotID = f'/topic/{robotID}'
        self.__topicFeedbackRobot = f'/topic/live/{robotID}'
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
            mqttc.message_callback_add(self.__topicFeedbackRobot, self.on_robot_feedback_message)
            mqttc.subscribe(self.__topicFeedbackRobot, 0)

    def on_robot_feedback_message(self, mqttc, obj, msg):
        feedback_received = str(msg.payload, 'utf-8')
        logging.debug(f'[{__name__}] {self.__robotID} setpoint confirmation recived | <{feedback_received}>')
        self.__robotFeedbackQueue.put(feedback_received)

    # def on_message(self, mqttc, obj, msg):
    #     print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
    #     self.__robotFeedbackQueue.put(str(msg.topic))

    def on_publish(self, mqttc, obj, mid):
        logging.debug(f'[{__name__}] {self.__robotID} velocities sent')

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        logging.debug(f'[{__name__}] {self.__robotID} subscribed')

    def on_disconnect(self, client, userdata, rc):
        logging.warning(f'[{__name__}] {self.__robotID} unexpected disconnection')