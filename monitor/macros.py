# CONFIGURACION RED DE PETRI - MAPA
HILOS = 1

# MAPA
MAP_BORDER      = -1
MAP_OBSTACLE    = 1
MAP_OCCUPABLE   = 0
# MARCADO         = [ 0,2,  0,2,  0,2,  0,2,  0,2,
#                     0,2,  0,2,  0,2,  0,2,  0,2,
#                     0,2,  0,2,  0,0,  0,2,  0,2,
#                     0,2,  0,2,  0,0,  0,2,  0,2,
#                     0,2,  0,2,  0,2,  0,2,  0,2 ]

PATH_FINDER_MAX_ITERATIONS      = 1000
NULL_TRANSITION                 = -1

WAIT_ROBOT_FEEDBACK             = 300 # tiempo que el MQTT espera el mensaje de feedback del robot antes de arrojar timeout

KALMAN_ESTIMATED_STATE_PERIOD   = 10

ORIENTATION_0_DEGREE            = 0
ORIENTATION_90_DEGREE           = 1
ORIENTATION_180_DEGREE          = 2
ORIENTATION_270_DEGREE          = 3

# DEFAULT_CELL_SIZE                       = 1.0                   # expresado en metros - es cuanto mide el lado de una celda fisica real
DEFAULT_CELL_SIZE                       = 0.5                   # expresado en metros - es cuanto mide el lado de una celda fisica real
DEFAULT_ROBOT_MOVE_DISTANCE             = DEFAULT_CELL_SIZE     # expresado en metros
DEFAULT_ROBOT_ROTATE_180_DEG_DISTANCE   = 0.775                 # expresado en metros - distancia para dar una vuelta de 180 grados
DEFAULT_ROBOT_LINEAR_VELOCITY           = 0.35                  # expresado en metros/seg
DEFAULT_ROBOT_ANGULAR_VELOCITY          = 15.0                  # expresado en RPM

DEFAULT_CELL_ARRIVE_RADIUS      = 0.08  # expresado en metros. Radio minimo en cual debe estar el robot para considerar que llego a la coordenada esperada