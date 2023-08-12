import time
import threading
from threading import Thread
from .JobManager import Path
from .JobManager import Job
from .JobManager import JobManager
from .Robot import Robot

class RobotsManager:
    def __init__(self, monitor):
        self.__monitor = monitor
        self.__jobManager = JobManager()
        self.__robots = []

        # create instances for each robot - FIXME proximamente esto seria automatico cuando se registren los robots al conectarse
        robotNames = ['ROB_A', 'ROB_B', 'ROB_C']
        self.addRobot(Robot(self.__monitor, robotNames.pop()))
        self.addRobot(Robot(self.__monitor, robotNames.pop()))
        self.addRobot(Robot(self.__monitor, robotNames.pop()))

    def addRobot(self, robot):
        if(not type(robot) == Robot):
            print("[ROBOTS_MANAGER] Trying to add something that is not a robot.")
        self.__robots.append(robot)
        self.__jobManager.addRobotJobQueue(robot.getRobotID(), robot.getJobQueue())

    def sendMockJobsToRobots(self):
        for robot in self.__robots:
            # self.__jobManager.addRobotJobQueue(robot.getRobotID(), robot.getJobQueue())
            robot.getThread().start()

        threadSendTrbjo = Thread(target=self.__threadSendJobs, args=(self.__jobManager,))
        threadSendTrbjo.start()

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
