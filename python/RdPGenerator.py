

import macros_mapa

RDP_READ_FROM_FILE                          = False     # True to read RdP definition from rdpDefinition.txt regardless of map structure, False will generate generic RdP
RDP_REGENERATE_IF_READ_FROM_FILE_FAILED     = True      # True to regenerate RdP if some of de RdP definition files are missing or inconsistent
RDP_WRITE_CALCULATED_RDP_TO_FILE            = True      # True to save generated RdP (incidence and initial marking) into a file

class RdPGenerator:

    def __init__(self, mapDefinition):
        self.__mapDefinition = mapDefinition
        self.__incidenceRows = 2*((self.__mapDefinition.getHorizontalSize()-2) * (self.__mapDefinition.getVerticalSize()-2)) # place count
        self.__incidenceColumns = 2*((self.__mapDefinition.getVerticalSize()-2-1)*(self.__mapDefinition.getHorizontalSize()-2) +
                                     (self.__mapDefinition.getHorizontalSize()-2-1)*(self.__mapDefinition.getVerticalSize()-2)) # transition count
        self.__initialMarkSize = self.__incidenceRows

        self.__incidence = []
        self.__initialMark = []

        if(RDP_READ_FROM_FILE):
            incidenceRead, initialMarkRead = self.__fileRdPDefinitionRead()
            if(len(incidenceRead) == 0 or len(initialMarkRead) == 0):
                print("ERROR RDP GENERATOR - Unable to get RDP definition file - RDP WILL BE REGENERATED FROM MAP DEFINITION")

                if(RDP_REGENERATE_IF_READ_FROM_FILE_FAILED):
                    if(self.__generateRdP()):
                        print(f"RDP GENERATOR - RDP REgenerated from map successfully\n")
                else:
                    print("PROGRAM WILL DO NOTHING! -- EXITING...")
                    exit()
            else:
                self.__incidence = incidenceRead
                self.__initialMark = initialMarkRead
                print("RDP FILE rdpDefinition.txt READ SUCCESSFULLY")
        else:
            if(self.__generateRdP()):
                print(f"RDP GENERATOR - RDP generated from map successfully\n")

    def getIncidence(self):
        return self.__incidence

    def getInitialMark(self):
        return self.__initialMark

    def __generateRdP(self):
        self.calculateIncidence()
        self.calculateInitialMark()

        # check consistency of incidence and marking matrixes
        if(not self.__checkConsistency(self.getIncidence(), self.getInitialMark())):
            print(f"ERROR IN RDP GENERATOR - Inconsistent GENERATED RDP\n")
            self.__incidence = []
            self.__initialMark = []
            return False
        return True

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

        if(RDP_WRITE_CALCULATED_RDP_TO_FILE):
            self.__fileWrite(self.__initialMark, "initial_calculated.txt")

    def calculateIncidence(self):
        # given that petri net structure is based on having one resource place and one occupation place for each cell,
        # we need 2 places for each location in the map. The IDs are defined in such a way that even IDs always
        # refer to an occupation place and the odd IDs to a resoruce place, as well as in the incidence matrix.

        # create 2D array for the incidence matrix
        self.__incidence = [0 for i in range(self.__incidenceRows)]
        for i in range(self.__incidenceRows):
            self.__incidence[i] = [0 for j in range(self.__incidenceColumns)]

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

        if(RDP_WRITE_CALCULATED_RDP_TO_FILE):
            self.__fileWrite(self.__incidence, "rdp_calculated.txt")

    def __setIncidencePlaceXGotoY(self, incidence, placeOrigin, placeDestination, transitionIndex): # FIXME hace transitionIndex++ por cada movimiento
        incidence[placeOrigin][transitionIndex] = -1 # FIXME hacer con valor que venga del .env o algo
        incidence[placeOrigin+1][transitionIndex] = 1
        incidence[placeDestination][transitionIndex] = 1
        incidence[placeDestination+1][transitionIndex] = -1

    def __checkConsistency(self, incidence, initialMark):

        # FIXME hacer todo en un solo for

        # check that initial marking count and incidence matrix row (place) count match
        if(len(incidence) != len(initialMark)):
            print("ERROR DE INCONSISTENCIA RDP - Marcado != Incidencia")
            return False

        # check that all rows are the same size
        lastLength = 0
        for i in range(len(incidence)):
            if(lastLength != len(incidence[i]) and i!=0):
                print("ERROR DE INCONSISTENCIA RDP - Largos de filas distintos")
                return False
            lastLength = len(incidence[i])

        # check that all elements in incidende matrix are numbers
        for i in range(len(incidence)):
            for j in range(len(incidence[i])):
                if(type(incidence[i][j]) != int or incidence[i][j]>10 or incidence[i][j]<-10): # FIXME hacer defines de las constantes
                    print("ERROR DE INCONSISTENCIA RDP - Incidencia debe definirse como enteros entre (-10, 10)")
                    return False

        # check that all elements in marking matrix are numbers
        for i in range(len(initialMark)):
            if(type(initialMark[i]) != int or initialMark[i]<0):
                print("ERROR DE INCONSISTENCIA RDP - Marcado Inicial debe definirse como enteros >= 0")
                return False

        return True

    def __fileRdPDefinitionRead(self):
        try:
            rdpFile=open("rdpDefinition.txt","r") # FIXME hacer un define/config
            rdpDefinitionRead=eval(rdpFile.read())
            rdpFile.close()
            
            initialMarkFile=open("initial_calculated.txt","r") # FIXME hacer un define/config
            initialMarkRead=eval(initialMarkFile.read())
            initialMarkFile.close()
        except:
            print("EXCEPTION - Unable to read RdP file")
            return [],[]

        if(not self.__checkConsistency(rdpDefinitionRead, initialMarkRead)):
            return [],[]

        return rdpDefinitionRead, initialMarkRead

    def __fileWrite(self, list2write, fileName):
        writeFile=open(fileName,"w")
        writeFile.write(str(list2write))
        writeFile.close()

