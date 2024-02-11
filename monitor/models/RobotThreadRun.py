import queue
import time
import random
from .JobManager import Job
from .RobotThreadExecutor import RobotThreadExecutor
from .StateMachine import RobotMachine

class RobotThreadRun:
    def __init__(self, robot):
        self.__robot = robot

    def threadRun(self):

        self.robotThreadExecutor = RobotThreadExecutor(self.__robot.getRobotID(), self.__robot.getMonitor())
        self.stateMachine = RobotMachine(self.robotThreadExecutor, self.__robot)
        time.sleep(1.5) # esto es para que el hilo espere a que el visualizador inicie

        while(1):
            print(f"{self.__robot.getRobotID()} || me voy a bloquear")
            newJob = self.__robot.getJobQueue().get() # se bloquea hasta que se ponga un elemento

            if(not type(newJob) == Job):
                continue

            self.robotThreadExecutor.addJob(newJob)
            self.robotThreadExecutor.startPaths()

            running = True
            while(running):
                self.stateMachine.dispararMonitor()
                if self.stateMachine.green.is_active != False:
                    pass
                else:
                # assert self.stateMachine.green.is_active is False
                # assert self.stateMachine.yellow.is_active is True
                    self.stateMachine.mandarMensaje()
                    self.stateMachine.recibirMensaje()

            print(f"THREAD {self.__robot.getRobotID()} STALL")
