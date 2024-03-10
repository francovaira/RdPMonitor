from .KalmanFilter import KalmanFilter
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
        self.__measurementAccum = np.array(inputMeasurement) + np.array(self.__measurementAccum) # FIXME esta logica meterla dentro de cada filtro de kalman, no en el 2D

        self.__kalmanFilterX.inputMeasurementUpdate(self.__measurementAccum[0])
        self.__kalmanFilterY.inputMeasurementUpdate(self.__measurementAccum[1])
        logging.debug(f'[{__name__}] new measurement       <{inputMeasurement}>')
        logging.debug(f'[{__name__}] new measurement accum <{self.__measurementAccum}>')

        self.__estimatedStatePeriodCount = self.__estimatedStatePeriodCount + 1
        if(self.__estimatedStatePeriodCount >= macros.KALMAN_ESTIMATED_STATE_PERIOD):
            self.__periodicEstimatedState = self.getEstimatedState()
            self.__estimatedStatePeriodCount = 0

    # devuelve la medicion actualizada cada N actualizaciones de medicion
    def getPeriodicEstimatedState(self):
        returnValue = self.__periodicEstimatedState
        self.__periodicEstimatedState = np.array([[0,0], [0,0]])
        return returnValue

    # devuelve una matriz de 2x2: *E*k = [[Xk, VXk]
    #                                    [Yk, VYk]]
    def getEstimatedState(self):
        x_est_state = self.__kalmanFilterX.getEstimatedState()
        y_est_state = self.__kalmanFilterY.getEstimatedState()
        return np.array([x_est_state, y_est_state])

    def setInitialState(self, initialState):
        self.__measurementAccum = initialState
        self.__kalmanFilterX.setInitialState(initialState[0])
        self.__kalmanFilterY.setInitialState(initialState[1])


# def main():
#     kalmanFilter = KalmanFilter2D()

#     logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s',
#                         datefmt='%m/%d/%Y %I:%M:%S',
#                         level=logging.DEBUG)

#     measurements = []
#     measurements.append([[0.08, 0.18], [0.09, 0.17]])
#     measurements.append([[0.10, 0.22] ,[0.11, 0.21]])
#     measurements.append([[0.12, 0.25] ,[0.12, 0.26]])
#     measurements.append([[0.13, 0.27] ,[0.10, 0.28]])
#     measurements.append([[0.11, 0.24] ,[0.11, 0.25]])

#     for i in range(3):
#         kalmanFilter.inputMeasurementUpdate(measurements[i])
#         kalmanFilter.getEstimatedState()

# if __name__ == "__main__":
#     main()



