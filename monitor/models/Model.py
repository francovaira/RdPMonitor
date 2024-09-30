from .Map import Map
from .RdP import RdP
from .MonitorWithQueuesAndPriorityQueue import MonitorWithQueuesAndPriorityQueue
from .RobotsManager import RobotsManager
import signal, os

class Model:
    def __init__(self):
        self.__map = Map()
        self.__rdp = RdP(self.__map)
        self.__monitor = MonitorWithQueuesAndPriorityQueue(self.__rdp, self.__map.getPathFinder())
        self.__robotsManager = RobotsManager(self.__monitor)
        # Set the signal handler and a 5-second alarm
        # signal.signal(signal.SIGINT, self.handler)

    def createRobot(self, rob_id):
        self.__robotsManager.addRobot(rob_id)

    def setRobotRoad(self, rob_id):
        self.__robotsManager.sendJob(rob_id)

    def setInitialPoint(self, coordinates, rob_id):
        self.__robotsManager.setInitialPoint(coordinates, rob_id)

    def setFinalPoint(self, coordinates, rob_id):
        self.__robotsManager.setFinalPoint(coordinates, rob_id)

    def getRobotOrientation(self, rob_id):
        return self.__robotsManager.getRobotOrientation(rob_id)

    def getMapHorizontalSize(self):
        return self.__map.getMapDefinition().getHorizontalSize()

    def getMapVerticalSize(self):
        return self.__map.getMapDefinition().getVerticalSize()

    def getMapInSharedMemory(self):
        return self.__map.getMapInSharedMemory()

    def getPlaceIDFromMapCoordinate(self, coordinate):
        return self.__map.getPlaceIDFromMapCoordinate(coordinate)

    def handler(self, signum, frame):
        signame = signal.Signals(signum).name
        print(f'Signal handler called with signal {signame} ({signum})')
        raise OSError("Couldn't open device!")