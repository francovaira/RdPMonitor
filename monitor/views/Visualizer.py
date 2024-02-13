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
        self._diagonals = True

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

        # pygame.display.flip()

        # time.sleep(2)
        # pygame.display.update()
        self.__create_menu(pygame.display.get_surface())
        # pygame.display.flip()
        # pygame.display.update()

        # time.sleep(2)


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
            'Create Robot',
            self.__controller.createRobot,
            button_id='create_robot',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 75),
            shadow_width=10,
        )

        self.btn = self.__menu.add.button(
            'Start Road',
            self.__controller.setRobotRoad,
            button_id='start_road',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 75),
            shadow_width=10,
        )

        def _diagonals(value: bool) -> None:
            """
            Changes diagonals
            """
            self._diagonals = value

        self.__menu.add.toggle_switch(
            'Diagonals',
            self._diagonals,
            font_size=20,
            margin=(0, 30),
            onchange=_diagonals,
            state_text_font_color=((0, 0, 0), (0, 0, 0)),
            switch_margin=(15, 0),
            toggleswitch_id='diagonals',
            width=80
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
            self.__menu.update(events)
            if pygame_menu.events.MENU_LAST_WIDGET_DISABLE_ACTIVE_STATE in self.__menu.get_last_update_mode()[0]:
                events = []

            for event in events:
                if event.type == QUIT:
                    self.__running = False
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    but = pygame.mouse.get_pressed()
                    if (pos[0] > self.__cellWidth+80) and (pos[0] < self.__cellWidth*(self.__horizontalCells-1)+80):
                        if (pos[1] > self.__cellWidth+80) and (pos[1] < self.__cellWidth*(self.__horizontalCells-1)+80):
                            x = (pos[0]-80)//52
                            y = (pos[1]-80)//52
                            # print(f'DESOCUPADA: {}')
                            if self.__grid[x][y].getMapCell().getIsOccupable() == True:
                                if but[0] == True:
                                    # print(f"RIGHT: {(pos[0]-80)//52}, {(pos[1]-80)//52} ||| {but[0]}")
                                    self.__controller.setInitialPoint(tuple((x, y)))
                                elif but[2] == True:
                                    # print(f"LEFT: {(pos[0]-80)//52}, {(pos[1]-80)//52} ||| {but[2]}")
                                    self.__controller.setFinalPoint(tuple((x, y)))

            self.__updateFromMap()
            self.__drawDisplay()
            # time.sleep(4)

    def __updateFromMap(self):
        # pygame.display.update()
        # time.sleep(0.1)
        # print(f'H: {self.__horizontalCells} - V: {self.__verticalCells}')
        for i in range(self.__horizontalCells-1):
            for j in range(self.__verticalCells-1):
                self.__grid[i+1][j+1].update()
                # self.__grid[i][j].draw()
                # print(f'POS_X:' {self.__grid[i][j].getPosX()})
                # print(f'POS_X:', self.__grid[i][j].getMapCell().getXCoordinate())


    def __drawDisplay(self):
        pygame.display.update()
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                # self.__grid[i+1][j+1].update()
                self.__grid[i][j].draw()
        # pygame.display.update()
