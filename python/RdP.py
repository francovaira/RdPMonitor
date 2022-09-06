import time
from MapCellOccupationStates import MapCellOccupationStates

class RdP:

    #def __init__(self, placesCount, transitionCount, initialMark, incidence, pipeRdPTransmitter):
    def __init__(self, placesCount, transitionCount, initialMark, incidence, map):
        self.placesCount = placesCount
        self.transitionCount = transitionCount
        self.initialMark = initialMark
        self.incidence = incidence
        self.matrizEstado = []
        self.matrizEstadoPrior = []
        self.markingChangedPlaces = []
        self.map = map
        #self.pipeRdPTransmitter = pipeRdPTransmitter

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
                    self.matrizEstadoPrior[i] = self.matrizEstado[i]

            # update visualizer
            for placeID in self.markingChangedPlaces:
                #placeNewState = 1 if self.matrizEstado[placeID] != 0 else 0
                placeNewState = MapCellOccupationStates.OCCUPIED_PLACE if self.matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE
                posX, posY = self.__translatePlaceIDToPosition(placeID)
                #self.__updateVisualizerMap(posX, posY, placeNewState, id)
                if(self.__updateMap(posX, posY, placeNewState, id)):
                    print("ERROR while trying to modify Map from RdP")
            self.markingChangedPlaces.clear()

            return 1
        return 0

    #def __updateVisualizerMap(self, valueX, valueY, newState, id):
        # self.pipeRdPTransmitter.send([valueX, valueY, newState, id])

    def __updateMap(self, posX, posY, newState, id):
        return self.map.updatePosition(posX, posY, newState, id)

    def __translatePlaceIDToPosition(self, placeID):
        placeID = placeID // 2
        y = placeID // 3 + 1
        x = (y * 3) - placeID
        return x,y

    def printMarking(self):
        print("-------------------  MARCADO  -------------------");
        str = []
        str.append(time.time())
        for i in range(0, self.placesCount):
            str.append(self.matrizEstado[i])
        print(str)
        print()

