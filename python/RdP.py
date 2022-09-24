import time
import macros_mapa as rdp
from decouple import config
from MapCellOccupationStates import MapCellOccupationStates

class RdP:

    def __init__(self, map):
        self.initialMark = rdp.MARCADO
        self.incidence = rdp.INCIDENCIA
        self.matrizEstado = []
        self.matrizEstadoPrior = []
        self.markingChangedPlaces = []
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
                        self.markingChangedPlaces.append(i) # store places IDs
                    self.matrizEstadoPrior[i] = self.matrizEstado[i] # FIXME capaz meter aca adentro la actualizacion del mapa, para no crear otra lista al pepe

            # update visualizer // FIXME refactorizar
            for placeID in self.markingChangedPlaces:
                placeNewState = MapCellOccupationStates.OCCUPIED_PLACE if self.matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE
                posX, posY = self.__translatePlaceIDToPosition(placeID)
                if(self.__updateMap(posX, posY, placeNewState, id)):
                    print("ERROR while trying to modify Map from RdP")
            self.markingChangedPlaces.clear()
            return 1
        return 0

    def __updateMap(self, posX, posY, newState, id):
        return self.map.updatePosition(posX, posY, newState, id)

    def __translatePlaceIDToPosition(self, placeID):
        place = placeID // len(self.markingChangedPlaces)
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

