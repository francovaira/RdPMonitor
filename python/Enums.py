from enum import Enum

class MapCellTypes(Enum): # they have the format (enumID, isOccupable)
    BORDER = (0, False)
    OBSTACLE = (1, False)
    OCCUPABLE = (2, True)

class MapCellOccupationStates(Enum):
    FREE_PLACE = 0
    OCCUPIED_PLACE = 1
    RESERVED_PLACE = 2

class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GREY = (127, 127, 127)
    DARK_GREY = (180, 180, 180)
    BACKGROUND = BLACK

