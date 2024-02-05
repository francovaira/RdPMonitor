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

    def startJobManager(self):
        self.__robotsManager.sendMockJobsToRobots()

    def getMapHorizontalSize(self):
        return self.__map.getMapDefinition().getHorizontalSize()

    def getMapVerticalSize(self):
        return self.__map.getMapDefinition().getVerticalSize()

    def getMapInSharedMemory(self):
        return self.__map.getMapInSharedMemory()

    def handler(self, signum, frame):
        signame = signal.Signals(signum).name
        print(f'Signal handler called with signal {signame} ({signum})')
        raise OSError("Couldn't open device!")