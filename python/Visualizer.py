from multiprocessing import Lock
import pygame
from pygame.locals import *
import random
import time
from enum import Enum

# VERRRR DOCUUU https://pygame.readthedocs.io/en/latest/2_draw/draw.html

class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GREY = (127, 127, 127)
    DARK_GREY = (180, 180, 180)
    BACKGROUND = BLACK

class CellTypes(Enum):
    BORDER = 0
    OBSTACLE = 1
    FREE_PLACE = 2
    OCCUPIED_PLACE = 3


class VisualizerCell:
    def __init__(self, canvas, type, posX, posY, width, height):
        self.canvas = canvas
        self.type = CellTypes.FREE_PLACE.value
        self.color = Colors.BLACK.value
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.borderWidth = 0
        self.robotID = ""

        self.setType(type)

    # lo bueno de esto es que podes setear el estilo de cada tipo, incluso el borde y demases
    def setType(self, type):
        if(type == CellTypes.BORDER):
            self.type = type
            self.color = Colors.RED.value
        elif(type == CellTypes.OBSTACLE):
            self.type = type
            self.color = Colors.BLUE.value
        elif(type == CellTypes.FREE_PLACE):
            self.type = type
            self.color = Colors.GREY.value
        elif(type == CellTypes.OCCUPIED_PLACE):
            self.type = type
            self.color = Colors.DARK_GREY.value

    def setRobotID(self, robotID):
        self.robotID = robotID

    def update(self, show, id):
        if(show):
            self.setType(CellTypes.OCCUPIED_PLACE)
            self.setRobotID(id)
        else:
            self.setType(CellTypes.FREE_PLACE)
            self.setRobotID(None)

    def draw(self):
        pygame.draw.rect(self.canvas, self.color, (self.posX*self.width, self.posY*self.height, self.width, self.height), self.borderWidth)

        # draw robot ID
        if(self.robotID != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(self.robotID, True, Colors.WHITE.value)
            self.canvas.blit(img, (self.posX*self.width + 5, self.posY*self.height + 5))

class Visualizer:

    def __init__(self, canvasHorizontalSizePixels, canvasVerticalSizePixels, horizontalCells, verticalCells, pipeReceiver):
        pygame.init()
        self.canvas = pygame.display.set_mode((canvasHorizontalSizePixels, canvasVerticalSizePixels))
        self.canvasHorizontalSizePixels = canvasHorizontalSizePixels
        self.canvasVerticalSizePixels = canvasVerticalSizePixels
        self.running = True
        self.pipeReceiver = pipeReceiver

        self.canvas.fill(Colors.BACKGROUND.value) # set background color
        pygame.display.set_caption("Titulesco")

        if(horizontalCells != verticalCells):
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
                self.grid[i][j] = VisualizerCell(self.canvas, CellTypes.FREE_PLACE, i, j, self.cellWidth, self.cellHeight)

        # Draw random cells
        # for i in range(20):
        #     valueX = random.randint(1, self.horizontalCells-2)
        #     valueY = random.randint(1, self.verticalCells-2)
        #     self.grid[valueX][valueY].setType(CellTypes.OBSTACLE)

        # Draw defined map obstacles
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

            self.__draw()

            try:
                pipeReceived = self.pipeReceiver.recv()
                if(pipeReceived != None):
                    if(self.__updateCell(pipeReceived[0],pipeReceived[1],pipeReceived[2], pipeReceived[3]) != 0):
                        print("ERROR Unable to update cell from pipeReceiver message")
            finally:
                pass

    def __updateCell(self, posX, posY, show, id):
        if(posX >= self.horizontalCells or posY >= self.verticalCells or posX < 0 or posY < 0):
            return -1
        else:
            self.grid[posX][posY].update(show, id)
            return 0

    def __update(self):
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j].update(random.randint(0,1), "AAAAA")

    def __draw(self):
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j].draw()
        pygame.display.update()



