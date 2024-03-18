from .MonitorWithQueuesAndPriorityQueue import MonitorReturnStatus
from .JobManager import Job
from .KalmanFilter2D import KalmanFilter2D
import macros
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
        logging.debug(f'[{__name__}] {self.__robotID} received feedback <{robotFeedback}>')

        data = json.loads(robotFeedback)
        dx = data['dx']
        vx = data['vx']
        dy = data['dy']
        vy = data['vy']
        self.__kalmanFilter.inputMeasurementUpdate([[dx,vx], [dy,vy]])

    def getMovementVector(self):
        # desiredVector = getDesiredMovementVector(currentCoordinate, nextCoordinate)

        currentJob = self.__jobs[0]
        currentCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()+1]
        logging.debug(f'[{__name__}] busque la nueva coordenada <{nextCoordinate}>')

        res = tuple(map(operator.sub, nextCoordinate, currentCoordinate)) # obtiene el delta entre ambas coordenadas
        filtro_negativo = tuple(map(lambda x: -1 if (x<0) else x, res)) # normaliza la tupla
        filtro_positivo = tuple(map(lambda x: 1 if (x>0) else x, filtro_negativo))
        desiredVector = [macros.DEFAULT_ROBOT_MOVE_DISTANCE, filtro_positivo[0]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, filtro_positivo[1]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, 0.00]
        return desiredVector

    # retorna una tupla con las velocidades y distancia a recorrer (distance, vx, vy, vrot)
    def getMovementVector_OLD(self):
        # en esta funcion se podria hacer que tome la compensacion desde kalman, modificando las velocidades de setpoint
        # hay que ver bien que pasa con el kalman en los casos donde el robot cambia de direccion (dobla)
        currentJob = self.__jobs[0]

        if (currentJob.getTransitionIndex() == 0):
            return tuple((0,0))

        previousCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()-1]
        currentCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()]

        # normaliza la tupla
        res = tuple(map(operator.sub, currentCoordinate, previousCoordinate)) # obtiene el delta entre ambas coordenadas
        filtro_negativo = tuple(map(lambda x: -1 if (x<0) else x, res))
        filtro_positivo = tuple(map(lambda x: 1 if (x>0) else x, filtro_negativo))

        #unityVelocityVector = tuple((filtro_positivo[0], filtro_positivo[1])) # es un vector unitario de velocidad hacia donde se esta dirigiendo
        #unityVector = tuple((macros.DEFAULT_ROBOT_MOVE_DISTANCE, filtro_positivo[0], filtro_positivo[1], macros.DEFAULT_ROBOT_ANGULAR_VELOCITY)) # es un vector unitario de velocidad hacia donde se esta dirigiendo

        # aplicar compensacion de kalman
        expectedCurrentCoordinate = tuple((previousCoordinate[0] * macros.DEFAULT_CELL_SIZE, previousCoordinate[1] * macros.DEFAULT_CELL_SIZE))
        expectedNextCoordinate = tuple((currentCoordinate[0] * macros.DEFAULT_CELL_SIZE, currentCoordinate[1] * macros.DEFAULT_CELL_SIZE))
        estimatedCurrentState = self.__kalmanFilter.getEstimatedState()
        compensatedVector = self.getCompensatedVector(estimatedCurrentState, expectedCurrentCoordinate, expectedNextCoordinate)

        if(compensatedVector != None):
            compensatedVector = np.round(compensatedVector, decimals=3)
            compensatedMovementVector = np.array([compensatedVector[0], compensatedVector[1], compensatedVector[2], macros.DEFAULT_ROBOT_ANGULAR_VELOCITY])
        else:
            compensatedMovementVector = np.array([macros.DEFAULT_ROBOT_MOVE_DISTANCE, filtro_positivo[0]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, filtro_positivo[1]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, macros.DEFAULT_ROBOT_ANGULAR_VELOCITY])
        return compensatedMovementVector

    def getCompensatedVector(self, estimatedCurrentState, expectedCurrentCoordinate, expectedNextCoordinate):
        logging.debug(f'[{__name__} @ {self.__robotID}] INSIDE getCompensatedVector | estimated curr state :{estimatedCurrentState} | expected curr coordinate: {expectedCurrentCoordinate} | expected next coordinate: {expectedNextCoordinate}')

        # posicion estimada actual
        x_est_curr = estimatedCurrentState[0][0]
        y_est_curr = estimatedCurrentState[1][0]

        # posicion expected actual
        x_exp_curr = expectedCurrentCoordinate[0]
        y_exp_curr = expectedCurrentCoordinate[1]

        # posicion expected siguiente
        x_exp_next = expectedNextCoordinate[0]
        y_exp_next = expectedNextCoordinate[1]

        compensationDistance = np.hypot([x_exp_next-x_est_curr], [y_exp_next-y_est_curr])

        x_delta_dist_cmpstd = x_est_curr - x_exp_curr
        y_delta_dist_cmpstd = y_exp_next - y_est_curr

        if(x_delta_dist_cmpstd != 0 and y_delta_dist_cmpstd != 0):
            alpha = np.arctan([x_delta_dist_cmpstd / y_delta_dist_cmpstd])
            vx_cmpstd = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.sin(alpha)
            vy_cmpstd = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.cos(alpha)
            compensationVelocityVector = [compensationDistance[0], vx_cmpstd[0], vy_cmpstd[0]]

            logging.debug(f'[{__name__} @ {self.__robotID}] INSIDE getCompensatedVector | alpha: {alpha} | comp distance: {compensationDistance} | comp vector: {compensationVelocityVector}')
            return compensationVelocityVector

    def isCompensationTime(self):
        return self.__kalmanFilter.isCompensationTime()

    def getCompensatedVectorAutomagic(self):
        estimatedCurrentState = self.__kalmanFilter.getEstimatedState()
        currentJob = self.__jobs[0]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()]
        return self.__kalmanFilter.getCompensatedVectorAutomagic(estimatedCurrentState, nextCoordinate)

    # recibe una tupla con las velocidades y distancia a recorrer (distance, vx, vy, vrot)
    def traslateMovementVectorToMessage(self, movementVector):
        vectorMessage = {
            # "distance": macros.DEFAULT_ROBOT_MOVE_DISTANCE,
            # "vx": movementVector[0],
            # "vy": movementVector[1],
            # "vr": movementVector[2]

            "distance": movementVector[0],
            "vx": movementVector[1],
            "vy": movementVector[2],
            "vr": movementVector[3]
        }
        return json.dumps(vectorMessage)

    def sendSetpointToRobot(self):
        try:
            movementVector = self.getMovementVector()
            self.__currentMovementVector = movementVector

            setpoint_message = self.traslateMovementVectorToMessage(movementVector)
            msg = self.__robot.getMqttClient().publish(self.__robot.getRobotSendSetpointTopic(), setpoint_message, qos=0)
            msg.wait_for_publish()
            return True
        except Exception as e:
            logging.error(f'[{__name__} @ {self.__robotID}] EXCEPTION RAISED: {repr(e)}')
            return False

    def robotIsNearOrPassOverDestinationCoordinate(self):
    #def robotIsNearOrPassOverDestinationCoordinate(movementVector, estimatedCurrentCoordinate, nextCoordinate, radius):
        # robotIsNearOrPassOverDestinationCoordinate(movementVector, estimatedCurrentCoordinate, nextCoordinate, radius):

        # movementVector me dice hacia donde me estoy moviendo (desired vector no puede ser el vector compensado, es el vector ideal con solo 1 eje de velocidad != 0)
        # estimatedCurrentCoordinate me sirve para comparar y ver si llegue/me pase a nextCoordinate
        # radius es el radio que se toma "llegando" a nextCoordinate

        radius = macros.DEFAULT_CELL_ARRIVE_RADIUS

        estimatedCurrentState = self.__kalmanFilter.getEstimatedState()
        estimatedCurrentCoordinate = []
        estimatedCurrentCoordinate.append(0)
        estimatedCurrentCoordinate.append(0)
        estimatedCurrentCoordinate[0] = estimatedCurrentState[0][0]
        estimatedCurrentCoordinate[1] = estimatedCurrentState[1][0]


        #vx = movementVector[1]
        #vy = movementVector[2]
        vx = self.__currentMovementVector[1]
        vy = self.__currentMovementVector[2]

        currentJob = self.__jobs[0]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()]

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

