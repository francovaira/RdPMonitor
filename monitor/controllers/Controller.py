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

    def createRobot(self, rob_id):
        self.model.createRobot(rob_id)

    def setRobotRoad(self, rob_id):
        self.model.setRobotRoad(rob_id)

    def setInitialPoint(self, coordinates, rob_id):
        self.model.setInitialPoint(coordinates, rob_id)

    def setFinalPoint(self, coordinates, rob_id):
        self.model.setFinalPoint(coordinates, rob_id)
