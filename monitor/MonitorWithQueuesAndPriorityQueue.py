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
    TIMEOUT_WAITING_BLOCKED = 2

class TransitionMonitorQueue:

    def __init__(self):
        self.__threadsRequesting = []
        self.__hasRequests = False
        self.__semaphore = threading.BoundedSemaphore()
        self.__semaphore.acquire()

    def request(self, threadID):
        if(any(elem == threadID for elem in self.__threadsRequesting) or threadID == None or threadID == ""): # check for duplicates
            #print(f"ERROR IN MONITOR - The thread <{threadID}> is trying to request the transition again or has an empty thread ID") # creo que no necesariamente es un error
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
        self.__directPathFinderAccessCondition = threading.Condition(self.__monitorLock)
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
            self.__fileWrite(self.__accumLog, "LOG_OUTPUT.txt")
            print("Leaving...")
            exit()

        with self.__monitorEntranceLock:
            if(self.__priorityThread != "" and self.__priorityThread != threadID):
                #print(f"==== THREAD {threadID} || LIBERO EL LOCK DE ENTRADA, HAY ALGUIEN EN PRIORIDAD <{self.__priorityThread}> // CANT DISPAROS {self.__fireCount}")
                #return False
                return MonitorReturnStatus.UNABLE_TO_FIRE
            else:
                self.__monitorLock.acquire()
                if(self.__priorityThread != "" and self.__priorityThread != threadID):
                    self.__monitorLock.release()
                    #print(f"==== THREAD {threadID} || LIBERO EL LOCK, HAY ALGUIEN EN PRIORIDAD <{self.__priorityThread}> // CANT DISPAROS {self.__fireCount}")
                    #return False
                    return MonitorReturnStatus.UNABLE_TO_FIRE

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

                    if(self.__threadBlockedExistsInList(threadID, self.__threadsInConflict)): # si ya dispare y estaba en la cola de bloqueados, me voy
                        for thrBlocked in self.__threadsInConflict:
                            self.__transitionQueues[thrBlocked.transition].releaseRequest(thrBlocked.threadID)
                        self.__threadsInConflict = []
                        # for threadBlockedInList in self.__blockedThreadsQueue:
                        #     if(threadBlockedInList.threadID == threadID):
                        #         self.__blockedThreadsQueue.remove(threadBlockedInList)
                        #         print(f"{threadID} || ME BORRE DE LOS BLOQUEADOSSSSS")


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
                            print(f"==== THREAD {threadID} || SETTING PRIORITY THREAD TO {self.__transitionQueues[transitionDecision].getThreadsRequesting()[0]} // CANT DISPAROS {self.__fireCount}")

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

                    #return True
                    return MonitorReturnStatus.SUCCESSFUL_FIRING
                else:
                    # put myself as thread into according queue
                    # importante, el thread solo se va a encolar en caso que haya intentado disparar la transicion pero no pudo
                    print(f"==== THREAD {threadID} || TRANSICION NO SENSIBILIZADA, ME ENCOLO EN LA TRANSICION {transition}")
                    #self.__accumLog = self.__accumLog + f"{threadID},'20',"
                    self.__accumLog = self.__accumLog + f"{time.time()},{threadID},20\n"
                    # NSENS_TRANSITION = 20

                    # decide por politica quien recalcula -- el que recalcula se le cambian las transiciones, sale del monitor y se va a recalcular y pelear por otras transiciones (no deberia bloquearse en la transicion actual, tiene que obtener una nueva por haber recalculado)
                    # el que no recalcula debe bloquearse hasta que el que recalcula se mueva -- en definitiva haria el acquire

                    # ESTO DE ACA ABAJO MASO FUNCA, TIENE PROBLEMAS CON LA CONCURRENCIA
                    # for obj in self.__blockedThreadsQueue:
                    #     if(obj.threadID == threadID):
                    #         # an object with the given name exists in the list
                    #         if(len(self.__blockedThreadsQueue) > 1):
                    #             # comparo dentro de la lista si hay alguien que coincida mi equivalenciaInitXY con su equivalenciaEndXY y tambien viceversa -> si hay, es conflicto
                    #             for threadBlocked in self.__blockedThreadsQueue:
                    #                 if(threadBlocked != obj):
                    #                     newThreadBlockedInitPos = obj.transitionTranslated[0]
                    #                     newThreadBlockedEndPos = obj.transitionTranslated[1]
                    #                     threadBlockedInitPos = threadBlocked.transitionTranslated[0]
                    #                     threadBlockedEndPos = threadBlocked.transitionTranslated[1]
                    #                     if(newThreadBlockedInitPos == threadBlockedEndPos and newThreadBlockedEndPos == threadBlockedInitPos):
                    #                         # conflicto
                    #                         print(f"{threadID} || CONFLICTO DETECTADOOOO APENAS ENTREEEE AMNKVFEWKVW --- ENTRE <{obj.threadID}> YYY {threadBlocked.threadID}\n\n")

                    #                         self.__blockedThreadsQueue = []

                    #                         # decide por politica quien recalcula
                    #                         if(threadID == "ROB_C"): # esto seria la politica
                    #                             return MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED
                    #         break
                    # else:
                    #     # the loop completed without finding an object with the given name, the object does not exist in the list
                    #     newThreadBlocked = ThreadBlocked(threadID, transition, self.__getTransitionTranslation(transition))
                    #     self.__blockedThreadsQueue.append(newThreadBlocked)
                    #     print(f"{threadID} || ME AGREGUE A LA COLA DE BLOQUEADOS || {newThreadBlocked.transitionTranslated}")

                    #     # comparo dentro de la lista si hay alguien que coincida mi equivalenciaInitXY con su equivalenciaEndXY y tambien viceversa -> si hay, es conflicto
                    #     for threadBlocked in self.__blockedThreadsQueue:
                    #         if(threadBlocked != newThreadBlocked):
                    #             newThreadBlockedInitPos = newThreadBlocked.transitionTranslated[0]
                    #             newThreadBlockedEndPos = newThreadBlocked.transitionTranslated[1]
                    #             threadBlockedInitPos = threadBlocked.transitionTranslated[0]
                    #             threadBlockedEndPos = threadBlocked.transitionTranslated[1]
                    #             if(newThreadBlockedInitPos == threadBlockedEndPos and newThreadBlockedEndPos == threadBlockedInitPos):
                    #                 # conflicto
                    #                 print(f"CONFLICTO DETECTADOOOOAMNKVFEWKVW --- ENTRE <{newThreadBlocked.threadID}> YYY {threadBlocked.threadID}\n\n")

                    #                 # decide por politica quien recalcula
                    #                 if(threadID == "ROB_C"): # esto seria la politica
                    #                     self.__blockedThreadsQueue = []
                    #                     return MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED
                    #                 else:
                    #                     for obj in self.__blockedThreadsQueue:
                    #                         if(obj.threadID == "ROB_C"):
                    #                             # an object with the given name exists in the list
                    #                             self.__transitionQueues[obj.transition].getSemaphore().release()


                    # me pongo en la cola de bloqueados con la info [transicion, equivalenciaInitXY, equivalenciaEndXY]
                    # if(len(self.__blockedThreadsQueue) > 0 and not any(elem.threadID == threadID for elem in self.__blockedThreadsQueue)): # check si ya esta agregado el robot
                    #     print("asdasds")
                    #     pass
                    # else:
                    #     newThreadBlocked = ThreadBlocked(threadID, transition, self.__getTransitionTranslation(transition))
                    #     self.__blockedThreadsQueue.append(newThreadBlocked)
                    #     print(f"{threadID} || ME AGREGUE A LA COLA DE BLOQUEADOS || {newThreadBlocked.transitionTranslated}")

                    #     # comparo dentro de la lista si hay alguien que coincida mi equivalenciaInitXY con su equivalenciaEndXY y tambien viceversa -> si hay, es conflicto
                    #     for threadBlocked in self.__blockedThreadsQueue:
                    #         if(threadBlocked != newThreadBlocked):
                    #             newthreadBlockedInitPos = newthreadBlocked.transitionTranslated[0]
                    #             newthreadBlockedEndPos = newthreadBlocked.transitionTranslated[1]
                    #             threadBlockedInitPos = threadBlocked.transitionTranslated[0]
                    #             threadBlockedEndPos = threadBlocked.transitionTranslated[1]
                    #             if(newthreadBlockedInitPos == threadBlockedEndPos and newthreadBlockedEndPos == threadBlockedInitPos):
                    #                 # conflicto
                    #                 print(f"CONFLICTO DETECTADOOOOAMNKVFEWKVW --- ENTRE <{newThreadBlocked.threadID}> YYY {threadBlocked.threadID}\n\n")

                    # if(not self.__threadBlockedExistsInList(threadID, self.__blockedThreadsQueue)):
                    #     # the loop completed without finding an object with the given name, the object does not exist in the list
                    #     newThreadBlocked = ThreadBlocked(threadID, transition, self.__getTransitionTranslation(transition))
                    #     self.__blockedThreadsQueue.append(newThreadBlocked)
                    #     print(f"{threadID} || ME AGREGUE A LA COLA DE BLOQUEADOS || {newThreadBlocked.transitionTranslated}")

                    # if(self.__checkConflict(newThreadBlocked, self.__blockedThreadsQueue) == True):
                    #     threadDecision = self.__pathRecalculationPolicy.resolve(self.__blockedThreadsQueue) # decide que thread debe recalcular
                    #     if(threadDecision != threadID): # si la politica decidio otro robot, deberia despertar al hilo que se bloqueo -- ese hilo seria el que no debe recalcular
                    #         self.__priorityThread = threadDecision.threadID # FIXMEEEE esto hace falta?
                    #         self.__transitionQueues[threadDecision.transition].getSemaphore().release()
                    #         print(f"{threadID} || LE PUSE UN TOKEN AL SEMAFORO DEL THREAD {threadDecision.threadID}")
                    #     else: # si la politica decidio por mi, debo recalcular
                    #         if(self.__priorityThread == threadID): # me debo sacar de la lista de prioridad si estoy
                    #             self.__priorityThread = ""

                    #         return MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED


                    if(not self.__threadBlockedExistsInList(threadID, self.__blockedThreadsQueue)):
                        # the loop completed without finding an object with the given name, the object does not exist in the list
                        newThreadBlocked = ThreadBlocked(threadID, transition, self.__getTransitionTranslation(transition))
                        self.__blockedThreadsQueue.append(newThreadBlocked)
                        print(f"{threadID} || ME AGREGUE A LA COLA DE BLOQUEADOS || {newThreadBlocked.transitionTranslated}")

                    isConflict, threadInConflictA, threadInConflictB = self.__checkConflictA(self.__blockedThreadsQueue)
                    if(isConflict == True):
                        self.__threadsInConflict.append(threadInConflictA)
                        self.__threadsInConflict.append(threadInConflictB)

                        threadDecision = self.__pathRecalculationPolicy.resolve(self.__threadsInConflict) # decide que thread debe recalcular
                        print(f"{threadID} || LA POLITICA DECIDIOOOO {threadDecision.threadID}")
                        if(threadDecision.threadID != threadID): # si la politica decidio otro robot, deberia despertar al hilo que se bloqueo -- ese hilo seria el que no debe recalcular
                            self.__priorityThread = threadDecision.threadID # FIXMEEEE esto hace falta?
                            self.__transitionQueues[threadDecision.transition].getSemaphore().release()
                            threadDecision.mustRecalculatePath = True
                            print(f"{threadID} || LE PUSE UN TOKEN AL SEMAFORO DEL THREAD {threadDecision.threadID}")
                            #return MonitorReturnStatus.UNABLE_TO_FIRE

                            self.__monitorLock.release()
                            self.__transitionQueues[transition].getSemaphore().acquire(blocking=True)
                            self.__monitorLock.acquire()
                            k=True

                        else: # si la politica decidio por mi, debo recalcular
                            if(self.__priorityThread == threadID): # me debo sacar de la lista de prioridad si estoy
                                self.__priorityThread = ""
                            self.__transitionQueues[threadDecision.transition].releaseRequest(threadID)
                            return MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED
                    else:
                        self.__monitorLock.release()
                        self.__transitionQueues[transition].getSemaphore().acquire(blocking=True)
                        self.__monitorLock.acquire()
                        k=True

                        if(self.__threadBlockedExistsInList(threadID, self.__threadsInConflict)): # si me desperte y resulta que debo recalcular
                            for threadBlockedInList in self.__threadsInConflict:
                                if(threadBlockedInList.threadID == threadID and threadBlockedInList.mustRecalculatePath):
                                    print(f"{threadID} || ME VOY A RECALCULARRRR")
                                    return MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED

                    #self.__monitorLock.release()
                    #self.__transitionQueues[transition].getSemaphore().acquire(blocking=True)
                    #self.__monitorLock.acquire()
                    #k=True

        finally:
            self.__monitorLock.release()

    # comparo dentro de la lista si hay alguien que coincida mi equivalenciaInitXY con su equivalenciaEndXY y tambien viceversa -> si hay, es conflicto
    def __checkConflict(self, newThreadBlocked, threadBlockedList):
        for threadBlockedInList in threadBlockedList:
                if(threadBlockedInList != newThreadBlocked):
                    threadInListInitPos = threadBlockedInList.transitionTranslated[0]
                    threadInListEndPos = threadBlockedInList.transitionTranslated[1]
                    newThreadBlockedInitPos = newThreadBlocked.transitionTranslated[0]
                    newThreadBlockedEndPos = newThreadBlocked.transitionTranslated[1]
                    if(threadABlockedInitPos == newThreadBlockedEndPos and newThreadBlockedInitPos and threadABlockedEndPos):
                        # conflicto
                        print(f"CONFLICTO DETECTADOOOOAMNKVFEWKVW --- ENTRE <{newThreadBlocked.threadID}> YYY {threadBlockedInList.threadID}\n\n")
                        return True
        return False

    def __checkConflictA(self, threadBlockedList):
        # FIXME esto se podria optimizar haciendo que solo recorra como una matriz diagonal
        for threadBlockedA in threadBlockedList:
            for threadBlockedB in threadBlockedList:
                if(threadBlockedA != threadBlockedB):
                    threadBlockedAInitPos = threadBlockedA.transitionTranslated[0]
                    threadBlockedAEndPos = threadBlockedA.transitionTranslated[1]
                    threadBlockedBInitPos = threadBlockedB.transitionTranslated[0]
                    threadBlockedBEndPos = threadBlockedB.transitionTranslated[1]
                    if(threadBlockedAInitPos == threadBlockedBEndPos and threadBlockedBInitPos and threadBlockedAEndPos):
                        # conflicto
                        print(f"CONFLICTO DETECTADOOOOAMNKVFEWKVW --- ENTRE <{threadBlockedB.threadID}> YYY {threadBlockedA.threadID}\n\n")
                        return (True, threadBlockedA, threadBlockedB)
        return (False, None, None)

    def __threadBlockedExistsInList(self, threadID, threadBlockedList):
        for threadBlocked in threadBlockedList:
            if(threadBlocked.threadID == threadID):
                # an object with the given name exists in the list
                return True
        else:
            # the loop completed without finding an object with the given name, the object does not exist in the list
            return False

    def __getTransitionTranslation(self, transition):
        #with self.__directRdPAccessCondition:
        translation = self.__petriNet.getTransitionTranslation(transition)
        self.__directRdPAccessCondition.notify_all()
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

    def calculateDynamicPath(self, startX, startY, endX, endY, cellsCoordinatesMarkedAsOccupied):
        with self.__directPathFinderAccessCondition:
            pathCoordinates = self.__pathFinder.calculateDynamicPath(startX, startY, endX, endY, cellsCoordinatesMarkedAsOccupied)
            self.__directPathFinderAccessCondition.notify_all()
            return pathCoordinates

    def __fireCountIncrement(self):
        self.__fireCount = self.__fireCount+1

