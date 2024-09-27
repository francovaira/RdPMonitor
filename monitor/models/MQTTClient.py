
import paho.mqtt.client as mqtt
import logging

class MQTTClient:
    def __init__(self, robotID, robotFeedbackQueue):
        self.__robotID = robotID
        self.__robotFeedbackQueue = robotFeedbackQueue
        self.__topicRegisterRobot = f'topic/register'
        self.__topicFeedbackRobot = f'topic/live/{robotID}'
        self.__mqttClient = mqtt.Client()

        # self.__mqttClient.on_message = self.on_message
        # self.__mqttClient.on_publish = self.on_publish
        self.__mqttClient.on_connect = self.on_connect
        self.__mqttClient.on_subscribe = self.on_subscribe
        self.__mqttClient.on_disconnect = self.on_disconnect

        self.__mqttClient.message_callback_add(self.__topicRegisterRobot, self.on_register_robot)

        try:
            # self.__mqttClient.connect('192.168.1.83', 1883, 60)
            self.__mqttClient.connect('127.0.0.1', 1883, 60)
            self.__mqttClient.loop_start()
            self.__mqttClient.subscribe(self.__topicRegisterRobot, 0)
        except:
            logging.error(f'[{__name__}] {self.__robotID} cant connect to the broker')

    def getClient(self):
        return self.__mqttClient

    def send_register_request(self):
        msg = self.__mqttClient.publish(self.__topicRegisterRobot, "{\"status\":15}", qos=0)
        msg.wait_for_publish()

    def on_register_robot(self, mqttc, obj, msg):
        #if self.__robotID == str(msg.payload, 'utf-8'):
        mqttc.message_callback_add(self.__topicFeedbackRobot, self.on_robot_feedback_message)
        mqttc.subscribe(self.__topicFeedbackRobot, 0)

    def on_robot_feedback_message(self, mqttc, obj, msg):
        feedback_received = str(msg.payload, 'utf-8')
        self.__robotFeedbackQueue.put(feedback_received)

    def on_connect(self, mqttc, obj, flags, rc):
        pass

    # def on_publish(self, mqttc, obj, mid):
    #     logging.debug(f'[{__name__}] {self.__robotID} velocities sent')

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        logging.debug(f'[{__name__}] {self.__robotID} subscribed')

    def on_disconnect(self, client, userdata, rc):
        logging.warning(f'[{__name__}] {self.__robotID} unexpected disconnection')

    # def on_message(self, mqttc, obj, msg):
    #     print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
    #     self.__robotFeedbackQueue.put(str(msg.topic))
