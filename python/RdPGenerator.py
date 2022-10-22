import macros_mapa

class RdPGenerator:
    def __init__(self, mapDefinition):
        self.__mapDefinition = mapDefinition
        self.__incidenceRows = 2*((self.__mapDefinition.getHorizontalSize()-2) * (self.__mapDefinition.getVerticalSize()-2)) # place count
        self.__incidenceColumns = 2*((self.__mapDefinition.getVerticalSize()-2-1)*(self.__mapDefinition.getHorizontalSize()-2) +
                                     (self.__mapDefinition.getHorizontalSize()-2-1)*(self.__mapDefinition.getVerticalSize()-2)) # transition count
        self.__initialMarkSize = self.__incidenceRows

        # create 2D array for the incidence matrix
        self.__incidence = [0 for i in range(self.__incidenceRows)]
        for i in range(self.__incidenceRows):
            self.__incidence[i] = [0 for j in range(self.__incidenceColumns)]

        self.calculateIncidence()
        self.calculateInitialMark()

    def getIncidence(self):
        return self.__incidence

    def getInitialMark(self):
        return self.__initialMark

    def calculateInitialMark(self):
        self.__initialMark = []

        for i in range(self.__mapDefinition.getHorizontalSize()-2):
            for j in range(self.__mapDefinition.getVerticalSize()-2):
                if(self.__mapDefinition.getMapStructure()[i+1][j+1] != macros_mapa.MAP_BORDER):
                    self.__initialMark.append(0) # occupation = 0
                    if(self.__mapDefinition.getMapStructure()[i+1][j+1] == macros_mapa.MAP_OCCUPABLE):
                        self.__initialMark.append(2)
                    else:
                        self.__initialMark.append(0)

        self.fileWrite(self.__initialMark, "initial_calculated.txt")

    def calculateIncidence(self):
        # given that petri net structure is based on having one resource place and one occupation place for each cell,
        # we need 2 places for each location in the map. The IDs are defined in such a way that even IDs always
        # refer to an occupation place and the odd IDs to a resoruce place, as well as in the incidence matrix.

        transitionIndex = 0
        # CREATE HORIZONTAL CONNECTIONS
        for i in range(self.__mapDefinition.getVerticalSize()-2):
            for j in range(self.__mapDefinition.getHorizontalSize()-2):
                if(self.__mapDefinition.getMapStructure()[j+1][i+1] != macros_mapa.MAP_BORDER and
                   self.__mapDefinition.getMapStructure()[j+2][i+1] != macros_mapa.MAP_BORDER):
                    idOccupationPlaceOrigin = 2*(j + i*(self.__mapDefinition.getHorizontalSize()-2))
                    idOccupationPlaceDestination = idOccupationPlaceOrigin + 2

                    self.__setIncidencePlaceXGotoY(self.__incidence, idOccupationPlaceOrigin, idOccupationPlaceDestination, transitionIndex)
                    transitionIndex = transitionIndex + 1
                    self.__setIncidencePlaceXGotoY(self.__incidence, idOccupationPlaceDestination, idOccupationPlaceOrigin, transitionIndex)
                    transitionIndex = transitionIndex + 1

        # CREATE VERTICAL CONNECTIONS
        for i in range(self.__mapDefinition.getHorizontalSize()-2):
            for j in range(self.__mapDefinition.getVerticalSize()-2):
                if(self.__mapDefinition.getMapStructure()[i+1][j+1] != macros_mapa.MAP_BORDER and
                   self.__mapDefinition.getMapStructure()[i+1][j+2] != macros_mapa.MAP_BORDER):
                    idOccupationPlaceOrigin = 2*(i + j*(self.__mapDefinition.getHorizontalSize()-2))
                    idOccupationPlaceDestination = 2*(i + (j+1)*(self.__mapDefinition.getHorizontalSize()-2))

                    self.__setIncidencePlaceXGotoY(self.__incidence, idOccupationPlaceOrigin, idOccupationPlaceDestination, transitionIndex)
                    transitionIndex = transitionIndex + 1
                    self.__setIncidencePlaceXGotoY(self.__incidence, idOccupationPlaceDestination, idOccupationPlaceOrigin, transitionIndex)
                    transitionIndex = transitionIndex + 1

        self.fileWrite(self.__incidence, "rdp_calculated.txt")

    def __setIncidencePlaceXGotoY(self, incidence, placeOrigin, placeDestination, transitionIndex): # FIXME hace transitionIndex++ por cada movimiento
        incidence[placeOrigin][transitionIndex] = -1 # FIXME hacer con valor que venga del .env o algo
        incidence[placeOrigin+1][transitionIndex] = 1
        incidence[placeDestination][transitionIndex] = 1
        incidence[placeDestination+1][transitionIndex] = -1

    def fileWrite(self, list2write, fileName):
        donorFile=open(fileName,"w")
        donorFile.write(str(list2write))
        donorFile.close()

