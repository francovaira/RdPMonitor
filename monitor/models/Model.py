import queue
import time
import random
import threading
from threading import Thread
from .Map import Map
from .RdP import RdP
from .MonitorWithQueuesAndPriorityQueue import MonitorWithQueuesAndPriorityQueue
from .JobManager import Path
from .JobManager import Job
from .JobManager import JobManager
from .RobotThreadExecutor import RobotThreadExecutor

class Model:
    def __init__(self):
        self.map = Map()
        # self.mapHorizontalSize = map.getMapDefinition().getHorizontalSize()

        self.rdp = RdP(self.map)
        # self.#mqttc, mqttc_queue =  mqtt.main()
        self.monitor = MonitorWithQueuesAndPriorityQueue(self.rdp, self.map.getPathFinder())

        # create threads for each robot
        threads = []
        self.jobQueueRobA = queue.Queue()
        self.jobQueueRobB = queue.Queue()
        self.jobQueueRobC = queue.Queue()

        self.thread_ROBOT_A = Thread(target=self.__threadRun, args=('ROB_A', self.jobQueueRobA, self.monitor))
        self.thread_ROBOT_B = Thread(target=self.__threadRun, args=('ROB_B', self.jobQueueRobB, self.monitor))
        self.thread_ROBOT_C = Thread(target=self.__threadRun, args=('ROB_C', self.jobQueueRobC, self.monitor))
        # threads.append(thread_ROBOT_A)
        # threads.append(thread_ROBOT_B)
        # threads.append(thread_ROBOT_C)

    def startJobManager(self):
        self.thread_ROBOT_A.start()
        self.thread_ROBOT_B.start()
        self.thread_ROBOT_C.start()

        self.jobManager = JobManager()
        self.jobManager.addRobotJobQueue('ROB_A', self.jobQueueRobA)
        self.jobManager.addRobotJobQueue('ROB_B', self.jobQueueRobB)
        self.jobManager.addRobotJobQueue('ROB_C', self.jobQueueRobC)

        self.threadSendTrbjo = Thread(target=self.__threadSendJobs, args=(self.jobManager,))

        self.threadSendTrbjo.start()

    def getMapHorizontalSize(self):
        return self.map.getMapDefinition().getHorizontalSize()

    def getMapVerticalSize(self):
        return self.map.getMapDefinition().getVerticalSize()

    def getMapInSharedMemory(self):
        return self.map.getMapInSharedMemory()

    def __threadRun(self, robotID, jobQueue, monitor):

        robotThreadExecutor = RobotThreadExecutor(robotID, monitor)

        time.sleep(1.5) # esto es para que el hilo espere a que el visualizador inicie

        while(1):
            print(f"{robotID} || me voy a bloquear")
            nextJob = jobQueue.get() # se bloquea hasta que se ponga un elemento

            if(not type(nextJob) == Job):
                continue

            robotThreadExecutor.addJob(nextJob)
            robotThreadExecutor.startPaths()

            running = True
            while(running):
                running = robotThreadExecutor.run()
                #time.sleep(0.5)
                time.sleep(random.random())

            print(f"THREAD {robotID} STALL")

    # este hilo simula como se irian generando los jobs y enviando a cada robot
    def __threadSendJobs(self, jobManager):
        jobA = Job()
        # path = Path(3,1,3,2)
        # jobA.addPath(path)
        # path = Path(3,2,4,5)
        # jobA.addPath(path)
        # path = Path(4,5,5,2)
        # jobA.addPath(path)
        path = Path(1,1,5,5)
        jobA.addPath(path)
        path = Path(5,5,1,1)
        jobA.addPath(path)
        jobManager.sendJobToRobot('ROB_A', jobA)

        #time.sleep(5)

        jobB = Job()
        # path = Path(1,3,5,1)
        # jobB.addPath(path)
        # path = Path(5,1,2,5)
        # jobB.addPath(path)
        # path = Path(2,5,1,5)
        # jobB.addPath(path)
        path = Path(5,1,1,5)
        jobB.addPath(path)
        path = Path(1,5,5,1)
        jobB.addPath(path)
        jobManager.sendJobToRobot('ROB_B', jobB)

        #time.sleep(20)

        jobC = Job()
        # path = Path(1,2,5,2)
        # jobC.addPath(path)
        # path = Path(5,2,2,5)
        # jobC.addPath(path)
        # path = Path(2,5,3,1)
        # jobC.addPath(path)
        path = Path(3,1,5,5)
        jobC.addPath(path)
        path = Path(5,5,3,1)
        jobC.addPath(path)
        jobManager.sendJobToRobot('ROB_C', jobC)
