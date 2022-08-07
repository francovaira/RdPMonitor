import threading
import time
import numpy
from threading import Thread, Lock
from time import perf_counter
import macros

monitor_lock = threading.Lock()
matriz_estado = []
matriz_estado_aux = []
conditions = []
threads = []
cant_disparos = 0

def incrementar_cant_disparos():
    global cant_disparos
    cant_disparos = cant_disparos+1

def solicitud_disparo(transicion):
    global matriz_estado
    global matriz_estado_aux

    for i in range(0, macros.PLAZAS):
        matriz_estado_aux[i] = matriz_estado[i] + macros.INCIDENCIA[i][transicion]
        if(matriz_estado_aux[i] == -1):
            return 0
    return 1

def red_disparar(transicion):
    global matriz_estado
    global matriz_estado_aux

    if(solicitud_disparo(transicion)):
        for i in range(0, macros.PLAZAS):
            matriz_estado[i] = matriz_estado_aux[i]
        return 1
    return 0


def print_marcado():
    global matriz_estado

    print("-------------------  MARCADO  -------------------");
    str = []
    str.append(time.time())
    for i in range(0, macros.PLAZAS):
        str.append(matriz_estado[i])
    print(str)
    print()


def monitor_disparar(transicion, id):
    global conditions

    with conditions[transicion]:
        k = solicitud_disparo(transicion)
        while(k == 0):
            print(f"{time.time()} [{id}] ### No sensibilizada {transicion} -- esperando...")
            conditions[transicion].wait() # espera que otro hilo lo despierte
            k = solicitud_disparo(transicion)

        # disparar efectivamente - obtener el nuevo marcado
        incrementar_cant_disparos()
        print(f"{time.time()} [{id}] ### Si sensibilizada, disparo: {transicion} __ CANT DISPAROS {cant_disparos}")
        red_disparar(transicion)
        print_marcado()
        conditions[transicion].notify_all()

    # notify for other conditions and potential waiting threads
    for i in range(0, macros.TRANSICIONES):
        with conditions[i]:
            conditions[i].notify_all()


def thread_run(secuencia, id):
    while(1):
        for transicion in secuencia:
            if(transicion != macros.NULL_TRANSITION):
                print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                # intentar disparar el monitor
                monitor_disparar(transicion, id)


def main():
    # aca deberia inicializar el procesador de petri

    # aca deberia inicializar el lock del monitor
    #monitor_lock = threading.Lock()

    # aca deberia inicializar las variables de condicion de los thread  - cada transicion tiene una condicion con la que despierta al hilo que queria dispararla
    global monitor_lock
    global conditions
    for i in range(0, macros.TRANSICIONES):
        cond = threading.Condition(monitor_lock) # reference to the main lock
        conditions.append(cond)

    # aca deberia inicializar las matrices de estado
    #matriz_estado = []
    #matriz_estado_aux = []
    global matriz_estado
    global matriz_estado_aux

    for i in range(0, macros.PLAZAS):
        matriz_estado.append(macros.MARCADO[i])
        matriz_estado_aux.append(0)

    # aca deberia inicializar el objeto con la secuencia de transiciones y demases
    seqPROD = [0, 3, 4] # T invariante del productor
    seqCONS = [1, 2, 5] # T invariante del consumidor

    # aca deberia crear los hilos y largarlos a correr
    global threads
    thread_PROD = Thread(target=thread_run, args=(seqPROD, 'PROD'))
    thread_CONS = Thread(target=thread_run, args=(seqCONS, 'CONS'))
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
