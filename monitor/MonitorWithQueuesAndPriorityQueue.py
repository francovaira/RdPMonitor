import threading
import time
from threading import Semaphore
import random

ITERATION_COUNT = 3 * 10000


class TransitionMonitorQueue:

    def __init__(self):
        self.__threadsRequesting = []
        self.__hasRequests = False
        self.__semaphore = threading.BoundedSemaphore()
        self.__semaphore.acquire()

    def request(self, threadID):
        if(any(elem == threadID for elem in self.__threadsRequesting) or threadID == None or threadID == ""): # check for duplicates
            print(f"ERROR IN MONITOR - The thread <{threadID}> is trying to request the transition again or has an empty thread ID") # creo que no necesariamente es un error
            pass
        else:
            self.__threadsRequesting.append(threadID)
            self.__hasRequests = True

    def releaseRequest(self, threadID):
        if(threadID == None or threadID == ""):
            return
        elif(any(elem == threadID for elem in self.__threadsRequesting)): # check existence
            self.__threadsRequesting.remove(threadID)

            if(len(self.__threadsRequesting) <= 0):
                self.__hasRequests = False
            else:
                self.__hasRequests = True
        else:
            print(f"ERROR IN MONITOR - The thread <{threadID}> tried to release the request but it was not a requesting member.")

    def getThreadsRequesting(self):
        return self.__threadsRequesting

    def getSemaphore(self):
        return self.__semaphore

    def hasRequests(self):
        return self.__hasRequests


class Policy:
    #def __init__(self):
    #    self.asfasdf = 5

    def resolve(self, candidates):
        return random.choice(candidates)

class MonitorWithQueuesAndPriorityQueue:

    def __init__(self, petriNet, pathFinder):
        self.__petriNet = petriNet
        self.__pathFinder = pathFinder
        self.__monitorLock = threading.Lock()
        self.__monitorEntranceLock = threading.Lock()
        self.__directRdPAccessCondition = threading.Condition(self.__monitorLock)
        self.__directPathFinderAccessCondition = threading.Condition(self.__monitorLock)
        self.__policy = Policy()
        self.__fireCount = 0
        self.__priorityThread = ""
        self.__accumLog = ""

        # create 1 queue for each RdP transition
        self.__transitionQueues = []
        for i in range(self.__petriNet.getTransitionCount()):
            self.__transitionQueues.append(TransitionMonitorQueue())

    def getAccumLog(self):
        return self.__accumLog

    def __fileWrite(self, list2write, fileName):
        writeFile=open(fileName,"w")
        writeFile.write(str(list2write))
        writeFile.close()

    def monitorDisparar(self, transition, threadID):

        if(self.__fireCount >= ITERATION_COUNT):
            self.__fileWrite(self.__accumLog, "LOG_OUTPUT.txt")
            print("Leaving...")
            exit()

        with self.__monitorEntranceLock:
            if(self.__priorityThread != "" and self.__priorityThread != threadID):
                #print(f"==== THREAD {threadID} || LIBERO EL LOCK DE ENTRADA, HAY ALGUIEN EN PRIORIDAD <{self.__priorityThread}> // CANT DISPAROS {self.__fireCount}")
                return False
            else:
                self.__monitorLock.acquire()
                if(self.__priorityThread != "" and self.__priorityThread != threadID):
                    self.__monitorLock.release()
                    #print(f"==== THREAD {threadID} || LIBERO EL LOCK, HAY ALGUIEN EN PRIORIDAD <{self.__priorityThread}> // CANT DISPAROS {self.__fireCount}")
                    return False

        try:
            k = True
            self.__transitionQueues[transition].request(threadID)
            #print(f"==== THREAD {threadID} || REQUESTED TRANSITION {transition}")
            #self.__accumLog = self.__accumLog + f"{threadID},'1',"
            self.__accumLog = self.__accumLog + f"{time.time()},{threadID},1\n"
            # REQ_TRANSITION = 1

            while(k == True):
                #self.__transitionQueues[transition].request(threadID)
                #print(f"==== THREAD {threadID} || REQUESTED TRANSITION {transition}")

                # 0) intenta disparar de una
                k = self.__petriNet.redDisparar(transition, threadID)
                if(k): # si pudo disparar, ...

                    if(self.__priorityThread == threadID):
                        #print(f"==== THREAD {threadID} || LA PRIORIDAD SOY YO, YA DISPARE Y CLEAR EL PRIORITY THREAD // CANT DISPAROS {self.__fireCount}")
                        self.__priorityThread = ""

                    self.__fireCountIncrement()
                    #print(f"==== THREAD {threadID} || PUDE DISPARAR LA TRANSICION {transition} // CANT DISPAROS {self.__fireCount}")
                    #self.__accumLog = self.__accumLog + f"{threadID},'2',"
                    self.__accumLog = self.__accumLog + f"{time.time()},{threadID},2\n"
                    # FIRED_TRANSITION = 2
                    self.__transitionQueues[transition].releaseRequest(threadID)
                    #print(f"==== THREAD {threadID} || UNREQUESTED TRANSITION {transition}")
                    #self.__accumLog = self.__accumLog + f"{threadID},'3',"
                    self.__accumLog = self.__accumLog + f"{time.time()},{threadID},3\n"
                    # UNREQ_TRANSITION = 3
                    # 1) obtener las sensibilizadas luego del cambio de estado
                    sensibilizadas = self.__petriNet.getSensibilizadas() # devuelve algo como [12, 4, 83, 67, ...]
                    #print(f"==== THREAD {threadID} || SENSIBILIZADAS DESPUES DEL DISPARO MONITOR - {sensibilizadas} // CANT DISPAROS {self.__fireCount}")
                    #self.__accumLog = self.__accumLog + f"{threadID},'4',"
                    self.__accumLog = self.__accumLog + f"{time.time()},{threadID},4\n"
                    # SENSI_TRANSITION = 4
                    if(len(sensibilizadas) > 0):

                        # 2) matchear sensibilizadas con colas de transiciones
                        transitionCandidates = self.__getTransitionCandidates(sensibilizadas)
                        #print(f"==== THREAD {threadID} || TRANSICIONES CANDIDATOS MONITOR - {transitionCandidates} // CANT DISPAROS {self.__fireCount}")
                        #self.__accumLog = self.__accumLog + f"{threadID},'5',"
                        self.__accumLog = self.__accumLog + f"{time.time()},{threadID},5\n"
                        # CANDI_TRANSITION = 5
                        # 3) si hay sensibilizadas con requests preguntar a la politica que transicion
                        if(len(transitionCandidates) > 0):
                            transitionDecision = self.__policy.resolve(transitionCandidates) # aca ver que hay que pasarle a la politica para que resuelva
                            #print(f"==== THREAD {threadID} || SOLUCION POLITICA MONITOR - {transitionDecision} // CANT DISPAROS {self.__fireCount}")
                            #self.__accumLog = self.__accumLog + f"{threadID},'10',"
                            self.__accumLog = self.__accumLog + f"{time.time()},{threadID},10\n"
                            #POLIC_TRANSITION = 10

                            if(self.__priorityThread != ""):
                                #print(f"==== THREAD {threadID} || WARNING!!!! OVERRIDING PRIORITY THREAD WITH {self.__transitionQueues[transitionDecision].getThreadsRequesting()[0]} // CANT DISPAROS {self.__fireCount}")
                                pass
                            self.__priorityThread = self.__transitionQueues[transitionDecision].getThreadsRequesting()[0]
                            #print(f"==== THREAD {threadID} || SETTING PRIORITY THREAD TO {self.__transitionQueues[transitionDecision].getThreadsRequesting()[0]} // CANT DISPAROS {self.__fireCount}")

                            # 4) se determino que debe ser la Tj, se pone un token en el semaforo de la transicion
                            self.__transitionQueues[transitionDecision].getSemaphore().release()
                            k=False # se va del monitor por haber disparado

                            # 5) me desencolo de la transicion porque ya dispare y me voy del monitor
                            #self.__transitionQueues[transitionDecision].releaseRequest(threadID)
                            #print(f"==== THREAD {threadID} || UNREQUESTED TRANSITION {transitionDecision}")
                        else:
                            # se va del monitor por no haber ninguna transicion con requests
                            k = False
                    else:
                        # se va del monitor por no haber ninguna transicion sensibilizada
                        k = False

                    # 5) me desencolo de la transicion porque ya dispare y me voy del monitor
                    #self.__transitionQueues[transition].releaseRequest(threadID)
                    #print(f"==== THREAD {threadID} || UNREQUESTED TRANSITION {transition}\n")
                    #print(f"\n")
                    #self.__accumLog = self.__accumLog
                    #self.__accumLog = self.__accumLog + f"{time.time()},{threadID},num\n"

                    return True
                else:
                    # put myself as thread into according queue
                    # importante, el thread solo se va a encolar en caso que haya intentado disparar la transicion pero no pudo
                    #print(f"==== THREAD {threadID} || TRANSICION NO SENSIBILIZADA, ME ENCOLO EN LA TRANSICION {transition}")
                    #self.__accumLog = self.__accumLog + f"{threadID},'20',"
                    self.__accumLog = self.__accumLog + f"{time.time()},{threadID},20\n"
                    # NSENS_TRANSITION = 20
                    self.__monitorLock.release()
                    self.__transitionQueues[transition].getSemaphore().acquire(blocking=True)
                    self.__monitorLock.acquire()
                    k=True

        finally:
            self.__monitorLock.release()


    def __getTransitionCandidates(self, sensibilizadas):
        transitionCandidates = []
        for i in range(len(sensibilizadas)):
            if(self.__transitionQueues[sensibilizadas[i]].hasRequests()):
                transitionCandidates.append(sensibilizadas[i])
        return transitionCandidates


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

