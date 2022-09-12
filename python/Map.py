from enum import Enum
from MapCellOccupationStates import MapCellOccupationStates

class MapCellTypes(Enum): # they have the format (enumID, isOccupable)
    BORDER = (0, False)
    OBSTACLE = (1, False)
    OCCUPABLE = (2, True)

class MapCell:
    def __init__(self, posX, posY):
        self.posX = posX # these are the "ordinal" coordinates (only whole numbers)
        self.posY = posY
        self.cellWidth = 1 # must be expressed in meters
        self.cellHeight = 1
        self.xCoordinate = posX * self.cellWidth # these are the "metric" coordinates, position in space (real numbers)
        self.yCoordinate = posY * self.cellHeight

        self.setType(MapCellTypes.OCCUPABLE)
        self.setOccupationState(MapCellOccupationStates.FREE_PLACE)

        self.robotsList = [] # will store the IDs of all robots that are currently occupying this cell
        self.robotsReservingCell = [] # will store the IDs of the robots that are currently reserving this cell
        self.robotsRequestingCell = [] # will store the IDs of the robots that are currently wanting to enter this cell

    def setType(self, cellType):
        self.cellType = cellType.value[0]
        self.isOccupable = cellType.value[1]

    def setOccupationState(self, occupationState):
        if(self.isOccupable):
            self.occupationState = occupationState.value
        else:
            self.occupationState = None

    def addRobot(self, robotID):
        if(self.isOccupable):
            if(any(elem == robotID for elem in self.robotsList)): # check for duplicates
                return
            else:
                self.robotsList.append(robotID)

    def removeRobot(self, robotID):
        if(self.isOccupable):
            if(any(elem == robotID for elem in self.robotsList)): # check existence
                self.robotsList.remove(robotID)

class Map:

    def __init__(self, horizontalCells, verticalCells, pipeMap2VisualizerTX):
        self.horizontalCells = horizontalCells # FIXME estas deberian provenir del archivo en si
        self.verticalCells = verticalCells
        self.pipeMap2VisualizerTX = pipeMap2VisualizerTX

        # create 2D array for the grid (2D map)
        self.gridMap = [0 for i in range(self.horizontalCells)]
        for i in range(self.horizontalCells):
            self.gridMap[i] = [0 for i in range(self.verticalCells)]

        # Create cells for the map
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.gridMap[i][j] = MapCell(i, j)

    def updatePosition(self, posX, posY, occupationState, id):
        # FIXME agregar checkeo de limites
        self.gridMap[posX][posY].setOccupationState(occupationState)
        self.pipeMap2VisualizerTX.send([posX, posY, occupationState.value, id])
        return 0