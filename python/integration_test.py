import multiprocessing
from multiprocessing import Process
import threading
from threading import Thread
import time
import numpy
import random
from decouple import config
import macros_mapa
from RdP import RdP
from Monitor import Monitor
from Visualizer import Visualizer
from Map import Map


def thread_run(monitor, robotID, pathFinder):

    # FIXME hacer que el robot tenga una "posicion/coordenada actual"

    coordenadasPathFinder = []
    if(robotID == "ROB_A"):
        coordenadasPathFinder = pathFinder.calculatePath(1,1,6,6) # FIXME deberia tener un lock para acceder uno por vez
        if(coordenadasPathFinder == None):
            print("PATH FINDER ERROR - No path found for given coordinates")
            #plazasSeq = [0]
            coordenadasSequence = [(1,1)]
        else:
            #placeSequence = monitor.getPlacesSequence(coordenadasPathFinder)
            #plazasSeq = placeSequence
            coordenadasSequence = coordenadasPathFinder
            coordenadasSequence.extend(pathFinder.calculatePath(6,6,1,6))
            coordenadasSequence.extend(pathFinder.calculatePath(1,6,1,1))
            #transSeq = monitor.getTransitionSequence(coordenadasSequence)

        #plazasSeq = [0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0]
        #plazasSeq = [16, 30, 44, 58, 72, 70, 56, 42, 28, 14, 16]
        #plazasSeq = [0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82, 80, 78, 76, 74, 72, 70, 56, 42, 28, 14, 0]
    elif(robotID == "ROB_B"):
        #plazasSeq = [82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82]
        #plazasSeq = [82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82]
        coordenadasSequence = [(1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (5,1), (4,1), (3,1), (2,1), (1,1)]
        #transSeq = monitor.getTransitionSequence(coordenadasSequence)

    transSeq = monitor.getTransitionSequence(coordenadasSequence)

    print(f"COORDENADAS {robotID} {coordenadasSequence}")
    print(f"TRANSICIONES {robotID} {transSeq}")

    #transSeq = monitor.getTransitionSequence(plazasSeq)
    #transSeq = monitor.getTransitionSequence(plazasSeq)
    #monitor.setRobotInPlace(plazasSeq[0], robotID)
    monitor.setRobotInCoordinate(coordenadasSequence[0], robotID)

    while(1):
        # FIXME poner una cola para recibir trabajos y que otro hilo se los mande (simulando el hilo de comm)
        for transicion in transSeq:
            if(transicion != int(config('NULL_TRANSITION'))):
                #print(f"{time.time()} [{robotID}] ### Intentando disparar transicion {transicion}")
                monitor.monitorDisparar(transicion, robotID)
                time.sleep(0.1)
                #time.sleep(2)
                #time.sleep(random.random()*1)

def main():

    #mapHorizontalSize = len(macros_mapa.MAPA[0])
    #mapVerticalSize = len(macros_mapa.MAPA)

    map = Map() # FIXME aca deberia buscar el archivo de definicion del mapa y crear la estructura del mapa
    mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
    mapVerticalSize = map.getMapDefinition().getVerticalSize()

    rdp = RdP(map) # FIXME aca hacer que detecte que si la matriz de incidencia y/o marcado son None que vaya a crear la red con la info del mapa
    monitor = Monitor(rdp)
    viz = Visualizer(800, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

    # create threads for each robot
    threads = []
    thread_ROBOT_A = Thread(target=thread_run, args=(monitor, 'ROB_A', map.getPathFinder()))
    thread_ROBOT_B = Thread(target=thread_run, args=(monitor, 'ROB_B', map.getPathFinder()))
    threads.append(thread_ROBOT_A)
    threads.append(thread_ROBOT_B)
    thread_ROBOT_A.start()
    thread_ROBOT_B.start()

    processVisualizer = multiprocessing.Process(target=viz.run())
    processVisualizer.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()
    processVisualizer.join()


if __name__ == "__main__":
    main()
