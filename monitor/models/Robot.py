from .MQTTClient import MQTTClient
from .RobotThreadRun import RobotThreadRun
import random as rd
import queue
import threading
import json
from threading import Thread

class Robot:
    def __init__(self, monitor, robotID):
        self.__robotID = robotID
        self.__prioridad = None
        self.__caminoRecorrido = None
        self.__messageQueue = queue.Queue(maxsize=1)
        self.__jobQueue = queue.Queue()
        self.__monitor = monitor
        self.__mqtt_client = MQTTClient(robotID, self.__messageQueue).createClient()

        self.robotThreadRun = RobotThreadRun(self)
        self.__thread = Thread(target=self.robotThreadRun.threadRun)

    def getRobotID(self):
        return self.__robotID

    def getRobotTopic(self):
        return str(f'/topic/v1/{self.__robotID}')

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
        if path == (1,0):
            json_path = str('{"setpoint" : 1, "vel_x" : 0.25, "vel_y" : 0, "vel_ang" : 0}')
            return json_path[:60]
        elif path == (-1,0):
            json_path = str('{"setpoint" : 1, "vel_x" : -0.25, "vel_y" : 0, "vel_ang" : 0}')
            return json_path[:61]
        elif path == (0,1):
            json_path = str('{"setpoint" : 1, "vel_x" : 0, "vel_y" : -0.25, "vel_ang" : 0}')
            return json_path[:61]
        elif path == (0,-1):
            json_path = str('{"setpoint" : 1, "vel_x" : 0, "vel_y" : 0.25, "vel_ang" : 0}')
            return json_path[:60]
        elif path == (0,0):
            json_path = str('{"setpoint" : 1, "vel_x" : 0, "vel_y" : 0, "vel_ang" : 0}')
            return json_path[:58]

    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):