import time
import macros_mapa as rdp
from decouple import config
from Enums import MapCellOccupationStates

class RdP:

    def __init__(self, map):
        self.__initialMark = rdp.MARCADO
        self.__incidence = rdp.INCIDENCIA
        self.__matrizEstado = []
        self.__matrizEstadoPrior = []
        self.__map = map
        self.__placesCount = len(rdp.INCIDENCIA)
        self.__transitionCount = len(rdp.INCIDENCIA[0])

        for i in range(0, self.__placesCount):
            self.__matrizEstado.append(self.__initialMark[i])

        for i in range(0, self.__placesCount):
            self.__matrizEstadoPrior.append(0)

    def getTransitionCount(self):
        return self.__transitionCount

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

    def __updateMap(self, placeID, robotID):
        if(placeID%2 == 0): # will update only occupancy places
            placeNewState = MapCellOccupationStates.OCCUPIED_PLACE if self.__matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE
            if(self.__map.updatePosition(placeID, placeNewState, robotID)):
                print(f"ERROR while trying to modify Map from RdP - Cell {placeID} is not occupable")

    def setRobotInPlace(self, placeID, robotID): # Forces the marking to set a robot in a place
        # FIXME agregar checkeo de placeID
        if(placeID < 0 or placeID >= self.__placesCount):
            return -1
        else:
            if(not self.__setOccupationInPlace(placeID) == 0):
                return -1

            self.__updateMap(placeID, robotID)
            return 0

    def getTransitionSequence(self, placeSequence): # returns the transitions that must be fired to accomplish the place sequence
        transitionSeq = []
        for i in range(len(placeSequence)-1):
            # FIXME check existence?
            origen = placeSequence[i]
            destino = placeSequence[i+1]

            #for j in range(len(rdp.INCIDENCIA[0])): # cantidad de transiciones
            for j in range(self.__transitionCount):
                if(rdp.INCIDENCIA[origen][j] == -1 and rdp.INCIDENCIA[destino][j] == 1): # Explicacion: en el origen se "resta" un elemento porque el robot deja de estar aqui. Se "suma" 1 al destino para marcar que hay un robot
                    transitionSeq.append(j)
        return transitionSeq

    def __setOccupationInPlace(self, placeID):
        if(not placeID%2 == 0):
            return -1
        else:
            if(self.__matrizEstado[placeID + 1] > 0): # if there is room in the place - it checks the resource place
                self.__matrizEstado[placeID + 1] = self.__matrizEstado[placeID + 1] - 1
                self.__matrizEstado[placeID] = self.__matrizEstado[placeID] + 1
                self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]
                return 0
            else:
                return -1

    def printMarking(self):
        print("-------------------  MARCADO  -------------------");
        str = []
        str.append(time.time())
        for i in range(0, self.__placesCount):
            str.append(self.__matrizEstado[i])
        print(str)
        print()
