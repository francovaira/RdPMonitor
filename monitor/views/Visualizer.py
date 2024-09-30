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

        self.__controller = None

        # Available robots
        self.__switch_rob_a = False
        self.__switch_rob_b = False
        self.__switch_rob_c = False

        # Set background color
        self.__canvas.fill(Colors.BACKGROUND.value)
        pygame.display.set_caption("Titulesco")

        self._clock = pygame.time.Clock()
        self._fps = 60

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
                self.__grid[i][j] = VisualizerCell(self.__canvas, self.__controller, self.__mapInSharedMemory[i][j], self.__cellWidth, self.__cellHeight)
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
            self.__syncRobot,
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
            self.__sendRobotJob,
            button_id='start_road',
            cursor=pygame_menu.locals.CURSOR_HAND,
            font_size=20,
            margin=(0, 75),
            shadow_width=3,
        )
        self.btn.set_onmouseover(button_onmouseover)
        self.btn.set_onmouseleave(button_onmouseleave)

        self.__menu.add.dropselect(
            title='',
            items=[('ROB_A', 0),
                   ('ROB_B', 1),
                   ('ROB_C', 2)],
            default=0,
            dropselect_id='robot_id',
            font_size=16,
            padding=0,
            placeholder='Select one',
            selection_box_height=5,
            selection_box_inflate=(0, 20),
            selection_box_margin=0,
            selection_box_text_margin=10,
            selection_box_width=200,
            selection_option_font_size=20,
            shadow_width=20
        )
        self.__menu.add.vertical_margin(10)

        for btn in self.__menu.get_widgets():
            btn.set_onmouseover(button_onmouseover)
            btn.set_onmouseleave(button_onmouseleave)
            btn.set_cursor(pygame_menu.locals.CURSOR_HAND)
            btn.set_background_color((75, 79, 81))

    def __updateFromMap(self):
        for i in range(self.__horizontalCells-1):
            for j in range(self.__verticalCells-1):
                self.__grid[i+1][j+1].update()

    def __drawDisplay(self):
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__grid[i][j].draw()

        # draw reference axis
        pygame.draw.line(self.__canvas, Colors.WHITE.value, (40, 40), (40, 80))
        pygame.draw.line(self.__canvas, Colors.WHITE.value, (40, 40), (80, 40))
        font = pygame.font.SysFont("Arial", 16)
        img = font.render("(0,0)", True, Colors.WHITE.value)
        self.__canvas.blit(img, (20, 20))
        img = font.render("+ Y", True, Colors.WHITE.value)
        self.__canvas.blit(img, (40, 85))
        img = font.render("+ X", True, Colors.WHITE.value)
        self.__canvas.blit(img, (85, 40))

    def __getRobotIdWidget(self):
        rob_id = self.__menu.get_widget('robot_id')
        return rob_id.get_value()[0][0]

    def __syncRobot(self):
        rob_id = self.__getRobotIdWidget()
        self.__controller.createRobot(rob_id)

    def __sendRobotJob(self):
        rob_id = self.__getRobotIdWidget()
        self.__controller.setRobotRoad(rob_id)

    def __selectMapsPoints(self):
        x, y = pygame.mouse.get_pos()
        left, middle, right = pygame.mouse.get_pressed()
        if (x > self.__cellWidth+80) and (x < self.__cellWidth*(self.__horizontalCells-1)+80):
            if (y > self.__cellWidth+80) and (y < self.__cellWidth*(self.__verticalCells-1)+80):
                x = (x-80)//int(self.__cellWidth)
                y = (y-80)//int(self.__cellHeight)
                rob_id = self.__getRobotIdWidget()
                if self.__grid[x][y].getMapCell().getIsOccupable() == True:
                    if left == True:
                        self.__controller.setInitialPoint(tuple((x, y)), rob_id)
                    elif right == True:
                        self.__controller.setFinalPoint(tuple((x, y)), rob_id)
                else:
                    logging.error(f'[{__name__}] coordinates ({x-1},{y-1}) are occupied')

    def __refreshWindow(self):
        self.__canvas.fill(Colors.BACKGROUND.value)
        self.__drawDisplay()
        self.__updateFromMap()
        self.__menu.draw(self.__canvas)
        pygame.display.flip()
        self._clock.tick(self._fps)

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
                    self.__selectMapsPoints()

            self.__refreshWindow()