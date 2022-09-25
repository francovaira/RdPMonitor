from multiprocessing import Lock
import pygame
from pygame.locals import *
import random
import time
from Enums import MapCellOccupationStates, Colors, MapCellTypes

# VERRRR DOCUUU https://pygame.readthedocs.io/en/latest/2_draw/draw.html



class VisualizerCell:
    def __init__(self, canvas, mapCell, width, height):
        self.canvas = canvas
        self.mapCell = mapCell
        self.color = Colors.BLACK.value
        self.width = width
        self.height = height
        self.borderWidth = 0
        self.robotID = ""

        self.update()
        #self.setColorByState(mapCell.getType(), mapCell.getOccupationState())

    # lo bueno de esto es que podes setear el estilo de cada tipo, incluso el borde y demases
    # def setColorByState(self, type, state):
    #     if(type == MapCellTypes.OBSTACLE):
    #         self.color = Colors.BLUE.value
    #     elif(type == MapCellTypes.BORDER):
    #         self.color = Colors.RED.value
    #     elif(type == MapCellTypes.OCCUPABLE):
    #         if(state == MapCellOccupationStates.OCCUPIED_PLACE.value):
    #             self.color = Colors.DARK_GREY.value
    #         elif(state == MapCellOccupationStates.FREE_PLACE.value):
    #             self.color = Colors.GREY.value
    #     # if(type == CellTypes.BORDER):
    #     #     self.type = type
    #     #     self.color = Colors.RED.value
    #     # elif(type == CellTypes.OBSTACLE):
    #     #     self.type = type
    #     #     self.color = Colors.BLUE.value
    #     # elif(type == CellTypes.FREE_PLACE):
    #     #     self.type = type
    #     #     self.color = Colors.GREY.value
    #     # elif(type == CellTypes.OCCUPIED_PLACE):
    #     #     self.type = type
    #     #     self.color = Colors.DARK_GREY.value

    def setRobotID(self, robotID):
        if(robotID == None):
            self.robotID = ""
        else:
            self.robotID = robotID

    def update(self):
        #self.setColorByState(state)
        if(self.mapCell.getType() == MapCellTypes.OBSTACLE):
            self.color = Colors.BLUE.value
        elif(self.mapCell.getType() == MapCellTypes.BORDER):
            self.color = Colors.RED.value
        elif(self.mapCell.getType() == MapCellTypes.OCCUPABLE):
            if(self.mapCell.getOccupationState() == MapCellOccupationStates.OCCUPIED_PLACE):
                self.color = Colors.GREEN.value
            elif(self.mapCell.getOccupationState() == MapCellOccupationStates.FREE_PLACE):
                self.color = Colors.GREY.value
        self.setRobotID(self.mapCell.getOccupantsID())
        # if(show):
        #     self.setColorByState(CellTypes.OCCUPIED_PLACE)
        #     self.setRobotID(id)
        # else:
        #     self.setColorByState(CellTypes.FREE_PLACE)
        #     self.setRobotID(None)

    def draw(self):
        pygame.draw.rect(self.canvas, self.color, (self.mapCell.getPosX()*self.width, self.mapCell.getPosY()*self.height, self.width, self.height), self.borderWidth)

        # draw robot ID
        if(self.robotID != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(self.robotID, True, Colors.BLACK.value)
            self.canvas.blit(img, (self.mapCell.getPosX()*self.width + 5, self.mapCell.getPosY()*self.height + 5))

class Visualizer:

    def __init__(self, canvasHorizontalSizePixels, canvasVerticalSizePixels, horizontalCells, verticalCells, mapInSharedMemory):
        pygame.init()
        self.canvas = pygame.display.set_mode((canvasHorizontalSizePixels, canvasVerticalSizePixels))
        self.canvasHorizontalSizePixels = canvasHorizontalSizePixels
        self.canvasVerticalSizePixels = canvasVerticalSizePixels
        self.running = True
        self.mapInSharedMemory = mapInSharedMemory

        self.canvas.fill(Colors.BACKGROUND.value) # set background color
        pygame.display.set_caption("Titulesco")

        if(horizontalCells != verticalCells): # FIXME refactorizar esto para que venga directamente desde la config o la red
            if(horizontalCells < verticalCells):
                horizontalCells = verticalCells
            else:
                verticalCells = horizontalCells

        self.horizontalCells = horizontalCells
        self.verticalCells = verticalCells
        self.cellWidth = canvasHorizontalSizePixels // horizontalCells
        self.cellHeight = canvasVerticalSizePixels // verticalCells

        # create 2D array for the grid
        self.grid = [0 for i in range(self.horizontalCells)]
        for i in range(self.horizontalCells):
            self.grid[i] = [0 for i in range(self.verticalCells)]

        # Create cells for the grid
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j] = VisualizerCell(self.canvas, self.mapInSharedMemory[i][j], self.cellWidth, self.cellHeight)

        # Draw defined map obstacles
        # To implement

        # Draw borders
        # To implement

        sysfont = pygame.font.get_default_font()
        font = pygame.font.SysFont(None, 20)
        img = font.render("ValEnTiN", True, Colors.WHITE.value)
        self.canvas.blit(img, ((self.canvasHorizontalSizePixels//2)-30, (self.canvasVerticalSizePixels//2)-10))
        pygame.display.update()
        time.sleep(0.5)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    pygame.quit()
                    quit()

            self.__updateFromMap()
            self.__drawDisplay()
            time.sleep(0.1)

            # update Visualizer grid according to Map state
            # for i in range(self.horizontalCells):
            #     for j in range(self.verticalCells):
            #         placeNewState = True if self.mapInSharedMemory[i][j].getOccupationState() == MapCellOccupationStates.OCCUPIED_PLACE.value else False # FIXME aca ver de hacer que le pase el enum directamente
            #         if(self.__updateCell(i, j, placeNewState, self.mapInSharedMemory[i][j].getOccupantsID()) != 0):
            #             print("ERROR Unable to update cell from pipeReceiver message")

    def __updateFromMap(self):
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                #placeNewState = True if self.mapInSharedMemory[i][j].getOccupationState() == MapCellOccupationStates.OCCUPIED_PLACE.value else False # FIXME aca ver de hacer que le pase el enum directamente
                #if(self.__updateCell(i, j) != 0):
                self.grid[i][j].update()
                    #print("ERROR Unable to update cell by reading shared memory")

    # def __updateCell(self, posX, posY):
    #     if(posX >= self.horizontalCells or posY >= self.verticalCells or posX < 0 or posY < 0):
    #         return -1
    #     else:
    #         self.grid[posX][posY].update()
    #         return 0

    def __drawDisplay(self):
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j].draw()
        pygame.display.update()



