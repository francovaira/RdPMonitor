import time
import threading
from threading import Thread
from .JobManager import Path
from .JobManager import Job
from .JobManager import JobManager
from .Robot import Robot

# esta clase contiene todos los robots asociados y a traves del job manager les envia trabajos

class RobotsManager:
    def __init__(self, monitor):
        self.__monitor = monitor
        self.__jobManager = JobManager()
        self.__robots = []

        # create instances for each robot - FIXME proximamente esto seria automatico cuando se registren los robots al conectarse
        self.robotNames = ['ROB_A', 'ROB_B', 'ROB_C']
        # self.addRobot(Robot(self.__monitor, robotNames.pop()))
        # self.addRobot(Robot(self.__monitor, robotNames.pop()))
        # self.addRobot(Robot(self.__monitor, robotNames.pop()))

    def addRobot(self):
        try:
            robot = Robot(self.__monitor, self.robotNames.pop())
            if(not type(robot) == Robot):
                print("[ROBOTS_MANAGER] Trying to add something that is not a robot.")
            self.__robots.append(robot)
            self.__jobManager.addRobotJobQueue(robot.getRobotID(), robot.getJobQueue())
            robot.getThread().start()
            print(f'[ROBOTS_MANAGER] {robot.getRobotID()} added to the Queue')
        except:
            print("[ROBOTS_MANAGER] Imposible to add more robots")

    # def sendMockJobsToRobots(self):
    #     for robot in self.__robots:
    #         # self.__jobManager.addRobotJobQueue(robot.getRobotID(), robot.getJobQueue())
    #         robot.getThread().start()

    #     threadSendTrbjo = Thread(target=self.__threadSendJobs, args=(self.__jobManager,))
    #     threadSendTrbjo.start()
    def setInitialPoint(self, coordinates):
        try:
            self.__robots[0].setInitialPoint(coordinates)
        except:
            print("[ROBOTS_MANAGER] Any robot available to set initial point")

    def setFinalPoint(self, coordinates):
        try:
            self.__robots[0].setFinalPoint(coordinates)
        except:
            print("[ROBOTS_MANAGER] Any robot available to set final point")

    # este hilo simula como se irian generando los jobs y enviando a cada robot
    def sendJob(self):
        try:
            jobA = Job()
            x_0 = self.__robots[0].getInitialPoint()[0]
            y_0 = self.__robots[0].getInitialPoint()[1]
            x_1 = self.__robots[0].getFinalPoint()[0]
            y_1 = self.__robots[0].getFinalPoint()[1]

            # path = 
            jobA.addPath(Path(x_0, y_0, x_1, y_1))
            # path = Path(3,1,3,3)
            # jobA.addPath(path)
            # path = Path(3,3,1,3)
            # jobA.addPath(path)
            # path = Path(1,3,1,1)
            # jobA.addPath(path)
            self.__jobManager.sendJobToRobot(self.__robots[0].getRobotID(), jobA)
        except:
            print("[ROBOTS_MANAGER] Any robot available")
        #time.sleep(5)

        # jobB = Job()
        # path = Path(11,1,1,11)
        # jobB.addPath(path)
        # jobManager.sendJobToRobot(self.__robots[1].getRobotID(), jobB)

        # #time.sleep(20)

        # jobC = Job()
        # path = Path(3,1,11,11)
        # jobC.addPath(path)
        # path = Path(11,11,3,1)
        # jobC.addPath(path)
        # jobManager.sendJobToRobot(self.__robots[2].getRobotID(), jobC)

        # time.sleep(15)
