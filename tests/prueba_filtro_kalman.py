import numpy as np


DELTA_T = 1 # expresado en segundos

x_0 = 4000 # Posicion inicial - expresado en metros
vx_0 = 280 # Velocidad inicial - expresado en m/seg
a_0 = 0 # Aceleracion inicial - expresado en m/seg^2

delta_Px    = 20 # valor inicial de la varianza de proceso - expresado en metros
delta_Pvx   = 5 # valor inicial de la varianza de proceso - expresado en m/seg

# observation errors - ver que significan
delta_x = 2
delta_vx = 1


def calculate_predicted_state(Xkm1):
    # returns a 2x1 matrix  *X*kp = [Xkp, Vxkp]

    A_matrix = np.array([[1, DELTA_T], [0, 1]])
    B_matrix = np.array([[0.5*(DELTA_T**2)], [DELTA_T]])
    wk_matrix = np.array([[0], [0]])
    a0_matrix = np.array([[a_0]])

    Xkp = np.array(A_matrix.dot(Xkm1) + B_matrix.dot(a0_matrix) + wk_matrix)
    return Xkp


def calculate_process_covariance_matrix(Pkm1):
    # returns a 2x2 matrix *P*kp = [[delta_Px^2, 0], [0, delta_Pvx^2]]

    A_matrix = np.array([[1, DELTA_T], [0, 1]])
    Qk_matrix = np.array([[0, 0], [0, 0]])

    Pkp = A_matrix.dot(Pkm1).dot(A_matrix.transpose()) + Qk_matrix

    # make zero all elements except diagonal
    Pkp_diagonal = Pkp*np.identity(len(Pkp))
    return Pkp_diagonal

def calculate_kalman_gain(Pkp, R):
    # returns a 2x2 matrix K = [[Kpx, 0], [0, Kpvx]]

    H_matrix = np.array([[1, 0], [0, 1]])

    numerator = Pkp.dot(H_matrix.transpose())
    denominator = H_matrix.dot(Pkp).dot(H_matrix.transpose()) + R
    K = divide_matrices(numerator, denominator)
    return K

def calculate_new_estimated_state(Xkp, K, Yk):
    # returns a 2x1 matrix *X*k = [Xk, Vk]

    H_matrix = np.array([[1, 0], [0, 1]])

    Xk = Xkp + K.dot(Yk - H_matrix.dot(Xkp))
    return Xk

def calculate_new_process_covariance_matrix(Pkp, K):
    # returns a 2x2 matrix *P*k = [[delta_Px^2, 0], [0, delta_Pvx^2]]

    I_matrix = np.array([[1, 0], [0, 1]])
    H_matrix = np.array([[1, 0], [0, 1]])

    Pk = (I_matrix - K.dot(H_matrix)).dot(Pkp)
    return Pk



def divide_matrices(numerator, denominator):
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

def main():
    Xkm1 = np.array([[x_0], [vx_0]]) # estado inicial de posicion y velocidad 
    Pkm1 = np.array([[delta_Px**2, 0], [0, delta_Pvx**2]]) # estado inicial de la matriz de covarianza de proceso

    Ykmx = 0
    Ykmvx = 0

    measurements = []
    #measurements.append([x_0, vx_0])
    measurements.append([4260, 282])
    measurements.append([4540, 285])
    measurements.append([4825, 286])
    measurements.append([5110, 290])

    # R is a 2x2 matrix R = [[delta_x^2, 0], [0, delta_vx^2]]
    R = np.array([[delta_x**2, 0], [0, delta_vx**2]])

    for i in range(5*len(measurements)):
        Xkp = calculate_predicted_state(Xkm1)
        print(f"PREDICTED STATE\n{Xkp}\n")

        Pkp = calculate_process_covariance_matrix(Pkm1)
        # print(f"PREDICTED PROCESS COVARIANCE MATRIX\n{Pkp}\n")

        K = calculate_kalman_gain(Pkp, R)
        #print(f"KALMAN GAIN\n{K}\n")

        #Ykmx = Ykmx + measurements[i%len(measurements)][0]
        Ykmx = measurements[i%len(measurements)][0]
        Ykmvx = measurements[i%len(measurements)][1]
        Yk = np.array([[Ykmx], [Ykmvx]])
        print(f"MEDICION GENERADA\n{Yk}\n")

        Xk = calculate_new_estimated_state(Xkp, K, Yk)
        print(f"NUEVO ESTADO ESTIMADO\n{Xk}\n")

        Pk = calculate_new_process_covariance_matrix(Pkp, K)
        print(f"NUEVA MATRIZ DE COVARIANZA DE PROCESO ESTIMADA\n{Pk}\n")

        #print(f"DELTA DE ESTIMACION VS MEDICION\n{Yk-Xk}")
        print(f"DELTA ESTIMADO VS PREDECIDO (deseado en el DELTA_T)\n{Xk-Xkp}\n")

        print(f"########################################################################\n\n")

        Xkm1 = Xk
        Pkm1 = Pk




if __name__ == "__main__":
    main()