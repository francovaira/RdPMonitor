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
        self.__map = Map()
        self.__jobManager = JobManager() # FIXME posiblemente el JobManager quede absorbido por una clase "RobotsManager"
        self.__rdp = RdP(self.__map)
        self.__monitor = MonitorWithQueuesAndPriorityQueue(self.__rdp, self.__map.getPathFinder())
        # self.#mqttc, mqttc_queue =  mqtt.main()

        # create instances for each robot - FIXME proximamente esto seria automatico cuando se registren los robots al conectarse
        robotNames = ['ROB_A', 'ROB_B', 'ROB_C']
        self.__robots = []
        self.__robots.append(Robot(self.__monitor, robotNames.pop()))
        self.__robots.append(Robot(self.__monitor, robotNames.pop()))
        self.__robots.append(Robot(self.__monitor, robotNames.pop()))

    def startJobManager(self):
        for robot in self.__robots:
            self.__jobManager.addRobotJobQueue(robot.getRobotID(), robot.getJobQueue())
            robot.getThread().start()

        threadSendTrbjo = Thread(target=self.__threadSendJobs, args=(self.__jobManager,))
        threadSendTrbjo.start()

    def getMapHorizontalSize(self):
        return self.__map.getMapDefinition().getHorizontalSize()

    def getMapVerticalSize(self):
        return self.__map.getMapDefinition().getVerticalSize()

    def getMapInSharedMemory(self):
        return self.__map.getMapInSharedMemory()

    # este hilo simula como se irian generando los jobs y enviando a cada robot
    def __threadSendJobs(self, jobManager):
        jobA = Job()
        # path = Path(4,5,5,2)
        # jobA.addPath(path)
        path = Path(1,1,11,11)
        jobA.addPath(path)
        path = Path(11,11,1,1)
        jobA.addPath(path)
        jobManager.sendJobToRobot(self.__robots[0].getRobotID(), jobA)

        #time.sleep(5)

        jobB = Job()
        path = Path(11,1,1,11)
        jobB.addPath(path)
        jobManager.sendJobToRobot(self.__robots[1].getRobotID(), jobB)

        #time.sleep(20)

        jobC = Job()
        path = Path(3,1,11,11)
        jobC.addPath(path)
        path = Path(11,11,3,1)
        jobC.addPath(path)
        jobManager.sendJobToRobot(self.__robots[2].getRobotID(), jobC)

        time.sleep(15)
