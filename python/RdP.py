import time

class RdP:

    def __init__(self, placesCount, transitionCount, initialMark, incidence, pipeRdPTransmitter):
        self.placesCount = placesCount
        self.transitionCount = transitionCount
        self.initialMark = initialMark
        self.incidence = incidence
        self.matrizEstado = []
        #self.matrizEstadoAux = []
        self.matrizEstadoPrior = []
        self.markingChangedPlaces = []
        self.pipeRdPTransmitter = pipeRdPTransmitter

        for i in range(0, self.placesCount):
            self.matrizEstado.append(self.initialMark[i])

        for i in range(0, self.placesCount):
            #self.matrizEstadoAux.append(0)
            self.matrizEstadoPrior.append(0)

    # def solicitudDisparo(self, transition):
    #     for i in range(0, self.placesCount):
    #         self.matrizEstadoAux[i] = self.matrizEstado[i] + self.incidence[i][transition]
    #         if(self.matrizEstadoAux[i] == -1):
    #             return 0
    #     return 1

    def solicitudDisparo(self, transition):
        for i in range(0, self.placesCount):
            if(self.matrizEstado[i] + self.incidence[i][transition] == -1):
                return 0
        return 1

    def redDisparar(self, transition, id):
        if(self.solicitudDisparo(transition)):
            for i in range(0, self.placesCount):
                #self.matrizEstado[i] = self.matrizEstadoAux[i]
                self.matrizEstado[i] = self.matrizEstado[i] + self.incidence[i][transition]

                # check which places changed marking since last iteration
                if(self.matrizEstado[i] != self.matrizEstadoPrior[i]):
                    print(f"MARKING OF PLACE {i} CHANGED TO {self.matrizEstado[i]}")
                    if(i%2 == 0): # will update only occupancy places
                        self.markingChangedPlaces.append(i) # store places IDs
                    self.matrizEstadoPrior[i] = self.matrizEstado[i]

            # update visualizer
            for placeID in self.markingChangedPlaces:
                placeShow = 1 if self.matrizEstado[placeID] != 0 else 0
                posX, posY = self.__translatePlaceIDToPosition(placeID)
                self.__updateVisualizerMap(posX, posY, placeShow, id)
            self.markingChangedPlaces.clear()

            return 1
        return 0

    def __updateVisualizerMap(self, valueX, valueY, show, id):
        self.pipeRdPTransmitter.send([valueX, valueY, show, id])

    def __translatePlaceIDToPosition(self, placeID):
        placeID = placeID // 2
        y = placeID // 3 + 1
        x = (y * 3) - placeID
        return x,y

    def print_marcado(self):
        print("-------------------  MARCADO  -------------------");
        str = []
        str.append(time.time())
        for i in range(0, self.placesCount):
            str.append(self.matrizEstado[i])
        print(str)
        print()

