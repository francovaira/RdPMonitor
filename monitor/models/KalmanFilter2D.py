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
        self.__estimatedStatePeriodCount = 0
        self.__periodicEstimatedState = np.array([[0,0], [0,0]])
        self.__measurementAccum = np.array([[0,0], [0,0]])

    # recibe una matriz con el formato: [[deltaX, VX], [deltaY, VY]]
    def inputMeasurementUpdate(self, inputMeasurement):
        logging.debug(f'[{__name__}] MEASUREMENT UPDATE - new measurement <{inputMeasurement}>')

        distanceMeasurementAccum = np.array([inputMeasurement[0][0] + self.__measurementAccum[0][0], inputMeasurement[1][0] + self.__measurementAccum[1][0]])
        self.__measurementAccum[0][0] = distanceMeasurementAccum[0]
        self.__measurementAccum[1][0] = distanceMeasurementAccum[1]
        self.__measurementAccum[0][1] = inputMeasurement[0][1]
        self.__measurementAccum[1][1] = inputMeasurement[1][1]
        logging.debug(f'[{__name__}] MEASUREMENT UPDATE - new measurement accum <{self.__measurementAccum}>')

        self.__kalmanFilterX.inputMeasurementUpdate(self.__measurementAccum[0])
        self.__kalmanFilterY.inputMeasurementUpdate(self.__measurementAccum[1])

        self.__estimatedStatePeriodCount = self.__estimatedStatePeriodCount + 1
        if(self.__estimatedStatePeriodCount >= macros.KALMAN_ESTIMATED_STATE_PERIOD):
            self.__periodicEstimatedState = self.getEstimatedState()
            self.__estimatedStatePeriodCount = 0

    # devuelve la medicion actualizada cada N actualizaciones de medicion
    def getPeriodicEstimatedState(self):
        returnValue = self.__periodicEstimatedState
        self.__periodicEstimatedState = np.array([[0,0], [0,0]])
        return returnValue

    # devuelve una matriz de 2x2: *E*k = [[Xk, VXk],[Yk, VYk]]
    def getEstimatedState(self):
        x_est_state = self.__kalmanFilterX.getEstimatedState()
        y_est_state = self.__kalmanFilterY.getEstimatedState()
        return np.array([x_est_state, y_est_state])

    def setInitialState(self, initialState):
        self.__measurementAccum = initialState
        self.__kalmanFilterX.setInitialState(initialState[0])
        self.__kalmanFilterY.setInitialState(initialState[1])

# devuelve el vector de compensacion en formato [dist_comp, vx_comp, vy_comp]
def getCompensatedVector(estimatedCurrentState, expectedCurrentCoordinate, expectedNextCoordinate):
    logging.debug(f'[{__name__}] compensation vector | estimated curr state :{estimatedCurrentState} | expected curr coordinate: {expectedCurrentCoordinate} | expected next coordinate: {expectedNextCoordinate}\n')

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

    dist_comp_x = x_est_curr - x_exp_curr
    dist_comp_y = y_exp_next - y_est_curr

    if(dist_comp_x != 0 or dist_comp_y != 0):
        alpha = np.arctan([dist_comp_x / dist_comp_y])
        vx_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.sin(alpha)
        vy_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.cos(alpha)
        compensationVelocityVector = [compensationDistance[0], vx_comp[0], vy_comp[0]]

        logging.debug(f'[{__name__}] compensation vector | alpha: {alpha} | comp distance: {compensationDistance}')
        return compensationVelocityVector

def getCompensatedVectorAutomagic(estimatedCurrentState, expectedCurrentCoordinate, expectedNextCoordinate):
    logging.debug(f'[{__name__}] compensation vector | estimated curr state :{estimatedCurrentState} | expected curr coordinate: {expectedCurrentCoordinate} | expected next coordinate: {expectedNextCoordinate}\n')

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

    if(np.abs(x_exp_next - x_est_curr) > 0): # desplazamiento en X
        dist_comp_x = x_exp_next - x_est_curr
        dist_comp_y = y_est_curr - y_exp_curr

        if(dist_comp_x != 0):
            alpha = np.arctan([dist_comp_y / dist_comp_x])
            vx_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.cos(alpha)
            vy_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.sin(alpha)

            compensationVelocityVector = [compensationDistance[0], vx_comp[0], vy_comp[0]]
            logging.debug(f'[{__name__}] compensation vector | alpha: {alpha} | comp distance: {compensationDistance}')
            return compensationVelocityVector

    elif(np.abs(y_exp_next - y_est_curr) > 0): # desplazamiento en Y
        dist_comp_x = x_est_curr - x_exp_curr
        dist_comp_y = y_exp_next - y_est_curr

        if(dist_comp_y != 0):
            alpha = np.arctan([dist_comp_x / dist_comp_y])
            vx_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.sin(alpha)
            vy_comp = macros.DEFAULT_ROBOT_LINEAR_VELOCITY * np.cos(alpha)

            compensationVelocityVector = [compensationDistance[0], vx_comp[0], vy_comp[0]]
            logging.debug(f'[{__name__}] compensation vector | alpha: {alpha} | comp distance: {compensationDistance}')
            return compensationVelocityVector



# se debe mandar el deltaT que es el tiempo total acumulado transcurrido, el vector deseado tal cual se envio al robot, la coordenada expected previa
def getExpectedCurrentCoordinate(deltaT, desiredVector, expectedPreviousCoordinate):
    vx = desiredVector[1]
    vy = desiredVector[2]

    expected_x = expectedPreviousCoordinate[0] + (vx * deltaT)
    expected_y = expectedPreviousCoordinate[1] + (vy * deltaT)

    return np.array([expected_x, expected_y])

def getMeasurementWithNoise(perfectMeasurement):
    porcentajeError = 10
    imperfectMeasurement = [[0,0], [0,0]]

    for i in range(2):
        for j in range(2):
            sign = -1 if random.random() < 0.5 else 1
            noise = sign * random.random() * (porcentajeError/100)
            imperfectMeasurement[i][j] = perfectMeasurement[i][j] + noise
    return imperfectMeasurement


def main():
    kalmanFilter = KalmanFilter2D()

    logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        level=logging.DEBUG)

    coordinatesSequence = [(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)]
    initCoordinate = coordinatesSequence[0]
    initVelocities = [0.00, 0.00]
    kalmanFilter.setInitialState([[initCoordinate[0], initVelocities[0]], [initCoordinate[1], initVelocities[1]]])

    deltaT = 0
    expectedCurrentCoordinate = []
    lastExpectedCurrentCoordinate = initCoordinate
    index = 0
    measurementCount = 0
    do_compensate = False

    #                 [dist]  [vx]   [vy]   [vr]
    desiredVector = [  1.00,  0.00,  0.25,  0.00  ]

    #                 [dx]  [vx]       [dy]  [vy]
    measurements = [[ 0.00, 0.00 ] , [ 0.25, 0.25]]

    while(1):

        kalmanFilter.inputMeasurementUpdate(measurements)
        #kalmanFilter.inputMeasurementUpdate(getMeasurementWithNoise(measurements))
        estimatedState = kalmanFilter.getEstimatedState()
        logging.debug(f'[{__name__}] estimated state: {estimatedState}\n')
        deltaT = 1.0 # esto despues seria tomado desde el timestamp de la ultima medicion recibida
        measurementCount = measurementCount + 1

        expectedCurrentCoordinate = getExpectedCurrentCoordinate(deltaT, desiredVector, lastExpectedCurrentCoordinate)
        lastExpectedCurrentCoordinate = expectedCurrentCoordinate
        logging.debug(f'[{__name__}] expected current coordinate <{expectedCurrentCoordinate}>')

        if(measurementCount >= 3):
            do_compensate = True
            measurementCount = 0

        if(expectedCurrentCoordinate[1] > coordinatesSequence[index+1][1]): # evalua si en el eje Y pasamos a otra celda
            #do_compensate = True
            index = index + 1
            logging.debug(f'[{__name__}] pasando a la siguiente celda...')

            if(index >= (len(coordinatesSequence)-1)):
                logging.debug(f'[{__name__}] fin de celdas...\n\n')
                exit()

        if(do_compensate):
            expectedNextCoordinate = coordinatesSequence[index+1]
            #compensatedVector = getCompensatedVector(estimatedState, expectedCurrentCoordinate, expectedNextCoordinate)
            compensatedVector = getCompensatedVectorAutomagic(estimatedState, expectedCurrentCoordinate, expectedNextCoordinate)
            logging.debug(f'[{__name__}] vector de compensacion: {compensatedVector}\n\n')
            #desiredVector = [compensatedVector[0], compensatedVector[1], compensatedVector[2], 0.00]

            do_compensate = False

        logging.debug(f'[{__name__}] ----------------------------\n\n')




if __name__ == "__main__":
    main()

