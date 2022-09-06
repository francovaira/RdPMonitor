from multiprocessing import Process, Lock, Pipe
import threading
from threading import Thread, Lock
import time
import numpy
import macros
from RdP import RdP
from Monitor import Monitor
from Visualizer import Visualizer
from Map import Map


def thread_run(monitor, secuencia, id):
    while(1):
        for transicion in secuencia:
            if(transicion != macros.NULL_TRANSITION):
                #print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                # intenta disparar el monitor
                monitor.monitorDisparar(transicion, id)
                #time.sleep(0.1)

def main():

    mapHorizontalSize = 10
    mapVerticalSize = 10

    pipeRdPReceiver, pipeMap2VisualizerTX = Pipe() # FIXME OJO que el pipe puede ser cuello de botella, si se llena y eso se traba la red

    map = Map(mapHorizontalSize, mapVerticalSize, pipeMap2VisualizerTX)
    #rdp = RdP(macros.PLAZAS, macros.TRANSICIONES, macros.MARCADO, macros.INCIDENCIA, pipeRdPTransmitter)
    rdp = RdP(macros.PLAZAS, macros.TRANSICIONES, macros.MARCADO, macros.INCIDENCIA, map)
    monitor = Monitor(threading.Lock(), rdp)
    viz = Visualizer(800, 800, mapHorizontalSize, mapVerticalSize, pipeRdPReceiver)

    # luego esta secuencia provendria desde el path finder, mediando una interfaz para traducir a transiciones
    seqROBOT_A = [2, 12, 20, 22, 19, 9, 5, 1] # Se ponen los numeros de transicion (arranca a contar desde cero) -- SECUENCIA RONDA
    seqROBOT_B = [22, 19, 9, 5, 1, 2, 12, 20] # Se ponen los numeros de transicion (arranca a contar desde cero) -- SECUENCIA RONDA

    # create threads for each robot
    threads = []
    thread_ROBOT_A = Thread(target=thread_run, args=(monitor, seqROBOT_A, 'ROB_A'))
    thread_ROBOT_B = Thread(target=thread_run, args=(monitor, seqROBOT_B, 'ROB_B'))
    threads.append(thread_ROBOT_A)
    threads.append(thread_ROBOT_B)
    thread_ROBOT_A.start()
    thread_ROBOT_B.start()

    processVisualizer = Process(target=viz.run()) # FIXME aca para optimizar podria llamarse directamente a un init o algo asi y que de ese directamente pase al run() asi capaz seria mejor
    processVisualizer.start()
    processVisualizer.join()

    # wait for the threads to complete
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
