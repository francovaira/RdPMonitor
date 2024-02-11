from .MonitorWithQueuesAndPriorityQueue import MonitorReturnStatus
from .JobManager import Job
import operator
import logging

class RobotThreadExecutor:
    def __init__(self, robotID, monitor):
        self.__monitor = monitor
        self.__robotID = robotID
        self.__jobs = []

    def addJob(self, job):
        if(type(job) == Job):
            self.__jobs.append(job)

    # calculates coordinates sequence then transition sequence for each job and places robot in init position. Sets everything to start running on the thread
    def startPaths(self):
        if(not len(self.__jobs) or len(self.__jobs) > 1): # FIXME por ahora no soporta mas de 1 job
            print(f"NO JOBS DEFINED -- WILL DO NOTHING, EXITING...")
            exit()

        # por aca deberia checkear que los path (si hay mas de uno) sean continuos - es decir, no seria valido ir de (1,1 a 5,5) y despues de (3,2 a 4,1)
        # capaz se podria hacer que calcule la trayectoria del tramo faltante de ultima

        for job in self.__jobs:
            coordinatesSequence = self.__getCoorinatesSequence(job.getPaths())
            transitionsSequence = self.__monitor.getTransitionSequence(coordinatesSequence)
            job.setCoordinatesPathSequence(coordinatesSequence)
            job.setTransitionsPathSequence(transitionsSequence)
            self.__monitor.setRobotInCoordinate(coordinatesSequence[0], self.__robotID)
        print(f"{self.__robotID} || STARTED PATHS || COORDINATES SEQUENCE = {coordinatesSequence} // TRANSITIONS SEQUENCE = {transitionsSequence}")

    def __getCoorinatesSequence(self, paths):
        coordinatesSequence = []
        for path in paths:
            initPos = path.getInitPos()
            endPos = path.getEndPos()
            coordSeq = self.__monitor.calculatePath(initPos[0], initPos[1], endPos[0], endPos[1])

            if(len(coordinatesSequence) > 0):
                coordSeq.pop(0)
                coordinatesSequence.extend(coordSeq)
            else:
                coordinatesSequence = coordSeq
        return coordinatesSequence

    def getPathTuple(self):
        currentJob = self.__jobs[0]
        transitionIndex = currentJob.getTransitionIndex()
        previousPath = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()-1]
        currentPath = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()]
        print('CURRENT:', currentPath, 'PREVIO', previousPath)
        print('INDEX', )
        if (currentJob.getTransitionIndex() == 0):
            return tuple((0,0))
        else:
            res = tuple(map(operator.sub, currentPath, previousPath))
            # Normalizar tupla
            filtro_negativo = tuple(map(lambda x: -1 if (x<0) else x, res))
            filtro_positivo = tuple(map(lambda x: 1 if (x>0) else x, filtro_negativo))
            return filtro_positivo

    def run(self):

        # FIXME aca adentro se deberia hacer toda la parte de comunicacion de setpoints y compensacion de kalman, etc
        try:
            currentJob = self.__jobs[0]
            transitionsSequence = currentJob.getTransitionsPathSequence()
            transitionIndex = currentJob.getTransitionIndex()

            if(not len(transitionsSequence)):
                print("ERROR - Transition sequence empty - must initialize paths")
                exit()

            transitionToExecute = transitionsSequence[transitionIndex]
            monitorReturnStatus = self.__monitor.monitorDisparar(transitionToExecute, self.__robotID)
            if(monitorReturnStatus == MonitorReturnStatus.SUCCESSFUL_FIRING): # si pudo disparar, busco la siguiente transicion
                nextTransitionIndex = transitionIndex + 1
                currentJob.setTransitionIndex(nextTransitionIndex)
                print(f"@{self.__robotID} || NEXT TRANSITION @{currentJob.getCoordinatesPathSequence()[transitionIndex]}")
                # blockedPosition = currentJob.getCoordinatesPathSequence()[transitionIndex]

                if(nextTransitionIndex>= len(transitionsSequence)):
                    print(f"SEQUENCE FINISHED AT THE END @{self.__robotID}")
                    self.__jobs = []
                    return False
            elif(monitorReturnStatus == MonitorReturnStatus.TIMEOUT_WAITING_BLOCKED):
                blockedPosition = currentJob.getCoordinatesPathSequence()[transitionIndex]
                remainingPathCoordinates = currentJob.getCoordinatesPathSequence()[transitionIndex+1:]
                print(f"{self.__robotID} || I MUST RECALCULATEEEEE -- ME QUEDE EN LA POSICION {blockedPosition} || ME QUEDE EN LA TRANSICION {transitionToExecute}")
                print(f"{self.__robotID} || ME QUEDA RECORRER {remainingPathCoordinates}")

                initPos = blockedPosition
                endPos = remainingPathCoordinates[0]
                dynamicOccupiedCells = []
                dynamicOccupiedCells.append(remainingPathCoordinates[0])
                print(f"{self.__robotID} || VOY A RECALCULARRRR // INIT POS = {initPos} // END POS = {endPos} // CELLS MARKED OCCUPIED = {dynamicOccupiedCells}")
                coordSeq = self.__monitor.calculateDynamicPath(initPos[0], initPos[1], endPos[0], endPos[1], dynamicOccupiedCells)
                newTransitionsSequence = self.__monitor.getTransitionSequence(coordSeq)
                print(f"{self.__robotID} || RETRAYECTORIADO = {coordSeq} -- CORRESPOND TO TRANSITIONS <{newTransitionsSequence}>\n\n--------------------------------\n")

                transitionsSequence.pop(transitionIndex)
                transitionsSequence[transitionIndex:transitionIndex] = newTransitionsSequence # inserts elements from index
                print(f"{self.__robotID} || NUEVO CALCULO DE LAS TRANSICIONES = {newTransitionsSequence} || EL TOTAL SERIA = {transitionsSequence}")
                currentJob.setTransitionsPathSequence(transitionsSequence)

                coordinatesPathSequence = currentJob.getCoordinatesPathSequence()
                coordinatesPathSequence.pop(transitionIndex)
                coordSeq.pop() # remove last element of list, the last element is the arrive position, which is already in the remaining of the sequence
                coordinatesPathSequence[transitionIndex:transitionIndex] = coordSeq # inserts elements from index
                print(f"{self.__robotID} || NUEVO CALCULO DE LAS COORDENADAS = {coordSeq} || EL TOTAL SERIA = {coordinatesPathSequence}\n\n--------------------------------\n")
                currentJob.setCoordinatesPathSequence(coordinatesPathSequence)

            return monitorReturnStatus

        except:
            # No hay jobs disponibles por lo tanto retorna False para mantener el estado
            return False

