import multiprocessing
from multiprocessing import Process, Lock, Pipe
import threading
from threading import Thread, Lock
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
        placeSequence = monitor.getPlacesSequence(coordenadasPathFinder)

        plazasSeq = [0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0]
        #plazasSeq = [16, 30, 44, 58, 72, 70, 56, 42, 28, 14, 16]
        #plazasSeq = [0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82, 80, 78, 76, 74, 72, 70, 56, 42, 28, 14, 0]
        #plazasSeq = placeSequence
    elif(robotID == "ROB_B"):
        #plazasSeq = [82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82]
        plazasSeq = [82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82]

    transSeq = monitor.getTransitionSequence(plazasSeq)
    monitor.setRobotInPlace(plazasSeq[0], robotID)
    print(f"TRANSICIONES {robotID} {transSeq}")

    while(1):
        for transicion in transSeq:
            if(transicion != int(config('NULL_TRANSITION'))):
                #print(f"{time.time()} [{robotID}] ### Intentando disparar transicion {transicion}")
                monitor.monitorDisparar(transicion, robotID)
                time.sleep(0.1)
                #time.sleep(random.random()*1)

def main():

    mapHorizontalSize = len(macros_mapa.MAPA[0])
    mapVerticalSize = len(macros_mapa.MAPA)

    map = Map(mapHorizontalSize, mapVerticalSize)
    rdp = RdP(map)
    monitor = Monitor(threading.Lock(), rdp)
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
