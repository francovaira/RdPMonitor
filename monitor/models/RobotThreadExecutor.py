from .MonitorWithQueuesAndPriorityQueue import MonitorReturnStatus
from .JobManager import Job
from .KalmanFilter2D import KalmanFilter2D
import operator
import logging
import time
import json

class RobotThreadExecutor:
    def __init__(self, robotID, monitor):
        self.__monitor = monitor
        self.__robotID = robotID
        self.__jobs = []
        self.__kalmanFilter = KalmanFilter2D()

    def addJob(self, job):
        if(type(job) == Job):
            self.__jobs.append(job)

    # calculates coordinates sequence then transition sequence for each job and places robot in init position. Sets everything to start running on the thread
    def startPaths(self):
        if(not len(self.__jobs) or len(self.__jobs) > 1): # FIXME por ahora no soporta mas de 1 job
            logging.error(f'[{__name__}] no jobs defined. Will do nothing.')

        # por aca deberia checkear que los path (si hay mas de uno) sean continuos - es decir, no seria valido ir de (1,1 a 5,5) y despues de (3,2 a 4,1)
        # capaz se podria hacer que calcule la trayectoria del tramo faltante de ultima

        for job in self.__jobs:
            coordinatesSequence = self.__getCoorinatesSequence(job.getPaths())
            transitionsSequence = self.__monitor.getTransitionSequence(coordinatesSequence)
            job.setCoordinatesPathSequence(coordinatesSequence)
            job.setTransitionsPathSequence(transitionsSequence)
            self.__monitor.setRobotInCoordinate(coordinatesSequence[0], self.__robotID)
        logging.debug(f'[{self.__robotID}] STARTED PATHS')
        logging.debug(f'[{self.__robotID}] COORDINATES SEQUENCE = {coordinatesSequence}')
        logging.debug(f'[{self.__robotID}] TRANSITIONS SEQUENCE = {transitionsSequence}')

    def __getCoorinatesSequence(self, paths):
        coordinatesSequence = []
        try:
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
        except:
            logging.error(f'[{__name__}] path doesnt exist')

    def getMovementVector(self):
        # en esta funcion se podria hacer que tome la compensacion desde kalman, modificando las velocidades de setpoint
        # hay que ver bien que pasa con el kalman en los casos donde el robot cambia de direccion (dobla)
        currentJob = self.__jobs[0]

        if (currentJob.getTransitionIndex() == 0):
            return tuple((0,0))

        previousCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()-1]
        currentCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()]

        res = tuple(map(operator.sub, currentCoordinate, previousCoordinate))
        # Normalizar tupla
        filtro_negativo = tuple(map(lambda x: -1 if (x<0) else x, res))
        filtro_positivo = tuple(map(lambda x: 1 if (x>0) else x, filtro_negativo))
        return filtro_positivo

    def updateRobotFeedback(self, robotFeedback):
        logging.debug(f'[{__name__}] {self.__robotID} received feedback <{robotFeedback}>')

        data = json.loads(robotFeedback)
        dx = data['dx']
        vx = data['vx']
        dy = data['dy']
        vy = data['vy']

        self.__kalmanFilter.inputMeasurementUpdate([ [dx,vx], [dy,vy] ])
        estimatedState = self.__kalmanFilter.getEstimatedState()
        logging.debug(f'[{__name__} @ {self.__robotID}] estimated state <{estimatedState}>')

    def run(self):

        try:
            logging.debug(f'[{self.__robotID}] ENTRE A BUSCAR LA PROXIMA TRANSICION A EJECUTAR!!')
            currentJob = self.__jobs[0]
            logging.debug(f'[{self.__robotID}] job found!!')

            transitionToExecute = currentJob.getNextTransitionToExecute()
            monitorReturnStatus = self.__monitor.monitorDisparar(transitionToExecute, self.__robotID)
            if(monitorReturnStatus == MonitorReturnStatus.SUCCESSFUL_FIRING): # si pudo disparar, busco la siguiente transicion
                logging.debug(f'[{self.__robotID}] || disparo monitor exitoso.')
                if(currentJob.updateNextTransitionToExecute()):
                    logging.debug(f'[{self.__robotID}] path sequence finished successfully.')
                    self.__jobs = []
                    return "END"
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

            return "WORKING"

        except Exception as e:
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)}')
            exit()
            return "NO_JOBS"

