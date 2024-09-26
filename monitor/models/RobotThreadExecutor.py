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
        self.__nextOrientation = robot.getCurrentOrientation()
        self.__time_start = 0
        self.__time_end = 0
        self.__robotReachedDestination = False;
        self.__isNewPathJob = False
        self.__isRotating = False

    def addJob(self, job):
        if(type(job) == Job):
            self.__jobs.append(job)
            self.__isNewPathJob = True

    # calculates coordinates sequence then transition sequence for each job and places robot in init position. Sets everything to start running on the thread
    def startPaths(self):
        if(not len(self.__jobs) or len(self.__jobs) > 1): # FIXME por ahora no soporta mas de 1 job
            logging.error(f'[{__name__}] no jobs defined. Will do nothing.')

        for job in self.__jobs:
            coordinatesSequence = self.__getCoorinatesSequence(job.getPaths())
            transitionsSequence = self.__monitor.getTransitionSequence(coordinatesSequence)
            job.setCoordinatesPathSequence(coordinatesSequence)
            job.setTransitionsPathSequence(transitionsSequence)
        self.__monitor.setRobotInCoordinate(coordinatesSequence[0], self.__robotID)
        self.__kalmanFilter.setInitialState([[coordinatesSequence[0][0],0], [coordinatesSequence[0][1],0]])

        res = tuple(map(operator.sub, coordinatesSequence[1], coordinatesSequence[0])) # obtiene el delta entre la coordenada actual y la destino iniciales
        filtro_negativo = tuple(map(lambda x: -1 if (x<0) else x, res)) # normaliza la tupla
        filtro_positivo = tuple(map(lambda x: 1 if (x>0) else x, filtro_negativo))
        filtro_positivo_eje_y_invertido = (filtro_positivo[0], -filtro_positivo[1])
        self.__robot.setCurrentOrientationAsVector(filtro_positivo_eje_y_invertido)

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

            # hay que convertir de coordenadas locales del robot a coordenadas globales del mapa (y del filtro de kalman)
            # segun la orientacion del robot deberia determinar a que componente corresponde en coordenadas globales del mapa
            translatedKalmanFeedback = self.translateRobotFeedbackToKalmanFeedback([dx, vx, dy, vy])
            # self.__kalmanFilter.inputMeasurementUpdate([[dx,vx], [dy,vy]], deltaT)
            self.__kalmanFilter.inputMeasurementUpdate([[translatedKalmanFeedback[0], translatedKalmanFeedback[1]], [translatedKalmanFeedback[2], translatedKalmanFeedback[3]]], deltaT)

        return True

    def processRobotFeedback(self, robotFeedback):
        logging.debug(f'[{__name__}] {self.__robotID} received feedback <{robotFeedback}>')
        data = json.loads(robotFeedback)

        if('status' in data):
            status = data['status']
            if(type(status)!=int):
                logging.error(f'[{__name__}] {self.__robotID} json contains invalid data for status')
                return 0
            if(status == 0): # robot avisa que llego a destino
                return 2
        else:
            return 0
        return 1

    # retorna una tupla con las velocidades y distancia a recorrer (distance, vx, vy, vrot)
    def getMovementVector(self):
        return self.__currentMovementVector

    # retorna true si el vector de movimiento solo contiene componente rotacional distinta de cero, las demas siendo cero (el robot girando sobre su propio eje)
    def isRotacionMovement(self):
        return self.__currentMovementVector[3] != 0 and self.__currentMovementVector[0] != 0 and self.__currentMovementVector[1] == 0 and self.__currentMovementVector[2] == 0

    def isNewPathJob(self):
        try:
            return self.__isNewPathJob
        except Exception as e:
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)} @ {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}')
            return False

    def isCompensationTime(self):
        return self.__kalmanFilter.isCompensationTime()

    def calculateCompensatedVector(self):
        estimatedCurrentState = self.__kalmanFilter.getEstimatedState()
        currentJob = self.__jobs[0]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()+1]

        # self.__currentMovementVector = self.__kalmanFilter.getCompensatedVectorAutomagic(estimatedCurrentState, nextCoordinate)
        compensatedVector = self.__kalmanFilter.getCompensatedVectorAutomagic(estimatedCurrentState, nextCoordinate)
        translatedCompensatedVector = self.translateKalmanFeedbackToRobotFeedback(compensatedVector)
        self.__currentMovementVector = translatedCompensatedVector

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

        # descomentar esto si se quiere que el robot se mueva en la direccion que indica la nueva coordenada sin rotacion, no se orienta al robot (full omnidireccional)
        # newDesiredVector = [macros.DEFAULT_ROBOT_MOVE_DISTANCE, filtro_positivo[0]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, filtro_positivo[1]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, 0.00]

        # esta operacion calcula el nuevo movimiento basandose en que siempre el robot queda orientado para que una de sus caras siempre mire a la pared
        # se tiene un -1.0*abs(...) en la componente Y de velocidad por la ubicacion del sensor magnetico, que esta colocado en sentido del eje -Y
        # el robot siempre se va a mover a lo largo de su propio eje -Y (que en realidad puede ser cualquier eje relativo del robot)
        # newDesiredVector = [macros.DEFAULT_ROBOT_MOVE_DISTANCE, 0.00, -1.0*abs(filtro_positivo[1]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY), 0.00]
        newDesiredVector = [macros.DEFAULT_ROBOT_MOVE_DISTANCE, 0.00, 1.0*abs(macros.DEFAULT_ROBOT_LINEAR_VELOCITY), 0.00]

        # if(transitionIndex > 1): # FIXME deberia ser >0 cuando se arregle que el disparo de la red se haga y recien cuando llegue impacte el estado
        if(transitionIndex > 0): # FIXME deberia ser >0 cuando se arregle que el disparo de la red se haga y recien cuando llegue impacte el estado
            if(not self.__isRotating):
                previousCoordinate = currentJob.getCoordinatesPathSequence()[transitionIndex-1]
                if(self.cambioDireccion(previousCoordinate, currentCoordinate, nextCoordinate)):
                    logging.debug(f'[{__name__}] cambio de direccion (!)')
                    self.__kalmanFilter.notifyDirectionChange()
                    self.__isRotating = True
            elif(self.__isRotating):
                self.__isRotating = False
                self.__robot.setCurrentOrientation(self.__nextOrientation)
                logging.debug(f'[{__name__}] robot new orientation = {self.__robot.getCurrentOrientation()}')

        if(self.__isRotating):
            robotCurrentOrientation = self.__robot.getCurrentOrientation()
            rotationDistance = macros.DEFAULT_ROBOT_ROTATE_180_DEG_DISTANCE
            rotationVelocity = macros.DEFAULT_ROBOT_ANGULAR_VELOCITY

            # esto existe porque cuando filtro_positivo[1] > 0, significa que debe moverse a lo largo del eje +Y, pero como el eje +Y incrementa "hacia abajo"
            # en el mapa, se invierte el sentido
            filtro_positivo_eje_y_invertido = (filtro_positivo[0], -filtro_positivo[1])

            grados, direccion = self.__calculateRotation(self.__robot.getCurrentOrientationAsVector(), filtro_positivo_eje_y_invertido)
            logging.debug(f'[{__name__}] debe girar ---> {grados} / {direccion}')

            if(grados == 90):
                rotationDistance = macros.DEFAULT_ROBOT_ROTATE_180_DEG_DISTANCE/2
                if(direccion == "izquierda"):
                    self.__nextOrientation = (self.__robot.getCurrentOrientation() + macros.ORIENTATION_90_DEGREE) % 4
                elif(direccion == "derecha"):
                    self.__nextOrientation = (self.__robot.getCurrentOrientation() - macros.ORIENTATION_90_DEGREE) % 4
            elif(grados == 180):
                rotationDistance = macros.DEFAULT_ROBOT_ROTATE_180_DEG_DISTANCE
                self.__nextOrientation = (self.__robot.getCurrentOrientation() + macros.ORIENTATION_180_DEGREE) % 4
            else:
                rotationDistance = 0
                self.__nextOrientation = robotCurrentOrientation
                logging.error(f'[{__name__}] ERROR')

            if(direccion == "izquierda"):
                rotationVelocity = macros.DEFAULT_ROBOT_ANGULAR_VELOCITY
            elif(direccion == "derecha"):
                rotationVelocity = -macros.DEFAULT_ROBOT_ANGULAR_VELOCITY

            newDesiredVector = [rotationDistance, 0.00, 0.00, rotationVelocity]

        self.__currentMovementVector = newDesiredVector
        return (self.__currentMovementVector != None)

    def cambioDireccionDEPRECATED(self, currentCoordinate, nextCoordinate):
        if(currentCoordinate[0] != nextCoordinate[0] or currentCoordinate[1] != nextCoordinate[1]):
            return True
        return False

    def cambioDireccion(self, previousCoordinate, currentCoordinate, nextCoordinate):
        x1 = previousCoordinate[0]
        y1 = previousCoordinate[1]
        x2 = currentCoordinate[0]
        y2 = currentCoordinate[1]
        x3 = nextCoordinate[0]
        y3 = nextCoordinate[1]
        return (x2 - x1) * (y3 - y1) != (y2 - y1) * (x3 - x1)

    def sendSetpointToRobot(self):
        try:
            movementVector = self.getMovementVector()
            setpoint_message = self.traslateMovementVectorToMessage(movementVector)
            msg = self.__robot.getMqttClient().publish(self.__robot.getRobotSendSetpointTopic(), setpoint_message, qos=0)
            msg.wait_for_publish()
            logging.debug(f'[{__name__}] sent setpoint to robot | {setpoint_message}')
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

        currentJob = self.__jobs[0]
        nextCoordinate = currentJob.getCoordinatesPathSequence()[currentJob.getTransitionIndex()+1]

        logging.debug(f'[{__name__}] radius {radius} | estCurrCoord {estimatedCurrentCoordinate} | nextCoord {nextCoordinate}')

        deltaX = abs(estimatedCurrentCoordinate[0] - nextCoordinate[0])
        deltaY = abs(estimatedCurrentCoordinate[1] - nextCoordinate[1])
        return (deltaX <= radius and deltaY <= radius)

    def setCoordinateConfirmation(self, confirmationValue):
        logging.debug(f'[{__name__}] SETTING COORD CONFIRMATION ...')
        currentJob = self.__jobs[0]
        destinationCoordinateTransition = currentJob.getTransitionsPathSequence()[currentJob.getTransitionIndex()]
        logging.debug(f'[{__name__} @ {self.__robotID}] confirmation of transition {destinationCoordinateTransition}')
        return self.__monitor.setCoordinateConfirmation(self.__robotID, destinationCoordinateTransition, confirmationValue)

    # robotFeedback recibe algo como [dx, vx, dy, vy]
    def translateRobotFeedbackToKalmanFeedback(self, robotFeedback):
        # dado que el robot siempre se va a mover a lo largo de su eje +Y, debemos convertir este vector "local" del robot
        # a un vector "global" que toma el kalman. Esto es porque kalman estima el estado del robot en un marco de referencia
        # igual al del mapa.
        translatedOutput = []
        robotCurrentOrientation = self.__robot.getCurrentOrientation()

        if(robotCurrentOrientation == macros.ORIENTATION_0_DEGREE):
            # aumento +Y robot -> aumento +Y mapa
            translatedOutput = [robotFeedback[0], -robotFeedback[1], robotFeedback[2], robotFeedback[3]]

        elif(robotCurrentOrientation == macros.ORIENTATION_90_DEGREE):
            # aumento +Y robot -> aumento +X mapa
            translatedOutput = [robotFeedback[2], robotFeedback[3], robotFeedback[0], robotFeedback[1]]

        elif(robotCurrentOrientation == macros.ORIENTATION_180_DEGREE):
            # aumento +Y robot -> aumento -Y mapa
            translatedOutput = [robotFeedback[0], robotFeedback[1], robotFeedback[2], -robotFeedback[3]]

        elif(robotCurrentOrientation == macros.ORIENTATION_270_DEGREE):
            # aumento +Y robot -> aumento -X mapa
            translatedOutput = [robotFeedback[2], -robotFeedback[3], robotFeedback[0], -robotFeedback[1]]

        return translatedOutput

    # kalmanFeedback recibe algo como [distance, vx, vy, vr]
    def translateKalmanFeedbackToRobotFeedback(self, kalmanFeedback):
        # dado que el kalman trabaja con las coordenadas globales del mapa, debemos convertir los vectores de compensacion
        # calculados al marco de referencia de coordenadas locales del robot (que siempre se mueve a lo largo de su eje +Y)
        translatedOutput = []
        robotCurrentOrientation = self.__robot.getCurrentOrientation()

        if(robotCurrentOrientation == macros.ORIENTATION_0_DEGREE):
            # aumento +Y mapa -> aumento +Y robot
            translatedOutput = [kalmanFeedback[0], kalmanFeedback[1], kalmanFeedback[2], kalmanFeedback[3]]

        elif(robotCurrentOrientation == macros.ORIENTATION_90_DEGREE):
            # aumento +X mapa -> aumento +Y robot
            translatedOutput = [kalmanFeedback[0], kalmanFeedback[2], kalmanFeedback[1], kalmanFeedback[3]]

        elif(robotCurrentOrientation == macros.ORIENTATION_180_DEGREE):
            # aumento -Y mapa -> aumento +Y robot
            translatedOutput = [kalmanFeedback[0], kalmanFeedback[1], -kalmanFeedback[2], kalmanFeedback[3]]

        elif(robotCurrentOrientation == macros.ORIENTATION_270_DEGREE):
            # aumento -X mapa -> aumento +Y robot
            translatedOutput = [kalmanFeedback[0], kalmanFeedback[2], -kalmanFeedback[1], kalmanFeedback[3]]

        return translatedOutput

    def __calculateRotation(self, currentOrientationVector, destinationOrientationVector):
        # Convertir los vectores a numpy arrays
        v1 = np.array(currentOrientationVector)
        v2 = np.array(destinationOrientationVector)

        # Calcular el ángulo entre los dos vectores
        angulo = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
        angulo_grados = np.degrees(angulo)

        # Normalizar el ángulo entre -180 y 180 grados
        angulo_grados = (angulo_grados + 360) % 360
        if angulo_grados > 180:
            angulo_grados -= 360

        if (angulo_grados > 0):
            direccion = "izquierda"
        elif (angulo_grados < 0):
            direccion = "derecha"
        else:
            direccion = "ninguna"

        logging.debug(f'[{__name__}] vectores ---> orientacion actual {v1} / orientacion destino {v2} / angulo grados {angulo_grados} ({angulo} rad) / direccion {direccion}')
        return abs(angulo_grados), direccion

    def run(self):

        try:
            if(len(self.__jobs) <= 0):
                return "NO_JOBS"

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
                    self.__isNewPathJob = False
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
            self.__isNewPathJob = False
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)} @ {type(e).__name__}, {__file__}, {e.__traceback__.tb_lineno}')
            exit()
            return "NO_JOBS"

