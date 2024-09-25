from .MQTTClient import MQTTClient
from .RobotThreadRun import RobotThreadRun
import macros
import random as rd
import threading
import queue
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
            self.__currentOrientation = macros.ORIENTATION_0_DEGREE
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

    def setCurrentOrientation(self, orientation):
        self.__currentOrientation = orientation

    def getInitialPoint(self):
        return self.__initialPoint

    def getFinalPoint(self):
        return self.__finalPoint

    def getRobotSendSetpointTopic(self):
        return str(f'topic/setpoint/{self.__robotID}')

    def getThread(self):
        return self.__thread

    def getJobQueue(self):
        return self.__jobQueue

    def getFeedbackQueue(self):
        return self.__feedbackQueue

    def getClient(self):
        return self.__mqtt_client

    def getMqttClient(self):
        return self.__mqtt_client.getClient()

    def getMonitor(self):
        return self.__monitor

    def __setRobotID(self, robotID):
        self.__robotID = robotID

    def getIsRunning(self):
        return self.robotThreadRun.getIsRunning()

    def getCurrentOrientation(self):
        return self.__currentOrientation

    # esta funcion convierte la orientacion actual del robot a vectores unitarios en el plano cartesiano que apuntan en esa direccion
    # tambien convierte la convencion que se tiene del robot sobre qué significa que este apuntando a 0 grados, 90, etc
    def getCurrentOrientationAsVector(self):
        if(self.__currentOrientation == macros.ORIENTATION_0_DEGREE):
            return (0, -1)
        elif(self.__currentOrientation == macros.ORIENTATION_90_DEGREE):
            return (1, 0)
        elif(self.__currentOrientation == macros.ORIENTATION_180_DEGREE):
            return (0, 1)
        elif(self.__currentOrientation == macros.ORIENTATION_270_DEGREE):
            return (-1, 0)

    def setCurrentOrientationAsVector(self, orientationVector):
        if(orientationVector == (0, -1)):
            self.__currentOrientation = macros.ORIENTATION_0_DEGREE
        if(orientationVector == (1, 0)):
            self.__currentOrientation = macros.ORIENTATION_90_DEGREE
        if(orientationVector == (0, 1)):
            self.__currentOrientation = macros.ORIENTATION_180_DEGREE
        if(orientationVector == (-1, 0)):
            self.__currentOrientation = macros.ORIENTATION_270_DEGREE
        logging.debug(f'[{__name__}] set new current orientation of robot: {self.__currentOrientation}')

    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):