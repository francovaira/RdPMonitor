import threading
from multiprocessing import Process, Lock
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
        self.setType(type)
        self.posX = posX
        self.posY = posY
        self.width = width
        self.height = height
        self.borderWidth = 0

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

    def update(self, show):
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        self.color = ((r,g,b))
        # if(show):
        #     #print(f"UPDATING ({self.posX},{self.posY}) OCCUPIED_PLACE")
        #     self.setType(CellTypes.OCCUPIED_PLACE)
        # else:
        #     #print(f"UPDATING ({self.posX},{self.posY}) FREE_PLACE")
        #     self.setType(CellTypes.FREE_PLACE)

    def draw(self):
        pygame.draw.rect(self.canvas, self.color, (self.posX*self.width, self.posY*self.height, self.width, self.height), self.borderWidth)


class Visualizer:

    def __init__(self, canvasHorizontalSizePixels, canvasVerticalSizePixels, horizontalCells, verticalCells, queue):
        pygame.init()
        self.canvas = pygame.display.set_mode((canvasHorizontalSizePixels, canvasVerticalSizePixels))
        self.canvasHorizontalSizePixels = canvasHorizontalSizePixels
        self.canvasVerticalSizePixels = canvasVerticalSizePixels
        self.updateAccessLock = Lock()
        self.running = True
        self.queue = queue

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
        self.grid = [0 for i in range(horizontalCells)]
        for i in range(horizontalCells):
            self.grid[i] = [0 for i in range(verticalCells)]

        # Create cells for the grid
        for i in range(horizontalCells):
            for j in range(verticalCells):
                self.grid[i][j] = VisualizerCell(self.canvas, CellTypes.FREE_PLACE, i, j, self.cellWidth, self.cellHeight)

        # Define borders
        for i in range(0,horizontalCells):
            self.grid[i][0].setType(CellTypes.BORDER)
            self.grid[i][verticalCells-1].setType(CellTypes.BORDER)
        for i in range(0, verticalCells):
            self.grid[0][i].setType(CellTypes.BORDER)
            self.grid[horizontalCells-1][i].setType(CellTypes.BORDER)

        # Draw random cells
        for i in range(20):
            valueX = random.randint(1, horizontalCells-2)
            valueY = random.randint(1, verticalCells-2)
            self.grid[valueX][valueY].update(True)

        #pygame.init() # FIXME

        sysfont = pygame.font.get_default_font()
        font = pygame.font.SysFont(None, 20)
        img = font.render("ValEnTiN", True, Colors.WHITE.value)
        self.canvas.blit(img, (20, 20))
        pygame.display.update()
        time.sleep(0.5)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    pygame.quit()
                    quit()

            #self.update() # in case some other update must be done
            #value = random.randint(0,1)
            #valueX = random.randint(1, 10-2)
            #valueY = random.randint(1, 10-2)
            #self.updateCell(valueX, valueY, value)

            self.__draw()

            try:
                queueItem = self.queue.get(False,)
                #print(f"{queueItem[0]},{queueItem[1]},{queueItem[2]}")
                if(queueItem != None):
                    if(self.updateCell(queueItem[0],queueItem[1],queueItem[2]) != 0):
                        print("ERROR Unable to update cell from queue message")
            finally:
                pass

            #print("MOTOR_VIZUALIZER")
            #time.sleep(0.1)

    def update(self):
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                #self.grid[i][j].update(True)
                self.grid[i][j].update(random.randint(0,1))

    def __draw(self):
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.grid[i][j].draw()
        pygame.display.update()


    def updateCell(self, posX, posY, show):
        if(posX >= self.horizontalCells or posY >= self.verticalCells or posX < 0 or posY < 0):
            return -1
        else:
            self.updateAccessLock.acquire()
            try:
                #print("LOCK ACQUIRED")
                self.__updateCell(posX, posY, show) # invoke private function for modifying the grid
            finally:
                #print("LOCK RELEASED")
                self.updateAccessLock.release()
        return 0

    def __updateCell(self, posX, posY, show):
        self.grid[posX][posY].update(show)



