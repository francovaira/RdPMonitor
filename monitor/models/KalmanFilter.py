import numpy as np

class KalmanFilter:
    def __init__(self):
        self.__DELTA_T = 0.5 # expresado en segundos

        self.__x_0  = 0 # Posicion inicial - expresado en metros
        self.__vx_0 = 0 # Velocidad inicial - expresado en m/seg
        self.__a_0  = 0 # Aceleracion inicial - expresado en m/seg^2

        self.__delta_Px     = 20 # valor inicial de la varianza de proceso - expresado en metros
        self.__delta_Pvx    = 5 # valor inicial de la varianza de proceso - expresado en m/seg

        # observation errors - ver que significan
        self.__delta_x = 2
        self.__delta_vx = 1

        self.__Xkm1 = np.array([[self.__x_0], [self.__vx_0]]) # estado inicial de posicion y velocidad 
        self.__Pkm1 = np.array([[self.__delta_Px**2, 0], [0, self.__delta_Pvx**2]]) # estado inicial de la matriz de covarianza de proceso
        self.__Xkp = self.__Xkm1

        # R is a 2x2 matrix R = [[delta_x^2, 0], [0, delta_vx^2]]
        self.__R = np.array([[self.__delta_x**2, 0], [0, self.__delta_vx**2]])

    def inputMeasurementUpdate(self, inputMeasurement):
        Ykmx = 0
        Ykmvx = 0

        Ykmx = Ykmx + inputMeasurement[0] # acumulativo de distancia - FIXME no deberia hacerse aca, deberia llegar desde afuera asi
        Ykmvx = inputMeasurement[1]
        Yk = np.array([[Ykmx], [Ykmvx]])

        self.__Xkp = self.__calculatePredictedState(self.__Xkm1)
        Pkp = self.__calculateProcessCovarianceMatrix(self.__Pkm1)
        K = self.__calculateKalmanGain(Pkp, self.__R)

        Xk = self.__calculateNewEstimatedState(self.__Xkp, K, Yk)
        Pk = self.__calculateNewProcessCovarianceMatrix(Pkp, K)

        self.__Xkm1 = Xk
        self.__Pkm1 = Pk

    def getEstimatedState(self):
        # returns a 2x1 matrix *X*k = [Xk, Vk]
        return self.__Xkm1

    # retorna un vector diciendo que tan desviado esta el estado estimado del predecido (el punto deseado en el DELTA_T)
    def getDeltaEstimatedAndPredictedState(self):
        return self.__Xkm1 - self.__Xkp

    def __calculatePredictedState(self, Xkm1):
        # returns a 2x1 matrix  *X*kp = [Xkp, Vxkp]

        A_matrix = np.array([[1, self.__DELTA_T], [0, 1]])
        B_matrix = np.array([[0.5*(self.__DELTA_T**2)], [self.__DELTA_T]])
        wk_matrix = np.array([[0], [0]])
        a0_matrix = np.array([[self.__a_0]])

        Xkp = np.array(A_matrix.dot(Xkm1) + B_matrix.dot(a0_matrix) + wk_matrix)
        return Xkp

    def __calculateProcessCovarianceMatrix(self, Pkm1):
        # returns a 2x2 matrix *P*kp = [[delta_Px^2, 0], [0, delta_Pvx^2]]

        A_matrix = np.array([[1, self.__DELTA_T], [0, 1]])
        Qk_matrix = np.array([[0, 0], [0, 0]])

        Pkp = A_matrix.dot(Pkm1).dot(A_matrix.transpose()) + Qk_matrix

        # make zero all elements except diagonal
        Pkp_diagonal = Pkp*np.identity(len(Pkp))
        return Pkp_diagonal

    def __calculateKalmanGain(self, Pkp, R):
        # returns a 2x2 matrix K = [[Kpx, 0], [0, Kpvx]]

        H_matrix = np.array([[1, 0], [0, 1]])

        numerator = Pkp.dot(H_matrix.transpose())
        denominator = H_matrix.dot(Pkp).dot(H_matrix.transpose()) + R
        K = self.__divideMatrices(numerator, denominator)
        return K

    def __calculateNewEstimatedState(self, Xkp, K, Yk):
        # returns a 2x1 matrix *X*k = [Xk, Vk]

        H_matrix = np.array([[1, 0], [0, 1]])

        Xk = Xkp + K.dot(Yk - H_matrix.dot(Xkp))
        return Xk

    def __calculateNewProcessCovarianceMatrix(self, Pkp, K):
        # returns a 2x2 matrix *P*k = [[delta_Px^2, 0], [0, delta_Pvx^2]]

        I_matrix = np.array([[1, 0], [0, 1]])
        H_matrix = np.array([[1, 0], [0, 1]])

        Pk = (I_matrix - K.dot(H_matrix)).dot(Pkp)
        return Pk

    def __divideMatrices(self, numerator, denominator):
        # this function divides two matrices and puts 0 when dividing by 0 instead of NaN (np.divide throws NaN)
        result = []
        for i in range(2):
            result.append([])
            for j in range(2):
                result[i].append(0)
                if(denominator[i][j] == 0):
                    result[i][j] = 0
                else:
                    result[i][j] = numerator[i][j] / denominator[i][j]
        return np.array(result)


# def main():
#     kalmanFilter = KalmanFilter()

#     measurements = []
#     # measurements.append([4000, 280])
#     # measurements.append([4260, 282])
#     # measurements.append([4540, 285])
#     # measurements.append([4825, 286])
#     # measurements.append([5110, 290])
#     measurements.append([0.08, 0.18])
#     measurements.append([0.10, 0.22])
#     measurements.append([0.12, 0.25])
#     measurements.append([0.13, 0.27])
#     measurements.append([0.11, 0.24])

#     distanciaRecorrida = 0
#     for i in range(3*len(measurements)):
#         distanciaRecorrida = distanciaRecorrida + measurements[i%len(measurements)][0]
#         velocidad = measurements[i%len(measurements)][1]
#         inputMeasurement = (distanciaRecorrida, velocidad)
#         kalmanFilter.inputMeasurementUpdate(inputMeasurement)
#         print(f"INPUT MEASUREMENT {measurements[i%len(measurements)]} || INPUT MEASUREMENT ACUMULADO {inputMeasurement}")
#         print(f"KALMAN ESTIMATED:\n{kalmanFilter.getEstimatedState()}\n")
#         print(f"DELTA ESTIMATED/PREDICTED:\n{kalmanFilter.getDeltaEstimatedAndPredictedState()}\n")
#         print("====================================")

# if __name__ == "__main__":
#     main()
