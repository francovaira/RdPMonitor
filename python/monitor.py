import threading
from threading import Thread, Lock
import time
import numpy
import macros
from RdP import RdP
from Monitor import Monitor

def thread_run(monitor, secuencia, id):
    while(1):
        for transicion in secuencia:
            if(transicion != macros.NULL_TRANSITION):
                print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                # intenta disparar el monitor
                monitor.monitor_disparar(transicion, id)


def main():

    rdp = RdP(macros.PLAZAS, macros.TRANSICIONES, macros.MARCADO, macros.INCIDENCIA)
    monitor = Monitor(threading.Lock(), rdp)

    # aca deberia inicializar el objeto con la secuencia de transiciones y demases
    seqPROD = [0, 3, 4] # T invariante del productor
    seqCONS = [1, 2, 5] # T invariante del consumidor

    # aca deberia crear los hilos y largarlos a correr
    threads = []
    thread_PROD = Thread(target=thread_run, args=(monitor, seqPROD, 'PROD'))
    thread_CONS = Thread(target=thread_run, args=(monitor, seqCONS, 'CONS'))
    threads.append(thread_PROD)
    threads.append(thread_CONS)
    thread_PROD.start()
    thread_CONS.start()

    # wait for the threads to complete
    #for thread in threads:
    #    thread.join()

    #self.pause()


if __name__ == "__main__":
    main()
