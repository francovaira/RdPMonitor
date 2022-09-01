from multiprocessing import Process, Lock, Pipe
import threading
from threading import Thread, Lock
import time
import numpy
#import random
import macros
from RdP import RdP
from Monitor import Monitor
from Visualizer import Visualizer


def thread_run(monitor, secuencia, id):
    while(1):
        for transicion in secuencia:
            if(transicion != macros.NULL_TRANSITION):
                print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                # intenta disparar el monitor
                monitor.monitor_disparar(transicion, id)
                time.sleep(0.1)

def main():

    pipeRdPReceiver, pipeRdPTransmitter = Pipe()

    rdp = RdP(macros.PLAZAS, macros.TRANSICIONES, macros.MARCADO, macros.INCIDENCIA, pipeRdPTransmitter)
    monitor = Monitor(threading.Lock(), rdp)
    viz = Visualizer(800, 800, 25, 25, pipeRdPReceiver)

    # luego esta secuencia provendria desde el path finder, mediando una interfaz para traducir a transiciones
    seqROBOT = [2, 12, 20, 22, 19, 9, 5, 1] # Se ponen los numeros de transicion (arranca a contar desde cero) -- SECUENCIA RONDA

    # create threads for each robot
    threads = []
    thread_ROBOT = Thread(target=thread_run, args=(monitor, seqROBOT, 'ROBOT'))
    threads.append(thread_ROBOT)
    thread_ROBOT.start()

    processVisualizer = Process(target=viz.run()) # FIXME aca para optimizar podria llamarse directamente a un init o algo asi y que de ese directamente pase al run() asi capaz seria mejor
    processVisualizer.start()
    processVisualizer.join()

    # wait for the threads to complete
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
