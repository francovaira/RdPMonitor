import time
from decouple import config
from .RdPGenerator import RdPGenerator
from Enums import MapCellOccupationStates, MapCellOccupationActions
import numpy as np

# FIXME refactorizar esta clase en una que sea la RDP sola y conectado tenga la interfaz para con el mapa y hacia el monitor

class RobotInRDPCell:
    def __init__(self, threadID):
        self.threadID = threadID
        self.isWaitingConfirmation = True

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

        # create a list for each transition to store threads waiting for confirmation - it will store RobotInRDPCell objects
        self.__threadsWaitingConfirmation = []
        for i in range(self.__transitionCount):
            self.__threadsWaitingConfirmation.append([])


    def solicitudDisparo(self, transition):
        for i in range(0, self.__placesCount):
            if(self.__matrizEstado[i] + self.__incidence[i][transition] == -1):
                return 0
        return 1

    def getSensibilizadas(self):
        sensibilizadas = []
        for transitionIndex in range(0, self.__transitionCount):
            if(self.solicitudDisparo(transitionIndex) > 0):
                sensibilizadas.append(transitionIndex)
        return sensibilizadas

    def redDisparar(self, transition, robotID):
        if(self.solicitudDisparo(transition)):
            for placeID in range(0, self.__placesCount):
                self.__matrizEstado[placeID] = self.__matrizEstado[placeID] + self.__incidence[placeID][transition]

                # check if place has changed marking since last iteration
                self.__checkChangeAndUpdateMap(placeID, robotID)
            return 1
        return 0

    def redDispararWaitConfirmation(self, transition, robotID):
        if(self.solicitudDisparo(transition)):

            # si esta habilitado para ejecutar la transicion (hay suficientes lugares libres en la celda destino), se bloquea hasta esperar confirmacion
            threadInCell = self.addRobotToCell(robotID, transition)

            if(threadInCell.isWaitingConfirmation == True):
                return 2 # FIXME aca deberia devolver un estado como "BLOQUEADO_ESPERANDO_CONFIRMACION"

            # si llego hasta aca es porque se desbloqueo y por ende puede terminar el disparo


            print(f'[RED_DE_PETRI] DISPARO EFECTIVOOOOOOO\n\n')
            for placeID in range(0, self.__placesCount):
                self.__matrizEstado[placeID] = self.__matrizEstado[placeID] + self.__incidence[placeID][transition]

                # check if place has changed marking since last iteration
                self.__checkChangeAndUpdateMap(placeID, robotID)
            return 1
        return 0

    def setCoordinateConfirmation(self, threadID, transition, confirmationValue):

        if(len(self.__threadsWaitingConfirmation[transition]) <= 0):
            print(f'ASDASDASDASD LISTA VACIA PARA LA TRANSICION <{transition}>\n')
            return -1

        print("[RED_DE_PETRI] inside (setCoordinateConfirmation)\n")

        for i in range(len(self.__threadsWaitingConfirmation[transition])):
            print(f'[RED_DE_PETRI] checking {self.__threadsWaitingConfirmation[transition][i].threadID} |||\n')
            if(self.__threadsWaitingConfirmation[transition][i].threadID == threadID):
                print("[RED_DE_PETRI] FOUND THREAD IN WAITING CONF LIST ...\n")

                self.__threadsWaitingConfirmation[transition][i].isWaitingConfirmation = confirmationValue
                print(f'SETTING CONFIRM ({confirmationValue}) OF TRANSITION EXECUTE {transition}\n')
                return 1
        return 0

    def addRobotToCell(self, threadID, transition):
        # retorna el objeto robot si lo encuentra en la lista o lo crea

        for i in range(len(self.__threadsWaitingConfirmation[transition])):
            if(self.__threadsWaitingConfirmation[transition][i].threadID == threadID):
                print(f'trying to add robot but exists. <{self.__threadsWaitingConfirmation[transition][i].threadID}>')
                return self.__threadsWaitingConfirmation[transition][i]

        self.__threadsWaitingConfirmation[transition].append(RobotInRDPCell(threadID))
        print(f'adding robot <{threadID}> to ({transition}) to wait for confirmation')
        return self.__threadsWaitingConfirmation[transition][len(self.__threadsWaitingConfirmation[transition])-1]

    def setRobotInCoordinate(self, coordinate, robotID): # Forces the marking to set a robot in a place
        placeID = self.__map.getPlaceIDFromMapCoordinate(coordinate)
        if(placeID == None):
            print("ERROR GET PLACE ID FROM COORDINATE - No se pudo obtener el placeID con la coordenada")
            return -1

        if(self.__setOccupationInPlace(placeID)):
            return -1
        if(self.__checkChangeAndUpdateMap(placeID, robotID)):
            return -1
        return 0

    def __setOccupationInPlace(self, placeID):
        if(placeID < 0 or placeID >= self.__placesCount or not placeID%2 == 0):
            return -1

        if(self.__matrizEstado[placeID + 1] > 0): # if there is room in the place - it checks the resource place
            self.__matrizEstado[placeID + 1] = self.__matrizEstado[placeID + 1] - 1
            self.__matrizEstado[placeID] = self.__matrizEstado[placeID] + 1
            return 0
        return -1

    def __checkChangeAndUpdateMap(self, placeID, robotID):
        if(placeID < 0 or placeID >= self.__placesCount or not placeID%2 == 0):
            return -1

        if(self.__matrizEstado[placeID] != self.__matrizEstadoPrior[placeID]):
            if(self.__updateMap(placeID, robotID)):
                return -1
            self.__matrizEstadoPrior[placeID] = self.__matrizEstado[placeID]
        return 0

    def getTransitionTranslation(self, transition):
        translation = []
        for placeIndex in range(self.__placesCount):
            if(placeIndex%2 == 0):
                if(self.__incidence[placeIndex][transition] == -1): # is initial position
                    translation.insert(0, self.__map.getMapCoordinateFromPlaceID(placeIndex))
                elif(self.__incidence[placeIndex][transition] == 1): # is end position
                    translation.insert(1, self.__map.getMapCoordinateFromPlaceID(placeIndex))

        if(len(translation) != 2):
            print(f"ERRORRRRR -- fallo la insercion de tranduccion // LENGTH {len(translation)}")
            return []
        return translation

    def getTransitionSequence(self, coordinatesSequence): # returns the transitions that must be fired to accomplish the coordinates sequence
        placeSequence = self.__map.getPlacesSequenceFromCoordinates(coordinatesSequence) # FIXME esta funcion capaz implementarla dentro de RdP.py
        if(len(placeSequence) == 0):
            print("ERROR - unable to get transition sequence")
            return None

        # FIXME agregar que checkee el largo del resultado para detectar discontinuidades en la secuencia - deberia haber X cantidad de transiciones para recorrer Y plazas
        transitionSeq = []
        for i in range(len(placeSequence)-1):
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
            if(self.__matrizEstado[placeID] > self.__matrizEstadoPrior[placeID]): # robot entered the cell
                placeOccupationAction = MapCellOccupationActions.ENTER_CELL
            elif(self.__matrizEstado[placeID] < self.__matrizEstadoPrior[placeID]): # robot left the cell
                placeOccupationAction = MapCellOccupationActions.LEAVE_CELL
            else:
                placeOccupationAction = MapCellOccupationActions.DO_NOTHING

            if(self.__map.updatePosition(placeID, placeOccupationAction, robotID)):
                return -1
            return 0

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

    def getMatrizEstado(self):
        incidencia = np.array(self.__rdpGen.getIncidence())
        return incidencia.sum(axis=0)