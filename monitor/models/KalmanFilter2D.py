#from .KalmanFilter import KalmanFilter
from KalmanFilter import KalmanFilter
import macros
import numpy as np
import logging


class KalmanFilter2D:
    def __init__(self):
        self.__kalmanFilterX = KalmanFilter()
        self.__kalmanFilterY = KalmanFilter()
        self.__estimatedStatePeriodCount = 0
        self.__periodicEstimatedState = np.array([[0,0], [0,0]])
        self.__measurementAccum = np.array([[0,0], [0,0]])

    # recibe una matriz con el formato: [[deltaX, deltaVX], [deltaY, deltaVY]]
    def inputMeasurementUpdate(self, inputMeasurement):
        logging.debug(f'[{__name__}] new measurement <{inputMeasurement}>')

        distanceMeasurementAccum = np.array([inputMeasurement[0][0] + self.__measurementAccum[0][0], inputMeasurement[1][0] + self.__measurementAccum[1][0]])
        self.__measurementAccum[0][0] = distanceMeasurementAccum[0]
        self.__measurementAccum[1][0] = distanceMeasurementAccum[1]
        self.__measurementAccum[0][1] = inputMeasurement[0][1]
        self.__measurementAccum[1][1] = inputMeasurement[1][1]
        logging.debug(f'[{__name__}] new measurement accum <{self.__measurementAccum}>')

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


def main():
    kalmanFilter = KalmanFilter2D()

    logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S',
                        level=logging.DEBUG)

    coordinatesSequence = [(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)]
    initCoordinate = coordinatesSequence[0]
    initVelocities = [0.00, 0.25]
    kalmanFilter.setInitialState([[initCoordinate[0], initVelocities[0]], [initCoordinate[1], initVelocities[1]]])

    measurements = []
    #                       [dx]   [vx]        [dy]   [vy]
    measurements.append([[  0.00,  0.00 ] , [  0.25,  0.25]])
    measurements.append([[  0.00,  0.00 ] , [  0.22,  0.23]])
    measurements.append([[  0.00,  0.00 ] , [  0.24,  0.25]])
    measurements.append([[  0.00,  0.00 ] , [  0.26,  0.27]])
    measurements.append([[  0.00,  0.00 ] , [  0.25,  0.26]])

    for i in range(len(measurements)):
        kalmanFilter.inputMeasurementUpdate(measurements[i])
        estimatedState = kalmanFilter.getEstimatedState()
        logging.debug(f'[{__name__}] estimated state: {estimatedState}')

        #expectedCurrentCoordinate = tuple((coordinatesSequence[i][0]*macros.DEFAULT_CELL_SIZE+(i*initVelocities[0]), coordinatesSequence[i][1]*macros.DEFAULT_CELL_SIZE+(i*initVelocities[1])))
        #if(i < len(measurements)-1):
            #expectedNextCoordinate = tuple((coordinatesSequence[i+1][0]*macros.DEFAULT_CELL_SIZE+(i*initVelocities[0]), coordinatesSequence[i+1][1]*macros.DEFAULT_CELL_SIZE+(i*initVelocities[1])))
            #estimatedCurrentState = kalmanFilter.getEstimatedState()
            #compensatedVector = getCompensatedVectorA(estimatedCurrentState, expectedCurrentCoordinate, expectedNextCoordinate)

        logging.debug(f'\n\n')

if __name__ == "__main__":
    main()

