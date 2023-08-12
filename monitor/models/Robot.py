# import MQTTClient as mqttc
from .RobotThreadRun import RobotThreadRun
import random as rd
import queue
import threading
from threading import Thread

class Robot:
    def __init__(self, monitor, robotID):
        self.__robotID = robotID
        self.__prioridad = None
        self.__caminoRecorrido = None
        # self.__mqtt_client = mqttc.create_client(self.__robotID)
        self.__jobQueue = queue.Queue()
        self.__monitor = monitor

        self.robotThreadRun = RobotThreadRun(self)
        self.thread = Thread(target=self.robotThreadRun.threadRun)

    def getRobotID(self):
        return self.__robotID

    def getThread(self):
        return self.thread

    def getJobQueue(self):
        return self.__jobQueue

    def getMonitor(self):
        return self.__monitor

    def __setRobotID(self, robotID):
        self.__robotID = robotID

    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):