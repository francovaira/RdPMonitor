# Macros para el monitor y la RdP

NULL_TRANSITION = -1


#CONFIGURACION RED DE PETRI - PRODUCTOR CONSUMIDOR
#PLAZAS = 8
#TRANSICIONES = 6
#HILOS = 2

# PRODUCTOR CONSUMIDOR
#MARCADO = [1,0,0,1,0,0,0,3]

# PRODUCTOR CONSUMIDOR
# INCIDENCIA = [  [-1,0,0,0,1,0],
#                 [1,0,0,-1,0,0],
#                 [0,0,0,1,-1,0],
#                 [0,-1,0,0,0,1],
#                 [0,1,-1,0,0,0],
#                 [0,0,1,0,0,-1],
#                 [1,-1,0,0,0,0],
#                 [-1,1,0,0,0,0]
#              ]


#CONFIGURACION RED DE PETRI - MAPA
PLAZAS = 18
TRANSICIONES = 24
HILOS = 1

# MAPA
MARCADO = [1,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1]

# MAPA
INCIDENCIA = [  [-1,1,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,-1,1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,-1,0,0,-1,1,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [-1,1,0,0,1,-1,1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,1,-1,0,0,-1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,-1,1,0,0,1,-1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,1,-1,0,0,0,0,0,0,-1,1,-1,1,0,0,0,0,0,0,0,0,0,0],
                [0,0,-1,1,0,0,0,0,0,0,1,-1,1,-1,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,1,-1,0,0,1,-1,0,0,-1,1,-1,1,0,0,0,0,0,0],
                [0,0,0,0,0,0,-1,1,0,0,-1,1,0,0,1,-1,1,-1,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,1,-1,0,0,0,0,1,-1,0,0,-1,1,0,0,0,0],
                [0,0,0,0,0,0,0,0,-1,1,0,0,0,0,-1,1,0,0,1,-1,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,1,-1,0,0,0,0,0,0,-1,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,-1,1,0,0,0,0,0,0,1,-1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,-1,0,0,1,-1,-1,1],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,1,0,0,-1,1,1,-1],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,-1,0,0,1,-1],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,1,0,0,-1,1]
             ]


