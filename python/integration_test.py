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
        coordenadasPathFinder = pathFinder.calculatePath(1,1,5,5) # FIXME deberia tener un lock para acceder uno por vez
        if(coordenadasPathFinder == None):
            print("PATH FINDER ERROR - No path found for given coordinates")
            coordenadasSequence = [(1,1)]
        else:
            coordenadasSequence = coordenadasPathFinder
            secondPart = pathFinder.calculatePath(5,5,1,1)
            secondPart.pop(0)
            coordenadasSequence.extend(secondPart)
    elif(robotID == "ROB_B"):
        #coordenadasSequence = [(1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (5,1), (4,1), (3,1), (2,1), (1,1)]
        coordenadasPathFinder = pathFinder.calculatePath(1,5,5,1) # FIXME deberia tener un lock para acceder uno por vez
        if(coordenadasPathFinder == None):
            print("PATH FINDER ERROR - No path found for given coordinates")
            coordenadasSequence = [(1,1)]
        else:
            coordenadasSequence = coordenadasPathFinder
            secondPart = pathFinder.calculatePath(5,1,1,5)
            secondPart.pop(0)
            coordenadasSequence.extend(secondPart)

    transSeq = monitor.getTransitionSequence(coordenadasSequence)
    monitor.setRobotInCoordinate(coordenadasSequence[0], robotID)

    print(f"COORDENADAS {robotID} {coordenadasSequence}")
    print(f"TRANSICIONES {robotID} {transSeq}")

    while(1):
        # FIXME poner una cola para recibir trabajos y que otro hilo se los mande (simulando el hilo de comm)
        for transicion in transSeq:
            if(transicion != int(config('NULL_TRANSITION'))):
                #print(f"{time.time()} [{robotID}] ### Intentando disparar transicion {transicion}")
                monitor.monitorDisparar(transicion, robotID)
                time.sleep(0.1)
                #time.sleep(1)
                #time.sleep(random.random()*1)

def main():

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