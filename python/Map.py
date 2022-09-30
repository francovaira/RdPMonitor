import multiprocessing
from multiprocessing import Manager
from PathFinderIntegrated import PathFinder
from Enums import MapCellOccupationStates, MapCellTypes
import macros_mapa

class MapCell:
    def __init__(self, posX, posY):
        self.__placeID = None
        self.__posX = posX # these are the "ordinal" coordinates (only whole numbers)
        self.__posY = posY
        self.__cellWidth = 1 # must be expressed in meters
        self.__cellHeight = 1
        self.__xCoordinate = posX * self.__cellWidth # these are the "metric" coordinates, position in space (real numbers)
        self.__yCoordinate = posY * self.__cellHeight

        self.setType(MapCellTypes.OCCUPABLE)
        self.setOccupationState(MapCellOccupationStates.FREE_PLACE)

        self.__robotsList = [] # will store the IDs of all robots that are currently occupying this cell
        self.__robotsReservingCell = [] # will store the IDs of the robots that are currently reserving this cell
        self.__robotsRequestingCell = [] # will store the IDs of the robots that are currently wanting to enter this cell

    def getPosX(self):
        return self.__posX

    def getPosY(self):
        return self.__posY

    def setPlaceID(self, placeID):
        self.__placeID = placeID

    def getPlaceID(self):
        return self.__placeID

    def setType(self, cellType):
        self.__cellType = cellType
        self.__isOccupable = cellType.value[1]

    def getType(self):
        return self.__cellType

    def getIsOccupable(self):
        return self.__isOccupable

    def setOccupationState(self, occupationState):
        if(self.__isOccupable):
            self.__occupationState = occupationState
        else:
            self.__occupationState = None

    def getOccupationState(self):
        return self.__occupationState

    def getOccupantsID(self):
        return None if len(self.__robotsList) == 0 else self.__robotsList[0]

    def addRobot(self, robotID):
        if(self.__isOccupable):
            if(any(elem == robotID for elem in self.__robotsList) or robotID == None or robotID == ""): # check for duplicates
                return
            else:
                self.__robotsList.append(robotID)

    def removeRobot(self, robotID):
        if(robotID == None or robotID == ""):
            return
        elif(any(elem == robotID for elem in self.__robotsList)): # check existence
            self.__robotsList.remove(robotID)

class Map:

    def __init__(self, horizontalCells, verticalCells):
        self.__horizontalCells = horizontalCells
        self.__verticalCells = verticalCells
        self.__manager = multiprocessing.Manager() # https://maxinterview.com/code/shared-list-in-multiprocessing-python-F4DFE1E6CB141B9/
        self.__mapInSharedMemory = self.__manager.list() # https://docs.python.org/3.9/library/multiprocessing.html#multiprocessing.Manager
        self.__pathFinder = PathFinder(self.__verticalCells, self.__horizontalCells)

        # create 2D array for the grid (2D map) in shared memory
        self.__mapInSharedMemory = [0 for i in range(self.__horizontalCells)]
        for i in range(self.__horizontalCells):
            self.__mapInSharedMemory[i] = [0 for i in range(self.__verticalCells)]

        # Create cells for the map
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                self.__mapInSharedMemory[i][j] = MapCell(i, j)

        # Initialize cells with map definition
        for i in range(self.__horizontalCells):
            for j in range(self.__verticalCells):
                if(macros_mapa.MAPA[j][i] == macros_mapa.MAP_BORDER):
                    self.__mapInSharedMemory[i][j].setType(MapCellTypes.BORDER)
                elif(macros_mapa.MAPA[j][i] == macros_mapa.MAP_OBSTACLE):
                    self.__mapInSharedMemory[i][j].setType(MapCellTypes.OBSTACLE)
                elif(not macros_mapa.MAPA[j][i] == macros_mapa.MAP_OCCUPABLE):
                    print("ERROR map cell definition unknown")

        # Associate map cells with RdP places # FIXME esto despues deberia venir desde el archivo de definicion del mapa
        for i in range(self.__verticalCells-2):
            for j in range(self.__horizontalCells-2):
                self.__mapInSharedMemory[j+1][i+1].setPlaceID(2*(j+(i*(self.__horizontalCells-2))))

    def getMapInSharedMemory(self):
        return self.__mapInSharedMemory

    def getPathFinder(self):
        return self.__pathFinder

    def updatePosition(self, placeID, occupationState, robotID):
        posX, posY = self.__getMapPositionFromPlaceID(placeID)
        if(not self.__mapInSharedMemory[posX][posY].getIsOccupable()):
            return -1

        self.__mapInSharedMemory[posX][posY].setOccupationState(occupationState)
        if(occupationState == MapCellOccupationStates.FREE_PLACE):
            self.__mapInSharedMemory[posX][posY].removeRobot(robotID)
        elif(occupationState == MapCellOccupationStates.OCCUPIED_PLACE):
            self.__mapInSharedMemory[posX][posY].addRobot(robotID)
        return 0

    def __getMapPositionFromPlaceID(self, placeID):
        for i in range(self.__verticalCells-2):
            for j in range(self.__horizontalCells-2):
                if(self.__mapInSharedMemory[j+1][i+1].getPlaceID() == placeID):
                    return self.__mapInSharedMemory[j+1][i+1].getPosX(), self.__mapInSharedMemory[j+1][i+1].getPosY()
        return None

