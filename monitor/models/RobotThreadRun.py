import queue
import time
import random
from .JobManager import Job
from .RobotThreadExecutor import RobotThreadExecutor

class RobotThreadRun:
    def __init__(self, robot):
        self.__robot = robot

    def threadRun(self):

        self.robotThreadExecutor = RobotThreadExecutor(self.__robot.getRobotID(), self.__robot.getMonitor())

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
                running = self.robotThreadExecutor.run()
                #time.sleep(0.5)
                time.sleep(random.random())

            print(f"THREAD {self.__robot.getRobotID()} STALL")
