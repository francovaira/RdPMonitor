import threading
from threading import Lock
import time

class Monitor:

    def __init__(self, petriNet, pathFinder):
        self.__monitorLock = threading.Lock()
        self.__petriNet = petriNet
        self.__pathFinder = pathFinder
        self.__conditions = []
        self.__directRdPAccessCondition = threading.Condition(self.__monitorLock)
        self.__directPathFinderAccessCondition = threading.Condition(self.__monitorLock)
        self.__fireCount = 0

        # initialize conditions for transitions and their threads
        for i in range(0, self.__petriNet.getTransitionCount()):
            cond = threading.Condition(self.__monitorLock) # reference to the main lock
            self.__conditions.append(cond)

    def monitorDisparar(self, transition, robotID):
        with self.__conditions[transition]:
            k = self.__petriNet.solicitudDisparo(transition)
            while(k == 0):
                print(f"{time.time()} [{robotID}] ### No sensibilizada {transition} -- esperando...")
                self.__conditions[transition].wait() # espera que otro hilo lo despierte
                k = self.__petriNet.solicitudDisparo(transition)

            # disparar efectivamente - obtener el nuevo marcado
            self.__petriNet.redDisparar(transition, robotID)
            self.__fireCountIncrement()
            print(f"{time.time()} [{robotID}] ### Si sensibilizada, disparo: {transition} __ CANT DISPAROS {self.__fireCount}")
            #self.__petriNet.printMarking()

        # print(f"{time.time()} [{robotID}] ### Transitions Count: {self.__petriNet.getTransitionCount()}")
        print(self.__petriNet.getMatrizEstado())
        # time.sleep(45)
        # notify for other conditions and potential waiting threads
        for i in range(0, self.__petriNet.getTransitionCount()):
            with self.__conditions[i]:
                self.__conditions[i].notify_all()

    def getTransitionSequence(self, coordinatesSequence):
        with self.__directRdPAccessCondition:
            transitionSequence = self.__petriNet.getTransitionSequence(coordinatesSequence)
            self.__directRdPAccessCondition.notify_all() # FIXME checkear si el with ya lo hace o no
        return transitionSequence

    def setRobotInCoordinate(self, coordinate, robotID):
        with self.__directRdPAccessCondition:
            if(self.__petriNet.setRobotInCoordinate(coordinate, robotID)):
                print("ERROR INSIDE MONITOR unable to set robot in coordinate")
            self.__directRdPAccessCondition.notify_all()

    def calculatePath(self, startX, startY, endX, endY):
        with self.__directPathFinderAccessCondition:
            pathCoordinates = self.__pathFinder.calculatePath(startX, startY, endX, endY)
            self.__directPathFinderAccessCondition.notify_all() # FIXME checkear si el with ya lo hace o no
        return pathCoordinates

    def __fireCountIncrement(self):
        self.__fireCount = self.__fireCount+1

