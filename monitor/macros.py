# CONFIGURACION RED DE PETRI - MAPA
HILOS = 1

# MAPA
CELL_WIDTH      = 0.5 # ancho de una celda del mapa fisico real - expresado en metros
CELL_HEIGHT     = 0.5 # alto de una celda del mapa fisico real - expresado en metros

MAP_BORDER      = -1
MAP_OBSTACLE    = 1
MAP_OCCUPABLE   = 0
MARCADO         = [ 0,2,  0,2,  0,2,  0,2,  0,2,
                    0,2,  0,2,  0,2,  0,2,  0,2,
                    0,2,  0,2,  0,0,  0,2,  0,2,
                    0,2,  0,2,  0,0,  0,2,  0,2,
                    0,2,  0,2,  0,2,  0,2,  0,2 ]

PATH_FINDER_MAX_ITERATIONS = 1000
NULL_TRANSITION = -1