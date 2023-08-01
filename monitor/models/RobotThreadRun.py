import queue
import time
import random
from .JobManager import Job
from .RobotThreadExecutor import RobotThreadExecutor

class RobotThreadRun:
    def __init__(self, robot):
        self.robot = robot

    def threadRun(self):

        self.robotThreadExecutor = RobotThreadExecutor(self.robot.getRobotID(), self.robot.getMonitor())

        time.sleep(1.5) # esto es para que el hilo espere a que el visualizador inicie

        while(1):
            print(f"{self.robot.getRobotID()} || me voy a bloquear")
            nextJob = self.robot.getRobotQueue().get() # se bloquea hasta que se ponga un elemento

            if(not type(nextJob) == Job):
                continue

            self.robotThreadExecutor.addJob(nextJob)
            self.robotThreadExecutor.startPaths()

            running = True
            while(running):
                running = self.robotThreadExecutor.run()
                #time.sleep(0.5)
                time.sleep(random.random())

            print(f"THREAD {self.robot.getRobotID()} STALL")