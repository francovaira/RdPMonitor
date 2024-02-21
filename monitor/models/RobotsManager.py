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
        except Exception as error:
            logging.error(f'[{__name__}] imposible add more robots')
            logging.error(f'[{__name__}] {error}')

    def getRobotIndex(self, rob_id):
        return self.__robotNames.index(rob_id)

    def setInitialPoint(self, coordinates, rob_id):
        try:
            robot = self.__robots[self.getRobotIndex(rob_id)]
            if not robot.getState():
                robot.setInitialPoint(coordinates)
                logging.debug(f'[@{rob_id}] inital point {coordinates}')
            else:
                logging.error(f'[{__name__}] exists job in process in {rob_id}')
        except:
            logging.error(f'[{__name__}] any robot available to set initial point')

    def setFinalPoint(self, coordinates, rob_id):
        try:
            robot = self.__robots[self.getRobotIndex(rob_id)]
            if not robot.getState():
                robot.setFinalPoint(coordinates)
                logging.debug(f'[@{rob_id}] final point {coordinates}')
            else:
                logging.error(f'[{__name__}] exists job in process in {rob_id}')
        except:
            logging.error(f'[{__name__}] any robot available to set final point')

    # este hilo simula como se irian generando los jobs y enviando a cada robot
    def sendJob(self, rob_id):
        try:
            robot = self.__robots[self.getRobotIndex(rob_id)]
            if not robot.getState():
                job = Job()
                initial = robot.getInitialPoint()
                final = robot.getFinalPoint()
                if (initial and final) != None: 
                    job.addPath(Path(initial, final))
                    self.__jobManager.sendJobToRobot(robot.getRobotID(), job)
                else:
                    logging.error(f'[{__name__}] initial and final points not selected for @{rob_id}')
            else:
                logging.error(f'[{__name__}] exists job in process in {rob_id}')
        except:
            logging.error(f'[{__name__}] any robot available')

    # def __verifyJob(self, rob_id):
    #     robot_index = self.getRobotIndex(rob_id)
    #     qsize = self.__robots[robot_index].getJobQueue().qsize()
    #     return qsize