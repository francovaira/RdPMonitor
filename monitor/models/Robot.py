from .MQTTClient import MQTTClient
from .RobotThreadRun import RobotThreadRun
import macros
import random as rd
import threading
import queue
import json
from threading import Thread
import logging

class Robot:
    def __init__(self, monitor, robotID):
        try:
            self.__robotID = robotID
            self.__prioridad = None
            self.__caminoRecorrido = None
            self.__initialPoint = None
            self.__finalPoint = None
            self.__feedbackQueue = queue.Queue(maxsize=1)
            self.__mqtt_client = MQTTClient(robotID, self.__feedbackQueue)
            self.__jobQueue = queue.Queue()
            self.__monitor = monitor
            self.robotThreadRun = RobotThreadRun(self)
            self.__thread = Thread(target=self.robotThreadRun.threadRun)
        except Exception as error:
            logging.error(f'[{__name__}] {error}')

    def getRobotID(self):
        return self.__robotID

    def setInitialPoint(self, point):
        self.__initialPoint = point

    def setFinalPoint(self, point):
        self.__finalPoint = point

    def getInitialPoint(self):
        return self.__initialPoint

    def getFinalPoint(self):
        return self.__finalPoint

    def getRobotSendSetpointTopic(self):
        return str(f'/topic/setpoint/{self.__robotID}')

    def getThread(self):
        return self.__thread

    def getJobQueue(self):
        return self.__jobQueue

    def getFeedbackQueue(self):
        return self.__feedbackQueue

    def getMqttClient(self):
        return self.__mqtt_client.getClient()

    def getMonitor(self):
        return self.__monitor

    def __setRobotID(self, robotID):
        self.__robotID = robotID

    # recibe una tupla con las velocidades y distancia a recorrer (distance, vx, vy, vrot)
    def traslateMovementVectorToMessage(self, movementVector):
        vectorMessage = {
            # "distance": macros.DEFAULT_ROBOT_MOVE_DISTANCE,
            # "vx": movementVector[0],
            # "vy": movementVector[1],
            # "vr": movementVector[2]

            "distance": movementVector[0],
            "vx": movementVector[1],
            "vy": movementVector[2],
            "vr": movementVector[3]
        }
        return json.dumps(vectorMessage)

    def getState(self):
        return self.robotThreadRun.getRobotState()

    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):