from multiprocessing import Lock
import pygame
from pygame.locals import *
import time
from Enums import Colors, MapCellOccupationStates, MapCellTypes

# VERRRR DOCUUU https://pygame.readthedocs.io/en/latest/2_draw/draw.html

class VisualizerCell:
    def __init__(self, canvas, mapCell, width, height):
        self.__canvas = canvas
        self.__mapCell = mapCell
        self.__color = Colors.BLACK.value
        self.__width = width
        self.__height = height
        self.__borderWidth = 0
        self.__robotID = ""

        self.update()

    def setRobotID(self, robotID):
        if(robotID == None):
            self.__robotID = ""
        else:
            self.__robotID = robotID

    def update(self):
        if(self.__mapCell.getType() == MapCellTypes.OBSTACLE):
            self.__color = Colors.BLUE.value
        elif(self.__mapCell.getType() == MapCellTypes.BORDER):
            self.__color = Colors.RED.value
        elif(self.__mapCell.getType() == MapCellTypes.OCCUPABLE):
            if(self.__mapCell.getOccupationState() == MapCellOccupationStates.OCCUPIED_PLACE):
                self.__color = Colors.GREEN.value
            elif(self.__mapCell.getOccupationState() == MapCellOccupationStates.FREE_PLACE):
                self.__color = Colors.GREY.value
        self.setRobotID(self.__mapCell.getOccupantsID())

    def draw(self):
        pygame.draw.rect(self.__canvas, self.__color, (self.__mapCell.getPosX()*self.__width, self.__mapCell.getPosY()*self.__height, self.__width, self.__height), self.__borderWidth)

        # draw robot ID
        if(self.__robotID != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(self.__robotID, True, Colors.BLACK.value)
            self.__canvas.blit(img, (self.__mapCell.getPosX()*self.__width + 5, self.__mapCell.getPosY()*self.__height + 5))

        # draw place ID
        if(self.__mapCell.getPlaceID() != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(str(self.__mapCell.getPlaceID()), True, Colors.BLACK.value)
            self.__canvas.blit(img, (self.__mapCell.getPosX()*self.__width + 5, self.__mapCell.getPosY()*self.__height + 20))

class Visualizer:

    def __init__(self, canvasHorizontalSizePixels, canvasVerticalSizePixels, horizontalCells, verticalCells, mapInSharedMemory):
        pygame.init()
        self.__canvas = pygame.display.set_mode((canvasHorizontalSizePixels, canvasVerticalSizePixels))
        self.__canvasHorizontalSizePixels = canvasHorizontalSizePixels
        self.__canvasVerticalSizePixels = canvasVerticalSizePixels
        self.__running = True
        self.__mapInSharedMemory = mapInSharedMemory

        self.__canvas.fill(Colors.BACKGROUND.value) # set background color
        pygame.display.set_caption("Titulesco")

        self.__horizontalCells = horizontalCells
        self.__verticalCells = verticalCells
        self.__cellWidth = canvasHorizontalSizePixels // self.__horizontalCells
        self.__cellHeight = canvasVerticalSizePixels // self.__verticalCells

        # create 2D array for the grid
        self.__grid = [0 for i in range(self.__horizontalCells)]
        for i in range(self.__horizontalCells):
            self.__grid[i] = [0 for i in range(self.__verticalCells)]

        # Create cells for the grid
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__grid[i][j] = VisualizerCell(self.__canvas, self.__mapInSharedMemory[i][j], self.__cellWidth, self.__cellHeight)

        font = pygame.font.SysFont(None, 25)
        img = font.render("ValEnTiN", True, Colors.WHITE.value)
        self.__canvas.blit(img, ((self.__canvasHorizontalSizePixels//2)-45, (self.__canvasVerticalSizePixels//2)))
        pygame.display.update()
        time.sleep(0.5)

    def run(self):
        while self.__running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.__running = False
                    pygame.quit()
                    quit()

            self.__updateFromMap()
            self.__drawDisplay()
            time.sleep(0.1)

    def __updateFromMap(self):
        for i in range(self.__horizontalCells-2):
            for j in range(self.__verticalCells-2):
                self.__grid[i+1][j+1].update()

    def __drawDisplay(self):
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__grid[i][j].draw()
        pygame.display.update()

