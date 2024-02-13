# from views.Visualizer import Visualizer as view
# from models.JobManager import JobManager as model
import multiprocessing
import logging
from multiprocessing import Process

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def getMapHorizontalSize(self):
        return self.model.getMapHorizontalSize()

    def getMapVerticalSize(self):
        return self.model.getMapVerticalSize()

    def getMapInSharedMemory(self):
        return self.model.getMapInSharedMemory()

    def getPlaceIDFromMapCoordinate(self, coordinate):
        return self.model.getPlaceIDFromMapCoordinate(coordinate)

    def createRobot(self):
        self.model.createRobot()

    def setRobotRoad(self):
        self.model.setRobotRoad()

    def setInitialPoint(self, coordinates):
        self.model.setInitialPoint(coordinates)

    def setFinalPoint(self, coordinates):
        self.model.setFinalPoint(coordinates)
