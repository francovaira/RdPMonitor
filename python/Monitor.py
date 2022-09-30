import threading
import time

class Monitor:

    def __init__(self, lock, petriNet):
        self.__monitorLock = lock
        self.__petriNet = petriNet
        self.__conditions = []
        self.__directRdPAccessCondition = threading.Condition(self.__monitorLock)
        self.__fireCount = 0

        # initialize conditions for transitions and their threads
        for i in range(0, self.__petriNet.getTransitionCount()):
            cond = threading.Condition(self.__monitorLock) # reference to the main lock
            self.__conditions.append(cond)

    def fireCountIncrement(self):
        self.__fireCount = self.__fireCount+1

    def monitorDisparar(self, transition, id):
        with self.__conditions[transition]:
            k = self.__petriNet.solicitudDisparo(transition)
            while(k == 0):
                #print(f"{time.time()} [{id}] ### No sensibilizada {transition} -- esperando...")
                self.__conditions[transition].wait() # espera que otro hilo lo despierte
                k = self.__petriNet.solicitudDisparo(transition)

            # disparar efectivamente - obtener el nuevo marcado
            self.__petriNet.redDisparar(transition, id)
            self.fireCountIncrement()
            print(f"{time.time()} [{id}] ### Si sensibilizada, disparo: {transition} __ CANT DISPAROS {self.__fireCount}")
            #self.__petriNet.printMarking()

        # notify for other conditions and potential waiting threads
        for i in range(0, self.__petriNet.getTransitionCount()):
            with self.__conditions[i]:
                self.__conditions[i].notify_all()

    def getTransitionSequence(self, placeSequence):
        return self.__petriNet.getTransitionSequence(placeSequence)

    def setRobotInPlace(self, placeID, robotID):
        with self.__directRdPAccessCondition:
            if(not self.__petriNet.setRobotInPlace(placeID, robotID) == 0):
                print("ERROR INSIDE MONITOR unable to set robot in place")
            self.__directRdPAccessCondition.notify_all()

