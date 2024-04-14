from .MonitorWithQueuesAndPriorityQueue import MonitorReturnStatus
from .JobManager import Job
from .KalmanFilter2D import KalmanFilter2D
import macros
from time import perf_counter
import numpy as np
import operator
import logging
import time
import json

class RobotThreadExecutor:
    def __init__(self, robot, monitor):
        self.__monitor = monitor
        self.__robot = robot
        self.__robotID = robot.getRobotID()
        self.__jobs = []
        self.__kalmanFilter = KalmanFilter2D()
        self.__currentMovementVector = []
        self.__lastDesiredMovementVector = []
        self.__time_start = 0
        self.__time_end = 0
        self.__robotReachedDestination = False;

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
        self.__kalmanFilter.setInitialState([[coordinatesSequence[0][0],0], [coordinatesSequence[0][1],0]])

        logging.debug(f'[{__name__} @ {self.__robotID}] STARTED PATHS | COORDINATES SEQUENCE = {coordinatesSequence} | TRANSITIONS SEQUENCE = {transitionsSequence}')

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

    def updateRobotFeedback(self, robotFeedback):

        # medir tiempo desde la ultima medicion
        self.__time_end = perf_counter()
        deltaT = self.__time_end - self.__time_start
        self.__time_start = self.__time_end

        logging.debug(f'[{__name__}] {self.__robotID} received feedback <{robotFeedback} @ deltaT = {deltaT}>')

        data = json.loads(robotFeedback)

        if('status' in data):
            status = data['status']
            if(type(status)!=int):
                logging.error(f'[{__name__}] {self.__robotID} json contains invalid data for status')
                return False
            if(status == 0): # robot avisa que llego a destino
                self.__robotReachedDestination = True
        else:
            dx = data['dx']
            vx = data['vx']
            dy = data['dy']
            vy = data['vy']
            if(type(dx)!=float or type(vx)!=float or type(dy)!=float or type(vy)!=float):
                logging.error(f'[{__name__}] {self.__robotID} json contains invalid data for measurement feedback')
                return False
            self.__kalmanFilter.inputMeasurementUpdate([[dx,vx], [dy,vy]], deltaT)

        return True

    # retorna una tupla con las velocidades y distancia a recorrer (distance, vx, vy, vrot)
    def getMovementVector(self):
        return self.__currentMovementVector

    def isCompensationTime(self):
        return self.__kalmanFilter.isCompensationTime()

    def calculateCompensatedVector(self):
        estimatedCurrentState = self.__kalmanFilter.getEstimatedState()
        currentJob = self.__jobs[0]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()+1]
        self.__currentMovementVector = self.__kalmanFilter.getCompensatedVectorAutomagic(estimatedCurrentState, nextCoordinate)

    # recibe una tupla con las velocidades y distancia a recorrer (distance, vx, vy, vrot)
    def traslateMovementVectorToMessage(self, movementVector):
        vectorMessage = {
            "distance": movementVector[0],
            "vx": movementVector[1],
            "vy": movementVector[2],
            "vr": movementVector[3]
        }
        return json.dumps(vectorMessage)

    def calculateMovementVector(self):
        currentJob = self.__jobs[0]
        transitionIndex = currentJob.getTransitionIndex()
        currentCoordinate = currentJob.getCoordinatesPathSequence()[transitionIndex]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[transitionIndex+1]
        logging.debug(f'[{__name__}] busque la nueva coordenada <{nextCoordinate}> | transicion <{transitionIndex}>')

        res = tuple(map(operator.sub, nextCoordinate, currentCoordinate)) # obtiene el delta entre ambas coordenadas
        filtro_negativo = tuple(map(lambda x: -1 if (x<0) else x, res)) # normaliza la tupla
        filtro_positivo = tuple(map(lambda x: 1 if (x>0) else x, filtro_negativo))
        newDesiredVector = [macros.DEFAULT_ROBOT_MOVE_DISTANCE, filtro_positivo[0]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, filtro_positivo[1]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, 0.00]

        if(transitionIndex > 1): # FIXME deberia ser >0 cuando se arregle que el disparo de la red se haga y recien cuando llegue impacte el estado
            if(self.cambioDireccion(self.__lastDesiredMovementVector, newDesiredVector)):
                logging.debug(f'[{__name__}] cambio de direccion (!)')
                self.__kalmanFilter.notifyDirectionChange()

        self.__currentMovementVector = newDesiredVector
        self.__lastDesiredMovementVector = newDesiredVector

        return (self.__currentMovementVector != None)

    def cambioDireccion(self, desiredVector, newDesiredVector):
        if(desiredVector[1] != newDesiredVector[1] or desiredVector[2] != newDesiredVector[2]):
            return True
        return False

    def sendSetpointToRobot(self):
        try:
            movementVector = self.getMovementVector()
            setpoint_message = self.traslateMovementVectorToMessage(movementVector)
            msg = self.__robot.getMqttClient().publish(self.__robot.getRobotSendSetpointTopic(), setpoint_message, qos=0)
            msg.wait_for_publish()
            self.__time_start = perf_counter() # comienza a contar tiempo para el deltaT desde que manda el setpoint
            return True
        except Exception as e:
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)} @ {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}')
            return False

    def robotIsNearOrPassOverDestinationCoordinate(self):

        if(self.__robotReachedDestination):
            self.__robotReachedDestination = False
            return True

        # currentMovementVector me dice hacia donde me estoy moviendo (desired vector no puede ser el vector compensado, es el vector ideal con solo 1 eje de velocidad != 0)
        # estimatedCurrentCoordinate me sirve para comparar y ver si llegue/me pase a nextCoordinate
        # radius es el radio que se toma "llegando" a nextCoordinate

        radius = macros.DEFAULT_CELL_ARRIVE_RADIUS

        estimatedCurrentState = self.__kalmanFilter.getEstimatedState()
        estimatedCurrentCoordinate = []
        estimatedCurrentCoordinate.append(0)
        estimatedCurrentCoordinate.append(0)
        estimatedCurrentCoordinate[0] = estimatedCurrentState[0][0]
        estimatedCurrentCoordinate[1] = estimatedCurrentState[1][0]

        vx = self.__lastDesiredMovementVector[1]
        vy = self.__lastDesiredMovementVector[2]

        currentJob = self.__jobs[0]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()+1]

        logging.debug(f'[{__name__}] radius {radius} | estCurrCoord {estimatedCurrentCoordinate} | nextCoord {nextCoordinate} | vector ({vx},{vy})')

        if(vx != 0):
            x_est_curr = estimatedCurrentCoordinate[0]
            x_exp_next = nextCoordinate[0]
            x_delta = np.abs(x_est_curr-x_exp_next)

            if(x_delta <= radius):
                return True
            if((vx > 0) and (x_est_curr >= x_exp_next)):
                return True
            elif((vx < 0) and (x_est_curr <= x_exp_next)):
                return True

        elif(vy != 0):
            y_est_curr = estimatedCurrentCoordinate[1]
            y_exp_next = nextCoordinate[1]
            y_delta = np.abs(y_est_curr-y_exp_next)

            if(y_delta <= radius):
                return True
            elif((vy > 0) and (y_est_curr >= y_exp_next)):
                return True
            elif((vy < 0) and (y_est_curr <= y_exp_next)):
                return True

        return False

    def setCoordinateConfirmation(self, confirmationValue):
        logging.debug(f'[{__name__}] SETTING COORD CONFIRMATION ...')
        currentJob = self.__jobs[0]
        destinationCoordinateTransition = currentJob.getTransitionsPathSequence()[currentJob.getTransitionIndex()]
        logging.debug(f'[{__name__} @ {self.__robotID}] confirmation of transition {destinationCoordinateTransition}')
        return self.__monitor.setCoordinateConfirmation(self.__robotID, destinationCoordinateTransition, confirmationValue)

    def run(self):

        try:
            currentJob = self.__jobs[0]
            transitionToExecute = currentJob.getNextTransitionToExecute()
            logging.debug(f'[{self.__robotID}] proxima transicion a ejecutar en el monitor <{transitionToExecute}>')

            monitorReturnStatus = self.__monitor.monitorDisparar(transitionToExecute, self.__robotID)

            if(monitorReturnStatus == MonitorReturnStatus.SUCCESSFUL_REQUEST_WAITING_CONFIRMATION): # si pudo solicitar el movimiento a la celda y esta esperando confirmacion
                return "WAIT_CONF"

            elif(monitorReturnStatus == MonitorReturnStatus.SUCCESSFUL_FIRING): # si pudo disparar, busco la siguiente transicion
                logging.debug(f'[{self.__robotID}] || disparo monitor exitoso.')
                if(currentJob.updateNextTransitionToExecute()):
                    logging.debug(f'[{self.__robotID}] path sequence finished successfully.')
                    self.__jobs = []
                    return "END"

                nextTransitionToExecute = currentJob.getNextTransitionToExecute()
                monitorReturnStatus = self.__monitor.monitorDisparar(nextTransitionToExecute, self.__robotID)

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
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)} @ {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}')
            exit()
            return "NO_JOBS"

