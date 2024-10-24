# CONFIGURACION RED DE PETRI - MAPA
HILOS = 1

# MAPA
MAP_BORDER      = -1
MAP_OBSTACLE    = 1
MAP_OCCUPABLE   = 0

PATH_FINDER_MAX_ITERATIONS      = 1000
NULL_TRANSITION                 = -1

WAIT_ROBOT_FEEDBACK                                 = 300 # tiempo que el MQTT espera el mensaje de feedback del robot antes de arrojar timeout
WAIT_TIME_BEFORE_SEND_NEXT_SETPOINT                 = 2.0 # tiempo de espera antes de que se envie el proximo setpoint hacia la siguiente coordenada - expresado en segundos

KALMAN_ESTIMATED_STATE_PERIOD                       = 100
KALMAN_CALCULATE_PROCESS_COVARIANCE_MATRIX_PERIOD   = 100

ORIENTATION_0_DEGREE            = 0
ORIENTATION_90_DEGREE           = 1
ORIENTATION_180_DEGREE          = 2
ORIENTATION_270_DEGREE          = 3

DEFAULT_CELL_SIZE                       = 0.45                  # expresado en metros - es cuanto mide el lado de una celda fisica real
DEFAULT_ROBOT_MOVE_DISTANCE             = DEFAULT_CELL_SIZE     # expresado en metros
# DEFAULT_ROBOT_ROTATE_180_DEG_DISTANCE   = 0.775                 # expresado en metros - distancia para dar una vuelta de 180 grados
DEFAULT_ROBOT_ROTATE_180_DEG_DISTANCE   = 0.95                   # expresado en metros - distancia para dar una vuelta de 180 grados
DEFAULT_ROBOT_LINEAR_VELOCITY           = 0.3                  # expresado en metros/seg
DEFAULT_ROBOT_ANGULAR_VELOCITY          = 18.0                  # expresado en RPM

# FIXME este valor en 0.1 es muy grande, deberia mejorarse
DEFAULT_CELL_ARRIVE_RADIUS              = 0.05                  # expresado en metros. Radio minimo en cual debe estar el robot para considerar que llego a la coordenada esperada