# CONFIGURACION RED DE PETRI - MAPA
HILOS = 1

# MAPA
MAP_BORDER      = -1
MAP_OBSTACLE    = 1
MAP_OCCUPABLE   = 0
MARCADO         = [ 0,2,  0,2,  0,2,  0,2,  0,2,
                    0,2,  0,2,  0,2,  0,2,  0,2,
                    0,2,  0,2,  0,0,  0,2,  0,2,
                    0,2,  0,2,  0,0,  0,2,  0,2,
                    0,2,  0,2,  0,2,  0,2,  0,2 ]

PATH_FINDER_MAX_ITERATIONS  = 1000
NULL_TRANSITION             = -1

WAIT_ROBOT_FEEDBACK         = 300 # tiempo que el MQTT espera el mensaje de feedback del robot antes de arrojar timeout
