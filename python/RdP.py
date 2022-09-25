import time
import macros_mapa as rdp
from decouple import config
from Enums import MapCellOccupationStates

class RdP:

    def __init__(self, map):
        self.initialMark = rdp.MARCADO
        self.incidence = rdp.INCIDENCIA
        self.matrizEstado = []
        self.matrizEstadoPrior = []
        self.map = map
        self.placesCount = len(rdp.INCIDENCIA)
        self.transitionCount = len(rdp.INCIDENCIA[0])
        self.mapHorizontalSize = int(config('MAP_HORIZONTAL_SIZE'))
        self.mapVerticalSize = int(config('MAP_VERTICAL_SIZE'))

        for i in range(0, self.placesCount):
            self.matrizEstado.append(self.initialMark[i])

        for i in range(0, self.placesCount):
            self.matrizEstadoPrior.append(0)

    def solicitudDisparo(self, transition):
        for i in range(0, self.placesCount):
            if(self.matrizEstado[i] + self.incidence[i][transition] == -1):
                return 0
        return 1

    def redDisparar(self, transition, robotID):
        if(self.solicitudDisparo(transition)):
            for placeID in range(0, self.placesCount):
                self.matrizEstado[placeID] = self.matrizEstado[placeID] + self.incidence[placeID][transition]

                # check which places changed marking since last iteration
                if(self.matrizEstado[placeID] != self.matrizEstadoPrior[placeID]):
                    self.__updateMap(placeID, robotID)
                    self.matrizEstadoPrior[placeID] = self.matrizEstado[placeID]
            return 1
        return 0

    def __updateMap(self, placeID, robotID):
        if(placeID%2 == 0): # will update only occupancy places
            placeNewState = MapCellOccupationStates.OCCUPIED_PLACE if self.matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE
            if(self.map.updatePosition(placeID, placeNewState, robotID)):
                print("ERROR while trying to modify Map from RdP")

    def printMarking(self):
        print("-------------------  MARCADO  -------------------");
        str = []
        str.append(time.time())
        for i in range(0, self.placesCount):
            str.append(self.matrizEstado[i])
        print(str)
        print()

