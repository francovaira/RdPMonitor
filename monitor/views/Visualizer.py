import pygame
from pygame.locals import *
import time
from Enums import Colors, MapCellOccupationStates, MapCellTypes
import pygame_menu
from Map import Map
import numpy as np

# VERRRR DOCUUU https://pygame.readthedocs.io/en/latest/2_draw/draw.html
class Visualizer:

    def __init__(self, canvasHorizontalSizePixels, canvasVerticalSizePixels, horizontalCells, verticalCells, mapInSharedMemory):
        pygame.init()
        self.__canvas = pygame.display.set_mode((canvasHorizontalSizePixels, canvasVerticalSizePixels))
        self.__canvasHorizontalSizePixels = canvasHorizontalSizePixels
        self.__canvasVerticalSizePixels = canvasVerticalSizePixels
        self.__running = True
        self.__mapInSharedMemory = mapInSharedMemory
        # # self.__mqttcEvent = mqttcEvent
        # # self.__mqttcQueue = mqttcQueue
        self.__robotID = ""

        # Set background color
        self.__canvas.fill(Colors.BACKGROUND.value)
        pygame.display.set_caption("Titulesco")

        self.__horizontalCells = horizontalCells
        self.__verticalCells = verticalCells
        self.__cellWidth = canvasHorizontalSizePixels // (self.__horizontalCells*2)
        self.__cellHeight = canvasHorizontalSizePixels // (self.__horizontalCells*2)

        # Create cells for the grid
        self.__grid = np.zeros((self.__horizontalCells, self.__verticalCells), dtype=object)
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__grid[i][j] = VisualizerCell(self.__canvas, self.__mapInSharedMemory[i][j], self.__cellWidth, self.__cellHeight, self.__robotID)

        self._create_menu(pygame.display.get_surface())

        pygame.display.update()
        pygame.display.flip()

    def _create_menu(self, surface, ):
        theme = pygame_menu.Theme(
            background_color=pygame_menu.themes.TRANSPARENT_COLOR,
            title=False,
            widget_font=pygame_menu.font.FONT_FIRACODE,
            widget_font_color=(255, 255, 255),
            widget_margin=(0, 15),
            widget_selection_effect=pygame_menu.widgets.NoneSelection()
        )

        self._menu = pygame_menu.Menu(
            height=self.__canvasVerticalSizePixels,
            mouse_motion_selection=True,
            position=(845, 25, False),
            theme=theme,
            title='',
            width=240
        )

        self._menu.add.button(
            'Run Solver',
            self._run_solver(),
            button_id='run_solver',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 75),
            shadow_width=10,
        )

        def button_onmouseover(w: 'pygame_menu.widgets.Widget', _) -> None:
            """
            Set the background color of buttons if entered.
            """
            if w.readonly:
                return
            w.set_background_color((98, 103, 106))

        def button_onmouseleave(w: 'pygame_menu.widgets.Widget', _) -> None:
            """
            Set the background color of buttons if leaved.
            """
            w.set_background_color((75, 79, 81))

        for btn in self._menu.get_widgets(['run_solver']):
            btn.set_onmouseover(button_onmouseover)
            btn.set_onmouseleave(button_onmouseleave)
            if not btn.readonly:
                btn.set_cursor(pygame_menu.locals.CURSOR_HAND)
            btn.set_background_color((75, 79, 81))

        self._menu.draw(surface)

    # def setRobotID(self, robotID):
    #     if(robotID == None):
    #         self.__robotID = ""
    #     else:
    #         self.__robotID = robotID

    def run(self):
        while self.__running:

            events = pygame.event.get()

            for event in events:
                if event.type == QUIT:
                    self.__running = False
                    pygame.quit()
                    quit()

            self._menu.update(events)
            self.__updateFromMap()
            self.__drawDisplay()
            time.sleep(0.01)

    def __updateFromMap(self):
        for i in range(self.__horizontalCells-2):
            for j in range(self.__verticalCells-2):
                self.__grid[i+1][j+1].update()

    def __drawDisplay(self):
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__grid[i][j].draw()
        pygame.display.update()

    def _run_solver(self) -> None:
        """
        Run the solver.

        """
        print("Run the solver")
        # manager.run_solver_callback()
        # self.__mqttcEvent.set()
        # self.setRobotID(self.__mqttcQueue.get())
        # print('ROBOT_ID:' + self.__robotID + ' - ' + str(len(self.__robotID)))

class VisualizerCell:
    def __init__(self, canvas, mapCell, width, height, robotID):
        self.__canvas = canvas
        self.__mapCell = mapCell
        self.__color = Colors.BLACK.value
        self.__width = width
        self.__height = height
        self.__borderWidth = 0
        self.__robotID = ""

        self.update()

    def setRobotID(self, robotID):
        if(robotID == None or len(robotID)==0):
            self.__robotID = ""
        else:
            self.__robotID = robotID[0]

    def getRobotID(self):
        return self.__robotID

    def update(self):
        self.setRobotID(self.__mapCell.getOccupantsID())
        cellType = self.__mapCell.getType()
        if(cellType == MapCellTypes.OBSTACLE):
            #self.__color = Colors.BLUE.value
            self.__color = Colors.LIGHT_BLUE.value
        elif(cellType == MapCellTypes.BORDER):
            self.__color = Colors.RED.value
        elif(cellType == MapCellTypes.OCCUPABLE):
            if(self.__mapCell.getOccupationState() == MapCellOccupationStates.OCCUPIED_PLACE):
                #self.__color = Colors.GREEN.value
                if(self.__robotID == "ROB_A"):
                    self.__color = Colors.ROBOT_1.value
                elif(self.__robotID == "ROB_B"):
                    self.__color = Colors.ROBOT_2.value
                elif(self.__robotID == "ROB_C"):
                    self.__color = Colors.ROBOT_3.value

            elif(self.__mapCell.getOccupationState() == MapCellOccupationStates.FREE_PLACE):
                self.__color = Colors.GREY.value
        #self.setRobotID(self.__mapCell.getOccupantsID())

    def draw(self):
        pygame.draw.rect(self.__canvas, self.__color, (self.__mapCell.getPosX()*self.__width+100, self.__mapCell.getPosY()*self.__height+100, self.__width, self.__height), self.__borderWidth)

        # draw robot ID
        if(self.__robotID != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(self.__robotID, True, Colors.BLACK.value)
            self.__canvas.blit(img, (self.__mapCell.getPosX()*self.__width + 105, self.__mapCell.getPosY()*self.__height + 105))

        # draw place ID
        if(self.__mapCell.getPlaceID() != None):
            font = pygame.font.SysFont(None, 20)
            img = font.render(str(self.__mapCell.getPlaceID()), True, Colors.BLACK.value)
            self.__canvas.blit(img, (self.__mapCell.getPosX()*self.__width + 105, self.__mapCell.getPosY()*self.__height + 120))