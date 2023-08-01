# import MQTTClient as mqttc
from .RobotThreadRun import RobotThreadRun
import random as rd
import queue
import threading
from threading import Thread

class Robot:
    def __init__(self, monitor):
    # def __init__(self, robotID):
        self.robotID = None
        self._prioridad = None
        self._caminoRecorrido = None
        # self._mqtt_client = mqttc.create_client(self.robotID)
        self.robotQueue = queue.Queue()
        self.monitor = monitor
        self.robotThreadRun = RobotThreadRun(self)

        self.__setRobotID()
        self.thread = Thread(target=self.robotThreadRun.threadRun)

    def getRobotID(self):
        return self.robotID

    def getThread(self):
        return self.thread

    def getRobotQueue(self):
        return self.robotQueue

    def getMonitor(self):
        return self.monitor

    def __setRobotID(self):
        identificador = "id_" + str(rd.randint(1, 10))
        self.robotID = identificador

    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):