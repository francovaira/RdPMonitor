from .KalmanFilter import KalmanFilter
#from KalmanFilter import KalmanFilter
import logging


class KalmanFilter2D:
    def __init__(self):
        self.__kalmanFilterX = KalmanFilter()
        self.__kalmanFilterY = KalmanFilter()

    # recibe una matriz con el formato: [[deltaX, deltaVX], [deltaY, deltaVY]]
    def inputMeasurementUpdate(self, inputMeasurement):
        deltaX  = inputMeasurement[0][0]
        deltaVX = inputMeasurement[0][1]
        deltaY  = inputMeasurement[1][0]
        deltaVY = inputMeasurement[1][1]

        logging.debug(f'[{__name__}] | deltaX <{deltaX}> | deltaX <{deltaVX}> | deltaY <{deltaY}> | deltaVY <{deltaVY}>')
        self.__kalmanFilterX.inputMeasurementUpdate(inputMeasurement[0])
        self.__kalmanFilterY.inputMeasurementUpdate(inputMeasurement[1])

    # devuelve una matriz de 2x2: *E*k = [Xk, VXk]
    #                                    [Yk, VYk]
    def getEstimatedState(self):
        logging.debug(f'[{__name__}] RETURNING ESTIMATED STATE {[self.__kalmanFilterX.getEstimatedState(), self.__kalmanFilterY.getEstimatedState()]}')
        return [self.__kalmanFilterX.getEstimatedState(),self.__kalmanFilterY.getEstimatedState()]



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



