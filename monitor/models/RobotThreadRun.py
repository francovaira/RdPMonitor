import queue
import time
import random
import logging
from .JobManager import Job
from .RobotThreadExecutor import RobotThreadExecutor
from .StateMachine import RobotMachine

class RobotThreadRun:
    def __init__(self, robot):
        self.__robot = robot
        self.__isRunning = False

    def threadRun(self):

        self.robotThreadExecutor = RobotThreadExecutor(self.__robot, self.__robot.getMonitor())
        self.stateMachine = RobotMachine(self.robotThreadExecutor, self.__robot)

        self.stateMachine.output_image_state_machine()

        while(1):
            logging.debug(f'[{__name__}] {self.__robot.getRobotID()} blocked waiting for new job.')
            newJob = self.__robot.getJobQueue().get() # se bloquea hasta que se ponga un elemento

            if(not type(newJob) == Job):
                continue

            self.robotThreadExecutor.addJob(newJob)
            self.robotThreadExecutor.startPaths()

            self.__isRunning = True
            while(self.__isRunning):
                self.__isRunning = self.stateMachine.run()

    def getIsRunning(self):
        return self.__isRunning