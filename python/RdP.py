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

    def redDisparar(self, transition, id):
        if(self.solicitudDisparo(transition)):
            for i in range(0, self.placesCount):
                self.matrizEstado[i] = self.matrizEstado[i] + self.incidence[i][transition]

                # check which places changed marking since last iteration
                if(self.matrizEstado[i] != self.matrizEstadoPrior[i]):
                    if(i%2 == 0): # will update only occupancy places
                        self.__updateMap(i, id)
                    self.matrizEstadoPrior[i] = self.matrizEstado[i]
            return 1
        return 0

    def __updateMap(self, placeID, id):
        posX, posY = self.__translatePlaceIDToPosition(placeID)
        placeNewState = MapCellOccupationStates.OCCUPIED_PLACE if self.matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE
        if(self.map.updatePosition(posX, posY, placeNewState, id)):
            print("ERROR while trying to modify Map from RdP")

    def __translatePlaceIDToPosition(self, placeID):
        place = placeID // 2
        y = place // self.mapHorizontalSize
        x = place % self.mapVerticalSize
        return x,y

    def printMarking(self):
        print("-------------------  MARCADO  -------------------");
        str = []
        str.append(time.time())
        for i in range(0, self.placesCount):
            str.append(self.matrizEstado[i])
        print(str)
        print()

