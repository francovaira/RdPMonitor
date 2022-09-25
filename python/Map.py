import multiprocessing
from multiprocessing import Manager
from Enums import MapCellOccupationStates, MapCellTypes

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
        self.horizontalCells = horizontalCells + 2 # FIXME estas deberian provenir del archivo en si
        self.verticalCells = verticalCells + 2
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

        # Define map obstacles # FIXME esto deberia venir desde el archivo de defincion del mapa
        for i in range(self.verticalCells-5):
            self.mapInSharedMemory[2][i+2].setType(MapCellTypes.OBSTACLE)
            self.mapInSharedMemory[3][i+2].setType(MapCellTypes.OBSTACLE)

        for i in range(self.verticalCells-5):
            self.mapInSharedMemory[5][i+2].setType(MapCellTypes.OBSTACLE)
            self.mapInSharedMemory[6][i+2].setType(MapCellTypes.OBSTACLE)

        # Define borders
        for i in range(self.horizontalCells):
            self.mapInSharedMemory[i][0].setType(MapCellTypes.BORDER)
            self.mapInSharedMemory[i][self.verticalCells-1].setType(MapCellTypes.BORDER)

        for i in range(self.verticalCells):
            self.mapInSharedMemory[0][i].setType(MapCellTypes.BORDER)
            self.mapInSharedMemory[self.horizontalCells-1][i].setType(MapCellTypes.BORDER)

        # Associate map cells with RdP places
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
        #place = placeID // 2
        #y = (place // (self.horizontalCells-2))+1
        #x = (place % (self.verticalCells-2)+1)
        for i in range(self.verticalCells-2):
            for j in range(self.horizontalCells-2):
                if(self.mapInSharedMemory[j+1][i+1].getPlaceID() == placeID):
                    return self.mapInSharedMemory[j+1][i+1].getPosX(), self.mapInSharedMemory[j+1][i+1].getPosY()
        return None

