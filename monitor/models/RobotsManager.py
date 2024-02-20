import time
import threading
from threading import Thread
from .JobManager import Path
from .JobManager import Job
from .JobManager import JobManager
from .Robot import Robot
import logging
# esta clase contiene todos los robots asociados y a traves del job manager les envia trabajos

class RobotsManager:
    def __init__(self, monitor):
        self.__monitor = monitor
        self.__jobManager = JobManager()
        self.__robots = []

        # create instances for each robot - FIXME proximamente esto seria automatico cuando se registren los robots al conectarse
        self.__robotNames = []

    def addRobot(self, rob_id):
        try:
            if rob_id in self.__robotNames:
                logging.error(f'[{__name__}] {rob_id} exists in the list')
            else:
                robot = Robot(self.__monitor, rob_id)
                self.__robotNames.append(rob_id)
                self.__robots.append(robot)
                self.__jobManager.addRobotJobQueue(robot.getRobotID(), robot.getJobQueue())
                robot.getThread().start()
        except:
            logging.error("[{__name__}] imposible add more robots")

    def getRobotIndex(self, rob_id):
        return self.__robotNames.index(rob_id)

    def setInitialPoint(self, coordinates, rob_id):
        try:
            self.__robots[self.getRobotIndex(rob_id)].setInitialPoint(coordinates)
            logging.debug(f'[@{rob_id}] inital point {coordinates}')
        except:
            logging.error(f'[{__name__}] any robot available to set initial point')

    def setFinalPoint(self, coordinates, rob_id):
        try:
            self.__robots[self.getRobotIndex(rob_id)].setFinalPoint(coordinates)
            logging.debug(f'[@{rob_id}] final point {coordinates}')
        except:
            logging.error(f'[{__name__}] any robot available to set final point')

    # este hilo simula como se irian generando los jobs y enviando a cada robot
    def sendJob(self, rob_id):
        try:
            job = Job()
            robot_index = self.getRobotIndex(rob_id)
            x_0 = self.__robots[robot_index].getInitialPoint()[0]
            y_0 = self.__robots[robot_index].getInitialPoint()[1]
            x_1 = self.__robots[robot_index].getFinalPoint()[0]
            y_1 = self.__robots[robot_index].getFinalPoint()[1]

            job.addPath(Path(x_0, y_0, x_1, y_1))
            self.__jobManager.sendJobToRobot(self.__robots[robot_index].getRobotID(), job)
        except:
            logging.error(f'[{__name__}] any robot available')