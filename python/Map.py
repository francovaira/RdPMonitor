import multiprocessing
from multiprocessing import Manager
from Enums import MapCellOccupationStates, MapCellTypes
import macros_mapa

class MapCell:
    def __init__(self, posX, posY):
        self.placeID = None
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

    def setPlaceID(self, placeID):
        self.placeID = placeID

    def getPlaceID(self):
        return self.placeID

    def setType(self, cellType):
        self.cellType = cellType
        self.isOccupable = cellType.value[1]

    def getType(self):
        return self.cellType

    def getIsOccupable(self):
        return self.isOccupable

    def setOccupationState(self, occupationState):
        if(self.isOccupable):
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
        self.horizontalCells = horizontalCells
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

        # Initialize cells with map definition
        for i in range(self.horizontalCells):
            for j in range(self.verticalCells):
                if(macros_mapa.MAPA[j][i] == macros_mapa.MAP_BORDER):
                    self.mapInSharedMemory[i][j].setType(MapCellTypes.BORDER)
                elif(macros_mapa.MAPA[j][i] == macros_mapa.MAP_OBSTACLE):
                    self.mapInSharedMemory[i][j].setType(MapCellTypes.OBSTACLE)
                elif(not macros_mapa.MAPA[j][i] == macros_mapa.MAP_OCCUPABLE):
                    print("ERROR map cell definition unknown")

        # Associate map cells with RdP places # FIXME esto despues deberia venir desde el archivo de definicion del mapa
        for i in range(self.verticalCells-2):
            for j in range(self.horizontalCells-2):
                self.mapInSharedMemory[j+1][i+1].setPlaceID(2*(j+(i*(self.horizontalCells-2))))

    def getMapInSharedMemory(self):
        return self.mapInSharedMemory

    def updatePosition(self, placeID, occupationState, robotID):
        posX, posY = self.__getMapPositionFromPlaceID(placeID)
        if(not self.mapInSharedMemory[posX][posY].getIsOccupable()):
            return -1

        self.mapInSharedMemory[posX][posY].setOccupationState(occupationState)
        if(occupationState == MapCellOccupationStates.FREE_PLACE):
            self.mapInSharedMemory[posX][posY].removeRobot(robotID)
        elif(occupationState == MapCellOccupationStates.OCCUPIED_PLACE):
            self.mapInSharedMemory[posX][posY].addRobot(robotID)
        return 0

    def __getMapPositionFromPlaceID(self, placeID):
        for i in range(self.verticalCells-2):
            for j in range(self.horizontalCells-2):
                if(self.mapInSharedMemory[j+1][i+1].getPlaceID() == placeID):
                    return self.mapInSharedMemory[j+1][i+1].getPosX(), self.mapInSharedMemory[j+1][i+1].getPosY()
        return None

