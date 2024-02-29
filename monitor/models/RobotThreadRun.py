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
        self.__state = False

    def threadRun(self):

        self.robotThreadExecutor = RobotThreadExecutor(self.__robot.getRobotID(), self.__robot.getMonitor())
        self.stateMachine = RobotMachine(self.robotThreadExecutor, self.__robot)

        while(1):
            logging.debug(f'[{__name__}] {self.__robot.getRobotID()} blocked')
            newJob = self.__robot.getJobQueue().get() # se bloquea hasta que se ponga un elemento

            if(not type(newJob) == Job):
                continue

            self.robotThreadExecutor.addJob(newJob)
            self.robotThreadExecutor.startPaths()

            self.__state = True
            while(self.__state):
                # Dispara la transición que desemboca en la ejecución del ciclo de estados
                self.stateMachine.dispararMonitor()
                if self.stateMachine.finish_state.is_active == True:
                    self.__state = False

    def getRobotState(self):
        return self.__state