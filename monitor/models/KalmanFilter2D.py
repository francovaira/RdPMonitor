#from .KalmanFilter import KalmanFilter
from KalmanFilter import KalmanFilter
import macros
import operator
import numpy as np
import logging
import random


class KalmanFilter2D:
    def __init__(self):
        self.__kalmanFilterX = KalmanFilter()
        self.__kalmanFilterY = KalmanFilter()
        self.__measurementCount = 0
        self.__isCompensationTime = False
        self.__measurementAccum = np.array([[0,0], [0,0]])

    # recibe una matriz con el formato: [[deltaX, VX], [deltaY, VY]]
    def inputMeasurementUpdate(self, inputMeasurement):
        logging.debug(f'[{__name__}] MEASUREMENT UPDATE - new measurement <{inputMeasurement}>')

        x_measure_accum = inputMeasurement[0][0] * (-1 if inputMeasurement[0][1] < 0 else 1) + self.__measurementAccum[0][0]
        y_measure_accum = inputMeasurement[1][0] * (-1 if inputMeasurement[1][1] < 0 else 1) + self.__measurementAccum[1][0]

        #distanceMeasurementAccum = np.array([inputMeasurement[0][0] + self.__measurementAccum[0][0], inputMeasurement[1][0] + self.__measurementAccum[1][0]])
        distanceMeasurementAccum = np.array([x_measure_accum, y_measure_accum])
        self.__measurementAccum[0][0] = distanceMeasurementAccum[0]
        self.__measurementAccum[1][0] = distanceMeasurementAccum[1]
        self.__measurementAccum[0][1] = inputMeasurement[0][1]
        self.__measurementAccum[1][1] = inputMeasurement[1][1]
        logging.debug(f'[{__name__}] MEASUREMENT UPDATE - new measurement accum <{self.__measurementAccum}>')

        self.__kalmanFilterX.inputMeasurementUpdate(self.__measurementAccum[0])
        self.__kalmanFilterY.inputMeasurementUpdate(self.__measurementAccum[1])
        self.__measurementCount = self.__measurementCount + 1

    # retorna True si se actualizo el estado tras N mediciones
    def isCompensationTime(self):
        if(self.__measurementCount >= macros.KALMAN_ESTIMATED_STATE_PERIOD):
            self.__measurementCount = 0
            return True
        return False

    # devuelve una matriz de 2x2: *E*k = [[Xk, VXk],[Yk, VYk]]
    def getEstimatedState(self):
        x_est_state = self.__kalmanFilterX.getEstimatedState()
        y_est_state = self.__kalmanFilterY.getEstimatedState()
        return np.array([x_est_state, y_est_state])

    def setInitialState(self, initialState):
        self.__measurementAccum = initialState
        self.__kalmanFilterX.setInitialState(initialState[0])
        self.__kalmanFilterY.setInitialState(initialState[1])

    # devuelve el vector de compensacion en formato [dist_comp, vx_comp, vy_comp, vr_comp]
    def getCompensatedVectorAutomagic(self, estimatedCurrentState, expectedNextCoordinate):
        logging.debug(f'[{__name__}] entre a calcular vector comp | estimated curr state :{estimatedCurrentState} | expected next coordinate: {expectedNextCoordinate}\n')

        # posicion estimada actual
        x_est_curr = estimatedCurrentState[0][0]
        y_est_curr = estimatedCurrentState[1][0]

        # posicion expected siguiente
        x_exp_next = expectedNextCoordinate[0]
        y_exp_next = expectedNextCoordinate[1]

        compensationDistance = np.hypot([x_exp_next-x_est_curr], [y_exp_next-y_est_curr])

        if(np.abs(x_exp_next - x_est_curr) > 0): # desplazamiento en X
            dist_comp_x = x_exp_next - x_est_curr
            dist_comp_y = y_est_curr - y_exp_next

            if(dist_comp_x != 0):
                alpha = np.arctan([dist_comp_y / dist_comp_x])
                vx_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.cos(alpha)
                vy_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.sin(alpha)

                compensationVelocityVector = [compensationDistance[0], vx_comp[0], vy_comp[0], 0.00]
                logging.debug(f'[{__name__}] compensacion vector DESP X | alpha: {alpha} | comp distance: {compensationDistance}')
                return compensationVelocityVector

        elif(np.abs(y_exp_next - y_est_curr) > 0): # desplazamiento en Y
            dist_comp_x = x_est_curr - x_exp_next
            dist_comp_y = y_exp_next - y_est_curr

            if(dist_comp_y != 0):
                alpha = np.arctan([dist_comp_x / dist_comp_y])
                vx_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.sin(alpha)
                vy_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.cos(alpha)

                compensationVelocityVector = [compensationDistance[0], vx_comp[0], vy_comp[0], 0.00]
                logging.debug(f'[{__name__}] compensacion vector DESP Y | dcx {dist_comp_x} | dcy {dist_comp_y} | alpha: {alpha} | comp distance: {compensationDistance}')
                return compensationVelocityVector


def getMeasurementWithNoise(perfectMeasurement):
    porcentajeError = 5
    imperfectMeasurement = [[0,0], [0,0]]

    for i in range(2):
        for j in range(2):
            sign = -1 if random.random() < 0.5 else 1
            noise = sign * random.random() * (porcentajeError/100)
            imperfectMeasurement[i][j] = perfectMeasurement[i][j] + noise
    return imperfectMeasurement

def getDesiredMovementVector(currentCoordinate, nextCoordinate):
    res = tuple(map(operator.sub, nextCoordinate, currentCoordinate)) # obtiene el delta entre ambas coordenadas
    filtro_negativo = tuple(map(lambda x: -1 if (x<0) else x, res)) # normaliza la tupla
    filtro_positivo = tuple(map(lambda x: 1 if (x>0) else x, filtro_negativo))
    desiredVector = [macros.DEFAULT_ROBOT_MOVE_DISTANCE, filtro_positivo[0]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, filtro_positivo[1]*macros.DEFAULT_ROBOT_LINEAR_VELOCITY, 0.00]
    return desiredVector

def coordinateIsNearCoordinate(currentCoordinate, destinationCoordinate, radius):
    dist = np.linalg.norm(currentCoordinate - destinationCoordinate)
    return (dist <= radius)

# PROXIMO A HACER: hacer que ande cuando tiene mediciones con ruido - es basicamente modificar la funcion coordinateIsNearCoordinate


def main():
    kalmanFilter = KalmanFilter2D()

    logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        level=logging.DEBUG)

    coordinatesSequence = [(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)]
    #coordinatesSequence = [(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (4, 7), (3, 7), (2, 7), (1, 7), (1, 6), (1, 5), (1, 4)]
    initCoordinate = coordinatesSequence[0]
    initVelocities = [0.00, 0.00]
    kalmanFilter.setInitialState([[initCoordinate[0], initVelocities[0]], [initCoordinate[1], initVelocities[1]]])

    deltaT = 0
    robotSentFinishedState = False
    radius = 0.05 # expresado en metros. Radio minimo en cual debe estar el robot para considerar que llego a la coordenada esperada
    isRobotInTravel = False

    #                 [dist]  [vx]   [vy]   [vr]
    desiredVector = [  1.00,  0.00,  0.25,  0.00  ]

    #                 [dx]  [vx]       [dy]  [vy]
    measurements = [[ 0.00, 0.00 ] , [ 0.25, 0.25]]

    while(1):

        for index_coordinate in range(len(coordinatesSequence)-1):

            currentCoordinate = coordinatesSequence[index_coordinate]
            nextCoordinate = coordinatesSequence[index_coordinate+1]
            logging.debug(f'[{__name__}] busque la nueva coordenada <{nextCoordinate}>')

            # 1) generar vector para ir de [currentCoordinate] a [nextCoordinate]
            desiredVector = getDesiredMovementVector(currentCoordinate, nextCoordinate)

            # 2) se envia el vector deseado al robot, ahora el robot empieza a mandar feedback cada X tiempo y va acercandose al destino

            # 3) se espera que las mediciones completen el trayecto para ir de la coordenada [currentCoordinate] a [nextCoordinate]
            isRobotInTravel = True
            while(isRobotInTravel):

                # 4) espera que llegue una medicion o que el robot mande un mensaje que llego
                if(robotSentFinishedState):
                    break

                # 5) espera una medicion, toma el deltaT entre la ultima medicion y la actual
                deltaT = 1.0

                # 6) actualiza kalman
                #measurements = [ [ 0.25*(1 if desiredVector[1] != 0 else 0), desiredVector[1]], [ 0.25*(1 if desiredVector[2] != 0 else 0), desiredVector[2]] ]
                kalmanFilter.inputMeasurementUpdate(measurements)

                # 7) obtiene el estado esperado y el real y verifica si llego a la coordenada
                estimatedCurrentState = kalmanFilter.getEstimatedState()
                estimatedCurrentCoordinate = np.array([estimatedCurrentState[0][0], estimatedCurrentState[1][0]])
                logging.debug(f'[{__name__}] estimated state: {estimatedCurrentState}\n')

                if(coordinateIsNearCoordinate(estimatedCurrentCoordinate, nextCoordinate, radius)):
                    # 7.1) llego a la coordenada esperada, busco la siguiente coordenada y actualizo el vector a enviar
                    logging.debug(f'[{__name__}] llegue a la coordenada <{nextCoordinate}> | busco la siguiente...')
                    isRobotInTravel = False
                    continue

                # 8) no llego a la coordenada aun, veo si kalman quiere compensar o no
                if(kalmanFilter.isCompensationTime()):
                    # 8.1) kalman nos devuelve el nuevo vector de movimiento para llegar a nextCoordinate
                    compensatedVector = kalmanFilter.getCompensatedVectorAutomagic(estimatedCurrentState, nextCoordinate)
                    desiredVector = compensatedVector
                    logging.debug(f'[{__name__}] vector de compensacion: {compensatedVector}')

                else:
                    # 8.2) kalman no va a compensar, sigo esperando mediciones
                    continue

                logging.debug(f'[{__name__}] ------------------------------------------------\n\n')

            logging.debug(f'[{__name__}] ###############################################################\n')
        # end foreach(coordinatesSequence)

        logging.debug(f'[{__name__}] fin de celdas...\n\n')
        exit()



if __name__ == "__main__":
    main()

