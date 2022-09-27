from multiprocessing import Lock
import pygame
from pygame.locals import *
import time
from Enums import Colors, MapCellOccupationStates, MapCellTypes

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

    def setRobotID(self, robotID):
        if(robotID == None):
            self.robotID = ""
        else:
            self.robotID = robotID

    def update(self):
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

    def draw(self):
        pygame.draw.rect(self.canvas, self.color, (self.mapCell.getPosX()*self.width, self.mapCell.getPosY()*self.height, self.width, self.height), self.borderWidth)

        # draw robot ID
        if(self.robotID != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(self.robotID, True, Colors.BLACK.value)
            self.canvas.blit(img, (self.mapCell.getPosX()*self.width + 5, self.mapCell.getPosY()*self.height + 5))

        # draw place ID
        if(self.mapCell.getPlaceID() != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(str(self.mapCell.getPlaceID()), True, Colors.BLACK.value)
            self.canvas.blit(img, (self.mapCell.getPosX()*self.width + 5, self.mapCell.getPosY()*self.height + 20))

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

        self.horizontalCells = horizontalCells
        self.verticalCells = verticalCells
        self.cellWidth = canvasHorizontalSizePixels // self.horizontalCells
        self.cellHeight = canvasVerticalSizePixels // self.verticalCells

        # create 2D array for the grid
        self.grid = [0 for i in range(self.horizontalCells)]
        for i in range(self.horizontalCells):
            self.grid[i] = [0 for i in range(self.verticalCells)]

        # Create cells for the grid
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j] = VisualizerCell(self.canvas, self.mapInSharedMemory[i][j], self.cellWidth, self.cellHeight)

        font = pygame.font.SysFont(None, 25)
        img = font.render("ValEnTiN", True, Colors.WHITE.value)
        self.canvas.blit(img, ((self.canvasHorizontalSizePixels//2)-45, (self.canvasVerticalSizePixels//2)))
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
            time.sleep(0.05)

    def __updateFromMap(self): # FIXME optimizar para que no actualice los bordes
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j].update()

    def __drawDisplay(self):
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j].draw()
        pygame.display.update()

