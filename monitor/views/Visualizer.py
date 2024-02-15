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
        # set the Controller
        self.__controller = None
        # Available robots
        self.__switch_rob_a = False
        self.__switch_rob_b = False
        self.__switch_rob_c = False
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
                self.__grid[i][j].draw()

        self.__create_menu(self.__canvas)

    def setController(self, controller):
        self.__controller = controller

    def __create_menu(self, surface):

        def _switch_rob_a(value: bool) -> None:
            """
            Changes diagonals
            """
            self.__switch_rob_a = value

        def _switch_rob_b(value: bool) -> None:
            """
            Changes diagonals
            """
            self.__switch_rob_b = value

        def _switch_rob_c(value: bool) -> None:
            """
            Changes diagonals
            """
            self.__switch_rob_c = value

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
            'Synchronize Robot',
            self.__controller.createRobot,
            button_id='sync_robot',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 30),
            shadow_width=3,
        )
        self.btn.set_onmouseover(button_onmouseover)
        self.btn.set_onmouseleave(button_onmouseleave)

        self.btn = self.__menu.add.button(
            'Start Road',
            self.__controller.setRobotRoad,
            button_id='start_road',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 75),
            shadow_width=3,
        )
        self.btn.set_onmouseover(button_onmouseover)
        self.btn.set_onmouseleave(button_onmouseleave)

        self.__menu.add.toggle_switch(
            'ROB_A',
            self.__switch_rob_a,
            font_size=20,
            margin=(0, 30),
            onchange=_switch_rob_a,
            state_text_font_color=((0, 0, 0), (0, 0, 0)),
            switch_margin=(15, 0),
            toggleswitch_id='ROB_A',
            shadow_width=3,
            width=80
        )

        self.__menu.add.toggle_switch(
            'ROB_B',
            self.__switch_rob_b,
            font_size=20,
            margin=(0, 30),
            onchange=_switch_rob_b,
            state_text_font_color=((0, 0, 0), (0, 0, 0)),
            switch_margin=(15, 0),
            toggleswitch_id='ROB_B',
            shadow_width=3,
            width=80
        )

        self.__menu.add.toggle_switch(
            'ROB_C',
            self.__switch_rob_c,
            font_size=20,
            margin=(0, 100),
            onchange=_switch_rob_c,
            state_text_font_color=((0, 0, 0), (0, 0, 0)),
            switch_margin=(15, 0),
            toggleswitch_id='ROB_C',
            shadow_width=3,
            width=80
        )

        for btn in self.__menu.get_widgets():
            btn.set_onmouseover(button_onmouseover)
            btn.set_onmouseleave(button_onmouseleave)
            btn.set_cursor(pygame_menu.locals.CURSOR_HAND)
            btn.set_background_color((75, 79, 81))

    def run(self):
        self.__createMap()
        while self.__running:
            events = pygame.event.get()
            self.__menu.update(events)
            if pygame_menu.events.MENU_LAST_WIDGET_DISABLE_ACTIVE_STATE in self.__menu.get_last_update_mode()[0]:
                events = []

            for event in events:
                if event.type == QUIT:
                    self.__running = False
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    x, y = pygame.mouse.get_pos()
                    right, middle, left = pygame.mouse.get_pressed()
                    if (x > self.__cellWidth+80) and (x < self.__cellWidth*(self.__horizontalCells-1)+80):
                        if (y > self.__cellWidth+80) and (y < self.__cellWidth*(self.__verticalCells-1)+80):
                            x = (x-80)//int(self.__cellWidth)
                            y = (y-80)//int(self.__cellHeight)
                            if self.__grid[x][y].getMapCell().getIsOccupable() == True:
                                if right == True:
                                    self.__controller.setInitialPoint(tuple((x, y)))
                                elif left == True:
                                    self.__controller.setFinalPoint(tuple((x, y)))
                            else:
                                print(f"[VISUALIZER] Coordinates ({x-1},{y-1}) are occupied")

            self.__updateFromMap()
            self.__drawDisplay()
            self.__menu.draw(self.__canvas)
            time.sleep(0.01)

    def __updateFromMap(self):
        for i in range(self.__horizontalCells-1):
            for j in range(self.__verticalCells-1):
                self.__grid[i+1][j+1].update()

    def __drawDisplay(self):
        pygame.display.update()
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__grid[i][j].draw()