import sys
import os

# Agrega el directorio padre al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from pygame.locals import *
import time
from Enums import Colors
import pygame_menu
from Map import Map
from VisualizerCell import VisualizerCell
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
            _run_solver(),
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

def main():
    map = Map()
    mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
    mapVerticalSize = map.getMapDefinition().getVerticalSize()

    viz = Visualizer(1200, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

    viz.run()

def _run_solver() -> None:
    """
    Run the solver.

    """
    print("Run the solver")
    # manager.run_solver_callback()
    # self.__mqttcEvent.set()
    # self.setRobotID(self.__mqttcQueue.get())
    # print('ROBOT_ID:' + self.__robotID + ' - ' + str(len(self.__robotID)))

if __name__ == "__main__":
    main()