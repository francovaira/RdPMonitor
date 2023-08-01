# import queue
import time
import threading
from threading import Thread
from .Map import Map
from .RdP import RdP
from .MonitorWithQueuesAndPriorityQueue import MonitorWithQueuesAndPriorityQueue
from .JobManager import Path
from .JobManager import Job
from .JobManager import JobManager
from .Robot import Robot

class Model:
    def __init__(self):
        self.map = Map()
        # self.mapHorizontalSize = map.getMapDefinition().getHorizontalSize()

        self.rdp = RdP(self.map)
        # self.#mqttc, mqttc_queue =  mqtt.main()
        self.monitor = MonitorWithQueuesAndPriorityQueue(self.rdp, self.map.getPathFinder())

        # create threads for each robot
        threads = []
        self.robA = Robot(self.monitor)
        self.robB = Robot(self.monitor)
        self.robC = Robot(self.monitor)

        # self.thread_ROBOT_A = Thread(target=self.__threadRun, args=(self.robA,))
        # self.thread_ROBOT_B = Thread(target=self.__threadRun, args=(self.robB,))
        # self.thread_ROBOT_C = Thread(target=self.__threadRun, args=(self.robC,))
        # threads.append(thread_ROBOT_A)
        # threads.append(thread_ROBOT_B)
        # threads.append(thread_ROBOT_C)

    def startJobManager(self):
        self.robA.getThread().start()
        self.robB.getThread().start()
        self.robC.getThread().start()

        self.jobManager = JobManager()
        # print(self.robA.getRobotQueue() , self.robB.getRobotQueue() , self.robC.getRobotQueue())
        self.jobManager.addRobotJobQueue(self.robA.getRobotID(), self.robA.getRobotQueue())
        self.jobManager.addRobotJobQueue(self.robB.getRobotID(), self.robB.getRobotQueue())
        self.jobManager.addRobotJobQueue(self.robC.getRobotID(), self.robC.getRobotQueue())

        self.threadSendTrbjo = Thread(target=self.__threadSendJobs, args=(self.jobManager,))

        self.threadSendTrbjo.start()

    def getMapHorizontalSize(self):
        return self.map.getMapDefinition().getHorizontalSize()

    def getMapVerticalSize(self):
        return self.map.getMapDefinition().getVerticalSize()

    def getMapInSharedMemory(self):
        return self.map.getMapInSharedMemory()

    # este hilo simula como se irian generando los jobs y enviando a cada robot
    def __threadSendJobs(self, jobManager):
        jobA = Job()
        # path = Path(3,1,3,2)
        # jobA.addPath(path)
        # path = Path(3,2,4,5)
        # jobA.addPath(path)
        # path = Path(4,5,5,2)
        # jobA.addPath(path)
        path = Path(1,1,11,11)
        jobA.addPath(path)
        path = Path(11,11,1,1)
        jobA.addPath(path)
        # path = Path(1,1,5,3)
        # jobA.addPath(path)
        # path = Path(5,3,1,1)
        # jobA.addPath(path)
        jobManager.sendJobToRobot(self.robA.getRobotID(), jobA)

        #time.sleep(5)

        jobB = Job()
        # path = Path(1,3,5,1)
        # jobB.addPath(path)
        # path = Path(5,1,2,5)
        # jobB.addPath(path)
        # path = Path(2,5,1,5)
        # jobB.addPath(path)
        path = Path(11,1,1,11)
        jobB.addPath(path)
        # path = Path(1,11,11,1)
        # jobB.addPath(path)
        # path = Path(11,1,7,9)
        # jobB.addPath(path)
        # path = Path(7,9,11,1)
        # jobB.addPath(path)
        jobManager.sendJobToRobot(self.robB.getRobotID(), jobB)

        #time.sleep(20)

        jobC = Job()
        # path = Path(1,2,5,2)
        # jobC.addPath(path)
        # path = Path(5,2,2,5)
        # jobC.addPath(path)
        # path = Path(2,5,3,1)
        # jobC.addPath(path)
        path = Path(3,1,11,11)
        jobC.addPath(path)
        path = Path(11,11,3,1)
        jobC.addPath(path)
        # path = Path(3,1,7,9)
        # jobC.addPath(path)
        # path = Path(7,9,3,1)
        # jobC.addPath(path)
        jobManager.sendJobToRobot(self.robC.getRobotID(), jobC)

        time.sleep(15)
