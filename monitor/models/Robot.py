from .MQTTClient import MQTTClient
from .RobotThreadRun import RobotThreadRun
import random as rd
import queue
import threading
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
            self.__messageQueue = queue.Queue(maxsize=1)
            self.__mqtt_client = MQTTClient(robotID, self.__messageQueue)
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

    def getRobotTopic(self):
        return str(f'/topic/v1/{self.__robotID}')

    def getThread(self):
        return self.__thread

    def getJobQueue(self):
        return self.__jobQueue

    def getMsgQueue(self):
        return self.__messageQueue

    def getMqttClient(self):
        return self.__mqtt_client.getClient()

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

    def getState(self):
        return self.robotThreadRun.getRobotState()

    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):