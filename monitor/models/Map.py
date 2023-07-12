import multiprocessing
from multiprocessing import Manager
from .PathFinderIntegrated import PathFinder
from .MapGenerator import MapGenerator
from Enums import MapCellOccupationStates, MapCellOccupationActions, MapCellTypes
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
        return self.__robotsList

    def addRobot(self, robotID):
        if(self.__isOccupable):
            if(any(elem == robotID for elem in self.__robotsList) or robotID == None or robotID == ""): # check for duplicates
                print(f"ERROR IN MAP CLASS - The robot <{robotID}> is trying to add another copy of itself into a cell <{self.__placeID}>")
            else:
                self.__robotsList.append(robotID)

    def removeRobot(self, robotID):
        if(robotID == None or robotID == ""):
            return
        elif(any(elem == robotID for elem in self.__robotsList)): # check existence
            self.__robotsList.remove(robotID)
        else:
            print(f"ERROR IN MAP CLASS - Trying to remove a robot {robotID} from a cell <{self.__placeID}> failed")

class Map:

    def __init__(self):
        self.__mapGenerator = MapGenerator()
        self.__mapDefinition = self.__mapGenerator.getMapDefinition()

        if(self.__mapDefinition == None):
            print("ERROR MAP CLASS - Unable to generate map")
            return

        self.__manager = multiprocessing.Manager() # https://maxinterview.com/code/shared-list-in-multiprocessing-python-F4DFE1E6CB141B9/
        self.__mapInSharedMemory = self.__manager.list() # https://docs.python.org/3.9/library/multiprocessing.html#multiprocessing.Manager
        self.__horizontalCells = self.__mapDefinition.getHorizontalSize()
        self.__verticalCells = self.__mapDefinition.getVerticalSize()
        self.__pathFinder = PathFinder(self.__mapDefinition)

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
                if(self.__mapDefinition.getMapStructure()[j][i] == macros_mapa.MAP_BORDER):
                    self.__mapInSharedMemory[i][j].setType(MapCellTypes.BORDER)
                elif(self.__mapDefinition.getMapStructure()[j][i] == macros_mapa.MAP_OBSTACLE):
                    self.__mapInSharedMemory[i][j].setType(MapCellTypes.OBSTACLE)
                elif(not self.__mapDefinition.getMapStructure()[j][i] == macros_mapa.MAP_OCCUPABLE):
                    print("ERROR map cell definition unknown")

        # Associate map cells with RdP places
        for i in range(self.__verticalCells-2):
           for j in range(self.__horizontalCells-2):
               self.__mapInSharedMemory[j+1][i+1].setPlaceID(self.__mapDefinition.getMapID()[j+1][i+1])

    def getMapDefinition(self):
        return self.__mapDefinition

    def getMapInSharedMemory(self):
        return self.__mapInSharedMemory

    def getPathFinder(self):
        return self.__pathFinder

    def updatePosition(self, placeID, occupationAction, robotID):
        posX, posY = self.getMapCoordinateFromPlaceID(placeID)
        if(not self.__mapInSharedMemory[posX][posY].getIsOccupable()):
            print(f"ERROR while trying to modify Map from RdP - Cell {placeID} is not occupable")
            return -1

        if(occupationAction != MapCellOccupationActions.DO_NOTHING):
            if(occupationAction == MapCellOccupationActions.ENTER_CELL):
                occupationState = MapCellOccupationStates.OCCUPIED_PLACE
                self.__mapInSharedMemory[posX][posY].addRobot(robotID)
            elif(occupationAction == MapCellOccupationActions.LEAVE_CELL):
                self.__mapInSharedMemory[posX][posY].removeRobot(robotID)
                if(len(self.__mapInSharedMemory[posX][posY].getOccupantsID())==0):
                    occupationState = MapCellOccupationStates.FREE_PLACE
                else:
                    occupationState = MapCellOccupationStates.OCCUPIED_PLACE
            elif(occupationAction == MapCellOccupationActions.RESERVE_CELL):
                occupationState = MapCellOccupationStates.RESERVED_PLACE
            self.__mapInSharedMemory[posX][posY].setOccupationState(occupationState)
        return 0

    def getMapCoordinateFromPlaceID(self, placeID):
        for i in range(self.__verticalCells-2):
            for j in range(self.__horizontalCells-2):
                if(self.__mapInSharedMemory[j+1][i+1].getPlaceID() == placeID):
                    return self.__mapInSharedMemory[j+1][i+1].getPosX(), self.__mapInSharedMemory[j+1][i+1].getPosY()
        return None

    def getPlaceIDFromMapCoordinate(self, coordinate):
        xPos = coordinate[0]
        yPos = coordinate[1]

        for i in range(self.__verticalCells-2):
            for j in range(self.__horizontalCells-2):
                if(xPos == self.__mapInSharedMemory[j+1][i+1].getPosX() and yPos == self.__mapInSharedMemory[j+1][i+1].getPosY()):
                    return self.__mapInSharedMemory[j+1][i+1].getPlaceID()
        return None

    def getPlacesSequenceFromCoordinates(self, coordinatesSequence):
        placeSequence = []
        for i in range(len(coordinatesSequence)):
            for x in range(self.__horizontalCells):
                for y in range(self.__verticalCells):
                    if(self.__mapInSharedMemory[x][y].getPosX() == coordinatesSequence[i][0] and self.__mapInSharedMemory[x][y].getPosY() == coordinatesSequence[i][1]):
                        placeSequence.append(self.__mapInSharedMemory[x][y].getPlaceID())
        return placeSequence




