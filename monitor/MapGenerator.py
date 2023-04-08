import os
import macros_mapa

class MapDefinition:

    def __init__(self, mapDefinition):
        self.__mapDefinition = mapDefinition
        self.__horizontalCells = len(self.__mapDefinition[0]) # size with borders included
        self.__verticalCells = len(self.__mapDefinition) # size with borders included

        self.__idMap = [None for i in range(self.__horizontalCells)]
        for i in range(self.__horizontalCells):
            self.__idMap[i] = [None for i in range(self.__verticalCells)]

        for i in range(self.__verticalCells-2): # indexes are -2 because of borders
            for j in range(self.__horizontalCells-2):
                self.__idMap[j+1][i+1] = 2*(j+i*(self.__horizontalCells-2))
                # given that petri net structure is based on having one resource place and one occupation place for each cell,
                # we need 2 places for each location in the map. The IDs are defined in such a way that even IDs always
                # refer to an occupation place and the odd IDs to a resoruce place, as well as in the incidence matrix.

    def getMapID(self):
        return self.__idMap

    def getMapStructure(self):
        return self.__mapDefinition

    def getVerticalSize(self):
        return self.__verticalCells

    def getHorizontalSize(self):
        return self.__horizontalCells

class MapGenerator:

    def __init__(self):
        self.__mapDefinitionRead = self.__fileMapDefinitionRead()
        if(self.__mapDefinitionRead == None):
            print("ERROR MAP GENERATOR - Unable to get map definition file")
            # FIXME aca generar el mapa segun la configuracion

        self.__mapDefinition = MapDefinition(self.__mapDefinitionRead)

    def getMapDefinition(self):
        return self.__mapDefinition

    def __fileMapDefinitionRead(self):
        try:
            absolutePath = os.path.dirname(os.path.realpath(__file__)) # get the absolute path of the directory the script is in
            mapFilePath = os.path.join(absolutePath, "maps", "mapDefinition.txt") # construct the path to the file in the subdirectory # FIXME hacer un define/config
            mapFile=open(mapFilePath,"r")
            mapDefinitionRead=eval(mapFile.read())
            mapFile.close()
        except Exception as e:
            print(str(e))
            print("EXCEPTION - Unable to read Map definition from file")
            return []

        if(not self.__checkConsistency(mapDefinitionRead)):
            mapDefinitionRead = None

        return mapDefinitionRead

    def __checkConsistency(self, mapDefinition):

        # FIXME hacer todo en un solo for

        # check that map is a square or rectangle
        lastLength = 0
        for i in range(len(mapDefinition)):
            if(lastLength != len(mapDefinition[i]) and i!=0):
                print("ERROR DE INCONSISTENCIA DEFINICION DE MAPA - Largos de filas distintos")
                return False
            lastLength = len(mapDefinition[i])

        # check that all elements in map matrix are numbers
        for i in range(len(mapDefinition)):
            for j in range(len(mapDefinition[i])):
                if(type(mapDefinition[i][j]) != int):
                    print("ERROR DE INCONSISTENCIA DEFINICION DE MAPA - Mapa debe definirse como enteros")
                    return False

        # check that all elements are valid definitions
        for i in range(len(mapDefinition)):
            for j in range(len(mapDefinition[i])):
                if(mapDefinition[i][j] != macros_mapa.MAP_BORDER and mapDefinition[i][j] != macros_mapa.MAP_OBSTACLE and mapDefinition[i][j] != macros_mapa.MAP_OCCUPABLE):
                    print("ERROR DE INCONSISTENCIA DEFINICION DE MAPA - Mapa contiene definiciones invalidas")
                    return False

        return True

