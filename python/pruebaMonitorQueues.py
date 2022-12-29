import multiprocessing
from multiprocessing import Process
import threading
from threading import Thread
import time
import numpy
import random
from decouple import config
import mqqt_client as mqtt
import macros_mapa
from RdP import RdP
from MonitorWithQueues import MonitorWithQueues
from Visualizer import Visualizer
from Map import Map


def thread_run(monitor, robotID):

    if(robotID == "ROB_A"):
        #coordenadasSequence = [(1, 1), (2, 1), (3, 1), (3, 2), (4, 2), (5, 2), (5, 3), (5, 4), (5, 5), (4, 5), (4, 4), (4, 3), (4, 2), (3, 2), (2, 2), (2, 1), (1, 1)]
        coordenadasSequence = [(1, 1), (2, 1), (2, 2), (2, 3), (1, 3), (1, 4), (1, 5), (1, 4), (1, 3), (2, 3), (2, 2), (2, 1), (1, 1)]
    elif(robotID == "ROB_B"):
        #coordenadasSequence = [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (5, 4), (5, 3), (5, 2), (5, 1), (5, 2), (4, 2), (3, 2), (2, 2), (2, 3), (1, 3), (1, 4), (1, 5)]
        coordenadasSequence = [(4, 2), (4, 3), (4, 4), (4, 5), (3, 5), (2, 5), (1, 5), (2, 5), (3, 5), (4, 5), (4, 4), (4, 3), (4, 2)]
    elif(robotID == "ROB_C"):
        #coordenadasSequence = [(3, 1), (3, 2), (4, 2), (5, 2), (5, 3), (5, 2), (4, 2), (3, 2), (3, 1)]
        coordenadasSequence = [(3, 1), (3, 2), (2, 2), (3, 2), (3, 1)]

    transSeq = monitor.getTransitionSequence(coordenadasSequence)
    monitor.setRobotInCoordinate(coordenadasSequence[0], robotID)

    print(f"COORDENADAS {robotID} {coordenadasSequence}")
    print(f"TRANSICIONES {robotID} {transSeq}")

    time.sleep(1.5) # esto es para que el hilo espere a que el visualizador inicie
    a = 0

    while(1):
        for transicion in transSeq:
            if(transicion != int(config('NULL_TRANSITION'))):
                # print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                monitor.monitorDisparar(transicion, robotID)
                time.sleep(0.2*(random.random()+1))

                if(robotID == "ROB_C"):
                    a = a + 1
                    if(a % 2 == 0):
                        time.sleep(4)


def main():

    map = Map()
    mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
    mapVerticalSize = map.getMapDefinition().getVerticalSize()

    rdp = RdP(map)
    monitor = MonitorWithQueues(rdp)
    viz = Visualizer(800, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

    # create threads for each robot
    threads = []
    thread_ROBOT_A = Thread(target=thread_run, args=(monitor, 'ROB_A'))
    thread_ROBOT_B = Thread(target=thread_run, args=(monitor, 'ROB_B'))
    thread_ROBOT_C = Thread(target=thread_run, args=(monitor, 'ROB_C'))
    threads.append(thread_ROBOT_A)
    threads.append(thread_ROBOT_B)
    threads.append(thread_ROBOT_C)
    thread_ROBOT_A.start()
    thread_ROBOT_B.start()
    thread_ROBOT_C.start()

    processVisualizer = multiprocessing.Process(target=viz.run())
    processVisualizer.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()
    processVisualizer.join()


if __name__ == "__main__":
    main()