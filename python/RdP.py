import time
from decouple import config
from RdPGenerator import RdPGenerator
from Enums import MapCellOccupationStates, MapCellOccupationActions

# FIXME refactorizar esta clase en una que sea la RDP sola y conectado tenga la interfaz para con el mapa y hacia el monitor

class RdP:

    def __init__(self, map):
        self.__rdpGen = RdPGenerator(map.getMapDefinition())
        self.__incidence = self.__rdpGen.getIncidence()
        self.__initialMark = self.__rdpGen.getInitialMark()

        if(self.__incidence == None or self.__initialMark == None):
            print("ERROR RDP CLASS - Unable to generate RdP")
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

                # FIXME refactorizar, capaz meter todo en una sola funcion
                # check which places changed marking since last iteration
                #if(self.__matrizEstado[placeID] != self.__matrizEstadoPrior[placeID]):
                #    self.__updateMap(placeID, robotID)
                #    self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]
                self.checkChangeAndUpdateMap(placeID, robotID)
            return 1
        return 0

    def setRobotInCoordinate(self, coordinate, robotID): # Forces the marking to set a robot in a place
        placeID = self.__map.getPlaceIDFromMapCoordinate(coordinate)
        if(placeID == None):
            print("ERROR GET PLACE ID FROM COORDINATE - No se pudo obtener el placeID con la coordenada")
            return

        if(not self.__setOccupationInPlace(placeID) == 0):
            return -1
        self.checkChangeAndUpdateMap(placeID, robotID)
        #self.__updateMap(placeID, robotID)
        #self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]
        return 0

    def __setOccupationInPlace(self, placeID):
        if(placeID < 0 or placeID >= self.__placesCount or not placeID%2 == 0):
            return -1
        else:
            if(self.__matrizEstado[placeID + 1] > 0): # if there is room in the place - it checks the resource place
                self.__matrizEstado[placeID + 1] = self.__matrizEstado[placeID + 1] - 1
                self.__matrizEstado[placeID] = self.__matrizEstado[placeID] + 1
                #self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]
                #FIXME esto tendria que actualizarse en otro lado para que no tenga el bug de que trata de remover un robot que aun no se agrego
                return 0
            else:
                return -1

    def checkChangeAndUpdateMap(self, placeID, robotID):
        if(placeID < 0 or placeID >= self.__placesCount or not placeID%2 == 0):
            return -1

        if(self.__matrizEstado[placeID] != self.__matrizEstadoPrior[placeID]):
            self.__updateMap(placeID, robotID)
            self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]

    def getTransitionSequence(self, coordinatesSequence): # returns the transitions that must be fired to accomplish the coordinates sequence
        placeSequence = self.__map.getPlacesSequenceFromCoordinates(coordinatesSequence) # FIXME esta funcion capaz implementarla dentro de RdP.py
        if(placeSequence == None):
            print("ERROR SECUENCIA PLAZAS - No se pudo obtener la secuencia")
            return None

        #print(f"PLACE SEQUENCE {placeSequence}")

        # FIXME agregar que checkee el largo del resultado para detectar discontinuidades en la secuencia - deberia haber X cantidad de transiciones para recorrer Y plazas
        transitionSeq = []
        for i in range(len(placeSequence)-1):
            # FIXME check existence?
            origen = placeSequence[i]
            destino = placeSequence[i+1]

            for j in range(self.getTransitionCount()):
                if(self.__incidence[origen][j] == -1 and self.__incidence[destino][j] == 1 and
                   self.__incidence[origen+1][j] == 1 and self.__incidence[destino+1][j] == -1): # Explicacion: en el origen se "resta" un elemento porque el robot deja de estar aqui. Se "suma" 1 al destino para marcar que hay un robot
                    transitionSeq.append(j)
        return transitionSeq

    def __updateMap(self, placeID, robotID):
        if(placeID < 0 or placeID >= self.__placesCount or not placeID%2 == 0):
            return -1
        else:
            #placeOccupationAction = MapCellOccupationStates.OCCUPIED_PLACE if self.__matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE
            #placeOccupationAction = MapCellOccupationStates.OCCUPIED_PLACE if self.__matrizEstado[placeID] != 0 else MapCellOccupationStates.FREE_PLACE 
            if(self.__matrizEstado[placeID] > self.__matrizEstadoPrior[placeID]): # robot entered the cell
                #placeOccupationAction = MapCellOccupationStates.OCCUPIED_PLACE
                placeOccupationAction = MapCellOccupationActions.ENTER_CELL
            elif(self.__matrizEstado[placeID] < self.__matrizEstadoPrior[placeID]): # robot left the cell
                #placeOccupationAction = MapCellOccupationStates.FREE_PLACE
                placeOccupationAction = MapCellOccupationActions.LEAVE_CELL
                print(f"PLACE ID <{placeID}> / MATRIZ ESTADO <{self.__matrizEstado[placeID]}> / PRIOR <{self.__matrizEstadoPrior[placeID]}>")
            else:
                placeOccupationAction = MapCellOccupationActions.DO_NOTHING
            #FIXME el bug de que no elimina bien los ID de una celda esta ACA. Se da porque cuando una celda tiene 2 robots y uno se va, la condicion de arriba se cumple, por lo
            # que el estado que le pasa a la updatePosition es un occupied pero con el ID del robot que se esta yendo. Para solucionarlo se podria hacer que le pase
            # una transicion de estado o ver como hacer para casos donde tengo mas de un robot en una celda y notificar que un robot se esta yendo
            if(self.__map.updatePosition(placeID, placeOccupationAction, robotID)):
                print(f"ERROR while trying to modify Map from RdP - Cell {placeID} is not occupable")

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

