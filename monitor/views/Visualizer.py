import pygame
from pygame.locals import *
import time
from Enums import Colors, MapCellOccupationStates, MapCellTypes
import pygame_menu
import numpy as np
from .VisualizerCell import VisualizerCell

# VERRRR DOCUUU https://pygame.readthedocs.io/en/latest/2_draw/draw.html
class Visualizer:

    def __init__(self, canvasHorizontalSizePixels, canvasVerticalSizePixels):
        pygame.init()
        self.__canvasHorizontalSizePixels = canvasHorizontalSizePixels
        self.__canvasVerticalSizePixels = canvasVerticalSizePixels
        self.__canvas = pygame.display.set_mode((self.__canvasHorizontalSizePixels, self.__canvasVerticalSizePixels))
        self.__running = True
        self.__mapInSharedMemory = None
        # set the controller
        self.__controller = None

        # Set background color
        self.__canvas.fill(Colors.BACKGROUND.value)
        pygame.display.set_caption("Titulesco")

    def __createMap(self):
        self.__horizontalCells = self.__controller.getMapHorizontalSize()
        self.__verticalCells = self.__controller.getMapVerticalSize()
        self.__cellWidth = self.__canvasHorizontalSizePixels // (self.__horizontalCells*1.75)
        self.__cellHeight = self.__canvasHorizontalSizePixels // (self.__horizontalCells*1.75)
        self.__mapInSharedMemory = self.__controller.getMapInSharedMemory()

        # Create cells for the grid
        self.__grid = np.zeros((self.__horizontalCells, self.__verticalCells), dtype=object)
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__grid[i][j] = VisualizerCell(self.__canvas, self.__mapInSharedMemory[i][j], self.__cellWidth, self.__cellHeight)

        self.__create_menu(pygame.display.get_surface())

        pygame.display.update()
        pygame.display.flip()

    def setController(self, controller):
        self.__controller = controller

    def __create_menu(self, surface):
        theme = pygame_menu.Theme(
            background_color=pygame_menu.themes.TRANSPARENT_COLOR,
            title=False,
            widget_font=pygame_menu.font.FONT_FIRACODE,
            widget_font_color=(255, 255, 255),
            widget_margin=(0, 15),
            widget_selection_effect=pygame_menu.widgets.NoneSelection()
        )

        self.__menu = pygame_menu.Menu(
            height=self.__canvasVerticalSizePixels,
            mouse_motion_selection=True,
            position=(845, 25, False),
            theme=theme,
            title='',
            width=240
        )

        self.btn = self.__menu.add.button(
            'Run Solver',
            self.__controller.run,
            button_id='run_solver',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 75),
            shadow_width=10,
        )

        self.btn = self.__menu.add.button(
            'Add Solver',
            self.__controller.add_solver,
            button_id='add_solver',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 75),
            shadow_width=1,
        )

        def button_onmouseover(w: 'pygame_menu.widgets.Widget', _) -> None:
            """
            Set the background color of buttons if entered.
            """
            if w.readonly:
                return
            w.set_background_color((255,255,255))

        def button_onmouseleave(w: 'pygame_menu.widgets.Widget', _) -> None:
            """
            Set the background color of buttons if leaved.
            """
            w.set_background_color((75, 79, 81))

        self.btn.set_onmouseover(button_onmouseover)
        self.btn.set_onmouseleave(button_onmouseleave)
        if not self.btn.readonly:
            self.btn.set_cursor(pygame_menu.locals.CURSOR_HAND)
        self.btn.set_background_color((75, 79, 81))

        self.__menu.draw(surface)

    def run(self):
        self.__createMap()
        while self.__running:

            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.__running = False
                    pygame.quit()
                    quit()

            self.__menu.update(events)
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
