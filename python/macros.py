# Macros para el monitor y la RdP

NULL_TRANSITION = -1


#CONFIGURACION RED DE PETRI
PLAZAS = 8
TRANSICIONES = 6
HILOS = 2

# PRODUCTOR CONSUMIDOR
#MARCADO = [1,0,0,1,0,0,0,3]
MARCADO = [1,0,0,1,0,0,3,0]

INCIDENCIA = [  [-1,0,0,0,1,0],
                [1,0,0,-1,0,0],
                [0,0,0,1,-1,0],
                [0,-1,0,0,0,1],
                [0,1,-1,0,0,0],
                [0,0,1,0,0,-1],
                [1,-1,0,0,0,0],
                [-1,1,0,0,0,0]
             ]

