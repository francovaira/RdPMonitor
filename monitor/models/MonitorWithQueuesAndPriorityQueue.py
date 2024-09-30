import threading
import time
from threading import Semaphore
from enum import Enum
import random

ITERATION_COUNT = 3 * 10000

TIMEOUT_THREAD_WAITING = 10

class MonitorReturnStatus(Enum):
    SUCCESSFUL_FIRING = 0
    UNABLE_TO_FIRE = 1
    SUCCESSFUL_REQUEST_WAITING_CONFIRMATION = 2
    TIMEOUT_WAITING_BLOCKED = 3

class TransitionMonitorQueue:

    def __init__(self):
        self.__threadsRequesting = []
        self.__hasRequests = False
        self.__semaphore = threading.BoundedSemaphore()
        self.__semaphore.acquire()

    def request(self, threadID):
        if(any(elem == threadID for elem in self.__threadsRequesting) or threadID == None or threadID == ""): # check for duplicates
            #print(f"ERROR IN MONITOR - The thread <{threadID}> is trying to request the transition again or has an empty thread ID")
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

class PathRecalculationPolicy:
    #def __init__(self):
    #    self.asfasdf = 5

    def resolve(self, candidates):
        return random.choice(candidates)

class ThreadBlocked:
    def __init__(self, threadID, transition, transitionTranslated):
        self.transition = transition
        self.threadID = threadID
        self.transitionTranslated = transitionTranslated
        self.mustRecalculatePath = False


class MonitorWithQueuesAndPriorityQueue:

    def __init__(self, petriNet, pathFinder):
        self.__petriNet = petriNet
        self.__pathFinder = pathFinder
        self.__monitorLock = threading.Lock()
        self.__monitorEntranceLock = threading.Lock()
        self.__directRdPAccessCondition = threading.Condition(self.__monitorLock)
        self.__directPathFinderAccessCondition = threading.Condition(threading.Lock())
        self.__policy = Policy()
        self.__pathRecalculationPolicy = PathRecalculationPolicy()
        self.__threadsInConflict = []
        self.__fireCount = 0
        self.__priorityThread = ""
        self.__blockedThreadsQueue = [] # en esta cola se ponen los hilos que intentaron disparar una transicion y no pudieron, junto con la info de la transicion que no pudo disparar
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
            #self.__fileWrite(self.__accumLog, "LOG_OUTPUT.txt")
            print("Leaving...")
            exit()

        with self.__monitorEntranceLock:
            if(self.__priorityThread != "" and self.__priorityThread != threadID):
                return MonitorReturnStatus.UNABLE_TO_FIRE
            else:
                self.__monitorLock.acquire()
                if(self.__priorityThread != "" and self.__priorityThread != threadID):
                    self.__monitorLock.release()
                    return MonitorReturnStatus.UNABLE_TO_FIRE

        try:
            k = True
            self.__transitionQueues[transition].request(threadID)

            while(k == True):
                # k = self.__petriNet.redDisparar(transition, threadID)
                k = self.__petriNet.redDispararWaitConfirmation(transition, threadID)

                if(k == 2): # esta bloqueado esperando la confirmacion de disparo, me voy del monitor
                    return MonitorReturnStatus.SUCCESSFUL_REQUEST_WAITING_CONFIRMATION

                #if(k):
                elif(k == 1): # pudo disparar

                    if(self.__priorityThread == threadID):
                        self.__priorityThread = ""

                    if(self.__threadBlockedExistsInList(threadID, self.__blockedThreadsQueue)): # si ya dispare y estaba en la cola de bloqueados, me voy
                        for thrBlocked in self.__blockedThreadsQueue:
                            if(thrBlocked.threadID == threadID):
                                self.__blockedThreadsQueue.remove(thrBlocked)

                    self.__fireCountIncrement()

                    # 0.5) me desencolo de la transicion porque ya dispare
                    self.__transitionQueues[transition].releaseRequest(threadID)

                    # 1) obtener las sensibilizadas luego del cambio de estado
                    sensibilizadas = self.__petriNet.getSensibilizadas() # devuelve algo como [12, 4, 83, 67, ...]

                    if(len(sensibilizadas) > 0):

                        # 2) matchear sensibilizadas con colas de transiciones
                        transitionCandidates = self.__getTransitionCandidates(sensibilizadas)

                        # 3) si hay sensibilizadas con requests preguntar a la politica que transicion
                        if(len(transitionCandidates) > 0):
                            transitionDecision = self.__policy.resolve(transitionCandidates) # aca ver que hay que pasarle a la politica para que resuelva
                            self.__priorityThread = self.__transitionQueues[transitionDecision].getThreadsRequesting()[0]

                            # 4) se determino que debe ser la Tj, se pone un token en el semaforo de la transicion
                            self.__transitionQueues[transitionDecision].getSemaphore().release()
                            k = False # se va del monitor por haber disparado
                        else:
                            k = False # se va del monitor por no haber ninguna transicion con requests
                    else:
                        k = False # se va del monitor por no haber ninguna transicion sensibilizada

                    return MonitorReturnStatus.SUCCESSFUL_FIRING
                else:
                    # put myself as thread into according queue
                    # importante, el thread solo se va a encolar en caso que haya intentado disparar la transicion pero no pudo
                    print(f"==== THREAD {threadID} || TRANSICION NO SENSIBILIZADA, ME ENCOLO EN LA TRANSICION {transition}")

                    # decide por politica quien recalcula -- el que recalcula se le cambian las transiciones, sale del monitor y se va a recalcular y pelear por otras transiciones (no deberia bloquearse en la transicion actual, tiene que obtener una nueva por haber recalculado)
                    # el que no recalcula debe bloquearse hasta que el que recalcula se mueva -- en definitiva haria el acquire

                    if(not self.__threadBlockedExistsInList(threadID, self.__blockedThreadsQueue)):
                        # the loop completed without finding an object with the given name, the object does not exist in the list
                        newThreadBlocked = ThreadBlocked(threadID, transition, self.__getTransitionTranslation(transition))
                        self.__blockedThreadsQueue.append(newThreadBlocked)

                    elif(self.__threadBlockedExistsInList(threadID, self.__threadsInConflict)): # si me desperte y resulta que debo recalcular
                        for threadBlockedInList in self.__threadsInConflict:
                            if(threadBlockedInList.threadID == threadID and threadBlockedInList.mustRecalculatePath):
                                self.__transitionQueues[transition].releaseRequest(threadID)
                                self.__threadsInConflict = []
                                return MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED

                    isConflict, threadInConflictA, threadInConflictB = self.__checkConflict(self.__blockedThreadsQueue)
                    if(isConflict == True):
                        self.__threadsInConflict.append(threadInConflictA)
                        self.__threadsInConflict.append(threadInConflictB)

                        threadDecision = self.__pathRecalculationPolicy.resolve(self.__threadsInConflict) # decide que thread debe recalcular

                        threadDecision.mustRecalculatePath = True
                        if(threadDecision.threadID == threadID): # si la politica decidio por mi que debo recalcular
                            if(self.__priorityThread == threadID): # me debo sacar de la lista de prioridad si estoy
                                self.__priorityThread = ""
                            self.__transitionQueues[transition].releaseRequest(threadID)
                            self.__threadsInConflict = [] # conflict "solved"
                            return MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED
                        else:
                            self.__transitionQueues[threadDecision.transition].getSemaphore().release() # puedo asumir que el robot por el que decidio la politica esta bloqueado en algun acquire para la transicion que queria. debo ponerle un token para que se despierte
                            self.__monitorLock.release()
                            self.__transitionQueues[transition].getSemaphore().acquire(blocking=True)
                            self.__monitorLock.acquire()
                            k = True
                    else:
                        self.__monitorLock.release()
                        self.__transitionQueues[transition].getSemaphore().acquire(blocking=True)
                        self.__monitorLock.acquire()
                        k = True

        finally:
            self.__monitorLock.release()

    def __checkConflict(self, threadBlockedList):
        # FIXME esto se podria optimizar haciendo que solo recorra como una matriz diagonal
        for threadBlockedA in threadBlockedList:
            for threadBlockedB in threadBlockedList:
                if(threadBlockedA != threadBlockedB):
                    threadBlockedAInitPos = threadBlockedA.transitionTranslated[0]
                    threadBlockedAEndPos = threadBlockedA.transitionTranslated[1]
                    threadBlockedBInitPos = threadBlockedB.transitionTranslated[0]
                    threadBlockedBEndPos = threadBlockedB.transitionTranslated[1]
                    if(threadBlockedAInitPos == threadBlockedBEndPos and threadBlockedBInitPos == threadBlockedAEndPos):
                        # conflicto
                        print(f"CONFLICTO DETECTADOOOO --- ENTRE <{threadBlockedB.threadID}> YYY {threadBlockedA.threadID}\n\n")
                        return (True, threadBlockedA, threadBlockedB)
        return (False, None, None)

    def __threadBlockedExistsInList(self, threadID, threadBlockedList):
        for threadBlocked in threadBlockedList:
            if(threadBlocked.threadID == threadID):
                return True
        else:
            # the loop completed without finding an object with the given name, the object does not exist in the list
            return False

    # warning: this function is not thread-safe, depends on the monitor to be used in a thread safe way
    def __getTransitionTranslation(self, transition):
        translation = self.__petriNet.getTransitionTranslation(transition)
        return translation

    def __getTransitionCandidates(self, sensibilizadas):
        transitionCandidates = []
        for i in range(len(sensibilizadas)):
            if(self.__transitionQueues[sensibilizadas[i]].hasRequests()):
                transitionCandidates.append(sensibilizadas[i])
        return transitionCandidates

    def getTransitionSequence(self, coordinatesSequence):
        with self.__directRdPAccessCondition:
            transitionSequence = self.__petriNet.getTransitionSequence(coordinatesSequence)
            self.__directRdPAccessCondition.notify_all()
            return transitionSequence

    def setRobotInCoordinate(self, coordinate, robotID):
        with self.__directRdPAccessCondition:
            if(self.__petriNet.setRobotInCoordinate(coordinate, robotID)):
                print("ERROR INSIDE MONITOR unable to set robot in coordinate\n")
            self.__directRdPAccessCondition.notify_all()

    def setCoordinateConfirmation(self, threadID, transition, confirmationValue):
        with self.__directRdPAccessCondition:
            result = self.__petriNet.setCoordinateConfirmation(threadID, transition, confirmationValue)
            self.__directRdPAccessCondition.notify_all()
            return result

    def calculatePath(self, startX, startY, endX, endY):
        with self.__directPathFinderAccessCondition:
            pathCoordinates = self.__pathFinder.calculatePath(startX, startY, endX, endY)
            self.__directPathFinderAccessCondition.notify_all()
            return pathCoordinates

    def calculateDynamicPath(self, startX, startY, endX, endY, cellsCoordinatesMarkedAsOccupied):
        with self.__directPathFinderAccessCondition:
            pathCoordinates = self.__pathFinder.calculateDynamicPath(startX, startY, endX, endY, cellsCoordinatesMarkedAsOccupied)
            self.__directPathFinderAccessCondition.notify_all()
            return pathCoordinates

    def __fireCountIncrement(self):
        self.__fireCount = self.__fireCount+1

