import macros_mapa

class MapDefinition:

    def __init__(self, mapDefinition):
        self.__mapDefinition = mapDefinition
        self.__horizontalCells = 0
        self.__verticalCells = 0

        self.__horizontalCells = len(self.__mapDefinition[0])
        self.__verticalCells = len(self.__mapDefinition)

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
            mapFile=open("mapDefinition.txt","r") # FIXME hacer un define/config
            mapDefinitionRead=eval(mapFile.read())
            mapFile.close()

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