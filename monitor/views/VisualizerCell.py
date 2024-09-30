import pygame
from pygame.locals import *
import macros
from Enums import Colors, MapCellOccupationStates, MapCellTypes

class VisualizerCell:
    def __init__(self, canvas, controller, mapCell, width, height):
        self.__canvas = canvas
        self.__controller = controller
        self.__mapCell = mapCell
        self.__color = Colors.BLACK.value
        self.__width = width
        self.__height = height
        self.__borderWidth = 0
        self.__robotID = ""
        self.__robotCurrentOrientation = macros.ORIENTATION_0_DEGREE

        self.update()

    def setRobotID(self, robotID):
        if(robotID == None or len(robotID)==0):
            self.__robotID = ""
        else:
            self.__robotID = robotID[0]

    def setRobotCurrentOrientation(self, robotCurrentOrientation):
        self.__robotCurrentOrientation = robotCurrentOrientation

    def getRobotID(self):
        return self.__robotID

    def getMapCell(self):
        return self.__mapCell

    def update(self):
        self.setRobotID(self.__mapCell.getOccupantsID())
        self.setRobotCurrentOrientation(self.__controller.getRobotOrientation(self.__robotID))
        cellType = self.__mapCell.getType()
        if(cellType == MapCellTypes.OBSTACLE):
            self.__color = Colors.LIGHT_BLUE.value
        elif(cellType == MapCellTypes.BORDER):
            self.__color = Colors.RED.value
        elif(cellType == MapCellTypes.OCCUPABLE):
            if(self.__mapCell.getOccupationState() == MapCellOccupationStates.OCCUPIED_PLACE):
                if(self.__robotID == "ROB_A"):
                    self.__color = Colors.ROBOT_1.value
                elif(self.__robotID == "ROB_B"):
                    self.__color = Colors.ROBOT_2.value
                elif(self.__robotID == "ROB_C"):
                    self.__color = Colors.ROBOT_3.value

            elif(self.__mapCell.getOccupationState() == MapCellOccupationStates.FREE_PLACE):
                self.__color = Colors.GREY.value

    def draw(self):
        pygame.draw.rect(self.__canvas, self.__color, (self.__mapCell.getPosX()*self.__width+80, self.__mapCell.getPosY()*self.__height+80, self.__width, self.__height), self.__borderWidth)
        # print((self.__mapCell.getPosX()*self.__width+80, self.__mapCell.getPosY()*self.__height+80, self.__width, self.__height))
        # draw robot ID
        # if(self.__robotID != None):
        if(self.__robotID != ""):
            font = pygame.font.SysFont(None, 20)
            img = font.render(self.__robotID, True, Colors.BLACK.value)
            self.__canvas.blit(img, (self.__mapCell.getPosX()*self.__width + 80, self.__mapCell.getPosY()*self.__height + 95))
            self.__drawOrientation()

        # draw place ID
        if(self.__mapCell.getPlaceID() != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(str(self.__mapCell.getPlaceID()), True, Colors.BLACK.value)
            self.__canvas.blit(img, (self.__mapCell.getPosX()*self.__width + 82, self.__mapCell.getPosY()*self.__height + 82))

    def __drawOrientation(self):
        arrowToPrint = '↓'

        if(self.__robotCurrentOrientation == macros.ORIENTATION_0_DEGREE):
            arrowToPrint = '↓'
        elif(self.__robotCurrentOrientation == macros.ORIENTATION_90_DEGREE):
            arrowToPrint = '→'
        elif(self.__robotCurrentOrientation == macros.ORIENTATION_180_DEGREE):
            arrowToPrint = '↑'
        elif(self.__robotCurrentOrientation == macros.ORIENTATION_270_DEGREE):
            arrowToPrint = '←'

        font = pygame.font.SysFont("Arial", 20)
        img = font.render(arrowToPrint, True, Colors.WHITE.value)
        self.__canvas.blit(img, (self.__mapCell.getPosX()*self.__width + (self.__width/2) + 80, self.__mapCell.getPosY()*self.__height + (self.__height/2) + 80))