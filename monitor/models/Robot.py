from .MQTTClient import MQTTClient
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
        self.__messageQueue = queue.Queue()
        self.__jobQueue = queue.Queue()
        self.__monitor = monitor
        self.__mqtt_client = MQTTClient(robotID, self.__messageQueue).createClient()

        self.robotThreadRun = RobotThreadRun(self)
        self.__thread = Thread(target=self.robotThreadRun.threadRun)

    def getRobotID(self):
        return self.__robotID

    def getThread(self):
        return self.__thread

    def getJobQueue(self):
        return self.__jobQueue

    def getMsgQueue(self):
        return self.__messageQueue

    def getMqttClient(self):
        return self.__mqtt_client

    def getMonitor(self):
        return self.__monitor

    def __setRobotID(self, robotID):
        self.__robotID = robotID

    def traslatePath(self, path):
        print("traslatePath" + str(tuple(map(lambda i, j: i & j, path, (1,0)))))

        if tuple(map(lambda i, j: i & j, path, (1,0))) == (1,0):
            print("You can become a web developer.")
        elif tuple(map(lambda i, j: i & j, path, (-1,0))) == (-1,0):
            print("You can become a backend developer.")
        elif tuple(map(lambda i, j: i & j, path, (0,1))) == (0,1):
            print("You can become a Data Scientist")
        elif tuple(map(lambda i, j: i & j, path, (0,-1))) == (0,-1):
             print("You can become a Blockchain developer.")
        elif path == (0,0):
            print("You can become a mobile app developer")

    # def __normalize(self, path):
    #     if path[0] >= 1:
    #         path[0]
    #     elif path[1] >= 1:


    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):