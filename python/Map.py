import multiprocessing
from multiprocessing import Manager
from Enums import MapCellOccupationStates, MapCellTypes

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

    def getPosX(self):
        return self.posX

    def getPosY(self):
        return self.posY

    def setType(self, cellType):
        #self.cellType = cellType.value[0]
        #self.isOccupable = cellType.value[1]
        self.cellType = cellType
        self.isOccupable = cellType.value[1]

    def getType(self):
        return self.cellType

    def setOccupationState(self, occupationState):
        if(self.isOccupable):
            #self.occupationState = occupationState.value # FIXME aca ver que onda con esto, se asigna un entero pero capaz deberia ser el mismo enum en si
            self.occupationState = occupationState
        else:
            self.occupationState = None

    def getOccupationState(self):
        return self.occupationState

    def getOccupantsID(self):
        return None if len(self.robotsList) == 0 else self.robotsList[0]

    def addRobot(self, robotID):
        if(self.isOccupable):
            if(any(elem == robotID for elem in self.robotsList)): # check for duplicates
                return
            else:
                self.robotsList.append(robotID)

    def removeRobot(self, robotID):
        if(any(elem == robotID for elem in self.robotsList)): # check existence
            self.robotsList.remove(robotID)

class Map:

    def __init__(self, horizontalCells, verticalCells):
        self.horizontalCells = horizontalCells # FIXME estas deberian provenir del archivo en si
        self.verticalCells = verticalCells
        self.manager = multiprocessing.Manager()
        self.mapInSharedMemory = self.manager.list()

        # create 2D array for the grid (2D map) in shared memory
        self.mapInSharedMemory = [0 for i in range(self.horizontalCells)]
        for i in range(self.horizontalCells):
            self.mapInSharedMemory[i] = [0 for i in range(self.verticalCells)]

        # Create cells for the map
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                self.mapInSharedMemory[i][j] = MapCell(i, j)

    def getMapInSharedMemory(self):
        return self.mapInSharedMemory

    def updatePosition(self, posX, posY, occupationState, id):
        if(posX >= self.horizontalCells or posY >= self.verticalCells or posX < 0 or posY < 0):
            return -1
        else:
            self.mapInSharedMemory[posX][posY].setOccupationState(occupationState)
            if(occupationState == MapCellOccupationStates.FREE_PLACE):
                self.mapInSharedMemory[posX][posY].removeRobot(id)
            elif(occupationState == MapCellOccupationStates.OCCUPIED_PLACE):
                self.mapInSharedMemory[posX][posY].addRobot(id)
            return 0
