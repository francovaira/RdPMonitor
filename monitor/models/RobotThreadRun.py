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
            logging.debug(f'[{__name__}] {self.__robot.getRobotID()} blocked')
            newJob = self.__robot.getJobQueue().get() # se bloquea hasta que se ponga un elemento

            if(not type(newJob) == Job):
                continue

            self.robotThreadExecutor.addJob(newJob)
            self.robotThreadExecutor.startPaths()

            self.__isRunning = True
            while(self.__isRunning):

                if (self.stateMachine.finish_state.is_active == True):
                    self.__isRunning = False
                    continue

                if(self.stateMachine.disparo_monitor.is_active == True):
                    self.stateMachine.dispararMonitor()
                    continue

                if(self.stateMachine.calculate_move_vector.is_active == True):
                    self.stateMachine.calculateMovementVector()
                    continue

                if(self.stateMachine.send_setpoint_robot.is_active == True):
                    self.stateMachine.sendSetpointToRobot()
                    continue

                if(self.stateMachine.espera_respuesta.is_active == True):
                    self.stateMachine.esperaRespuesta()
                    continue

                if(self.stateMachine.compensacion_kalman.is_active == True):
                    logging.debug(f'[{self.__robot.getRobotID()}] AAAAAAAA ME FUI A CALCULARRRRR !!!!')
                    self.stateMachine.compensationCalculation()
                    continue

    def getRobotState(self):
        return self.__isRunning