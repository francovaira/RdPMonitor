import time

class RdP:

    def __init__(self, placesCount, transitionCount, initialMark, incidence):
        self.placesCount = placesCount
        self.transitionCount = transitionCount
        self.initialMark = initialMark
        self.incidence = incidence
        self.matrizEstado = []
        self.matrizEstadoAux = []

        for i in range(0, self.placesCount):
            self.matrizEstado.append(self.initialMark[i])

        for i in range(0, self.placesCount):
            self.matrizEstadoAux.append(0)

    def solicitud_disparo(self, transition):
        for i in range(0, self.placesCount):
            self.matrizEstadoAux[i] = self.matrizEstado[i] + self.incidence[i][transition]
            if(self.matrizEstadoAux[i] == -1):
                return 0
        return 1

    def red_disparar(self, transition):
        if(self.solicitud_disparo(transition)):
            for i in range(0, self.placesCount):
                self.matrizEstado[i] = self.matrizEstadoAux[i]
            return 1
        return 0

    def print_marcado(self):
        print("-------------------  MARCADO  -------------------");
        str = []
        str.append(time.time())
        for i in range(0, self.placesCount):
            str.append(self.matrizEstado[i])
        print(str)
        print()

