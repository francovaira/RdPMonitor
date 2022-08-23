from multiprocessing import Process, Lock, Pipe
import threading
from threading import Thread, Lock
import time
import numpy
import random
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
                #time.sleep(random.random())
                time.sleep(0.5)

def main():

    pipeRdPReceiver, pipeRdPTransmitter = Pipe()

    rdp = RdP(macros.PLAZAS, macros.TRANSICIONES, macros.MARCADO, macros.INCIDENCIA, pipeRdPTransmitter)
    monitor = Monitor(threading.Lock(), rdp)
    viz = Visualizer(800, 800, 5, 5, pipeRdPReceiver)

    # aca deberia inicializar el objeto con la secuencia de transiciones y demases
    #seqPROD = [0, 3, 4] # T invariante del productor
    #seqCONS = [1, 2, 5] # T invariante del consumidor
    seqPROD = [2, 12, 20, 22, 19, 9, 5, 1] # Se ponen los numeros de transicion - 1 porque arranca a contar desde cero -- SECUENCIA RONDA

    # aca deberia crear los hilos y largarlos a correr
    threads = []
    thread_PROD = Thread(target=thread_run, args=(monitor, seqPROD, 'PROD'))
    #thread_CONS = Thread(target=thread_run, args=(monitor, seqCONS, 'CONS'))
    threads.append(thread_PROD)
    #threads.append(thread_CONS)
    thread_PROD.start()
    #thread_CONS.start()

    processVisualizer = Process(target=viz.run())
    processVisualizer.start()
    processVisualizer.join()

    # wait for the threads to complete
    for thread in threads:
        thread.join()

    #self.pause()


if __name__ == "__main__":
    main()
