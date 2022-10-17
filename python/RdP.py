import time
import macros_mapa as rdp
from decouple import config
from Enums import MapCellOccupationStates

# FIXME refactorizar esta clase en una que sea la RDP sola y conectado tenga la interfaz para con el mapa y hacia el monitor

class RdP:

    def __init__(self, map):

        self.__initialMark = rdp.MARCADO # FIXME esto se obtendria ahora desde un archivo
        self.__incidence = self.__fileRdPDefinitionRead()
        if(self.__incidence == None):
            print("ERROR RDP GENERATOR - Unable to get RDP definition file")
            # FIXME aca generar la red segun el mapa

        # check consistency of incidence and marking matrixes
        if(not self.__checkConsistency(self.__incidence, self.__initialMark)):
            print(f"ERROR - Inconsistent RDP\n")
            return

        self.__map = map
        self.__matrizEstado = []
        self.__matrizEstadoPrior = []
        self.__placesCount = len(self.__incidence)
        self.__transitionCount = len(self.__incidence[0])

        # create matrixes for dynamic state
        for i in range(0, self.__placesCount):
            self.__matrizEstado.append(self.__initialMark[i])
            self.__matrizEstadoPrior.append(0)

    def solicitudDisparo(self, transition):
        for i in range(0, self.__placesCount):
            if(self.__matrizEstado[i] + self.__incidence[i][transition] == -1):
                return 0
        return 1

    def redDisparar(self, transition, robotID):
        if(self.solicitudDisparo(transition)):
            for placeID in range(0, self.__placesCount):
                self.__matrizEstado[placeID] = self.__matrizEstado[placeID] + self.__incidence[placeID][transition]

                # check which places changed marking since last iteration
                if(self.__matrizEstado[placeID] != self.__matrizEstadoPrior[placeID]):
                    self.__updateMap(placeID, robotID)
                    self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]
            return 1
        return 0

    # def setRobotInPlace(self, placeID, robotID): # Forces the marking to set a robot in a place
    #     # FIXME agregar checkeo de existencia de placeID
    #     if(not self.__setOccupationInPlace(placeID) == 0):
    #         return -1

    #     self.__updateMap(placeID, robotID)
    #     return 0

    def setRobotInCoordinate(self, coordinate, robotID): # Forces the marking to set a robot in a place
        placeID = self.__map.getPlaceIDFromMapCoordinate(coordinate)

        if(placeID == None):
            print("ERROR GET PLACE ID FROM COORDINATE - No se pudo obtener el placeID con la coordenada")
            return

        # FIXME agregar checkeo de existencia de placeID
        if(not self.__setOccupationInPlace(placeID) == 0):
            return -1

        self.__updateMap(placeID, robotID)
        return 0
    

    def __setOccupationInPlace(self, placeID):
        if(placeID < 0 or placeID >= self.__placesCount or not placeID%2 == 0):
            return -1
        else:
            if(self.__matrizEstado[placeID + 1] > 0): # if there is room in the place - it checks the resource place
                self.__matrizEstado[placeID + 1] = self.__matrizEstado[placeID + 1] - 1
                self.__matrizEstado[placeID] = self.__matrizEstado[placeID] + 1
                self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]
                return 0
            else:
                return -1

    #def __getPlacesSequence(self, coordinatesSequence): # returns the places that the robot must go through to accomplish the place sequence
    #    return self.__map.getPlacesSequenceFromCoordinates(coordinatesSequence)

    #def getTransitionSequence(self, placeSequence): # returns the transitions that must be fired to accomplish the place sequence
    def getTransitionSequence(self, coordinatesSequence): # returns the transitions that must be fired to accomplish the coordinates sequence
        placeSequence = self.__map.getPlacesSequenceFromCoordinates(coordinatesSequence)

        if(placeSequence == None):
            print("ERROR SECUENCIA PLAZAS - No se pudo obtener la secuencia")
            return

        # FIXME agregar que checkee el largo del resultado para detectar discontinuidades en la secuencia - deberia haber X cantidad de transiciones para recorrer Y plazas
        transitionSeq = []
        for i in range(len(placeSequence)-1):
            # FIXME check existence?
            origen = placeSequence[i]
            destino = placeSequence[i+1]

            for j in range(self.getTransitionCount()):
                if(self.__incidence[origen][j] == -1 and self.__incidence[destino][j] == 1): # Explicacion: en el origen se "resta" un elemento porque el robot deja de estar aqui. Se "suma" 1 al destino para marcar que hay un robot
                    transitionSeq.append(j)
        return transitionSeq

    def __updateMap(self, placeID, robotID):
        if(placeID < 0 or placeID >= self.__placesCount or not placeID%2 == 0):
            return -1
        else:
            placeNewState = MapCellOccupationStates.OCCUPIED_PLACE if self.__matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE
            if(self.__map.updatePosition(placeID, placeNewState, robotID)):
                print(f"ERROR while trying to modify Map from RdP - Cell {placeID} is not occupable")

    def __checkConsistency(self, incidence, initialMark):

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
                print("ERROR DE INCONSISTENCIA RDP - Marcado Inicial debe definirse como enteros > 0")
                return False

        return True

    def __fileRdPDefinitionRead(self):
        # https://github.com/mrlaulearning/bloodDonors2DList/blob/master/bloodDonor.py
        rdpFile=open("rdpDefinition.txt","r") # FIXME hacer un define/config
        rdpDefinitionRead=eval(rdpFile.read())
        rdpFile.close()

        # FIXME check consistency
        #if(not self.__checkConsistency(rdpDefinitionRead)):
        #    rdpDefinitionRead = None

        return rdpDefinitionRead

    def printMarking(self):
        print("-------------------  MARCADO  -------------------");
        str = []
        str.append(time.time())
        for i in range(0, self.__placesCount):
            str.append(self.__matrizEstado[i])
        print(str)
        print()

    def getTransitionCount(self):
        return self.__transitionCount