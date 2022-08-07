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
        #matriz_estado_aux[i] = matriz_estado[i] + macros.INCIDENCIA[i][transicion]
        #if(matriz_estado_aux[i] == -1):
        if(matriz_estado[i] + macros.INCIDENCIA[i][transicion] == -1):
            return 0
    return 1

def red_disparar(transicion):
    global matriz_estado
    global matriz_estado_aux

    if(solicitud_disparo(transicion)):
        for i in range(0, macros.PLAZAS):
            #matriz_estado[i] = matriz_estado_aux[i]
            matriz_estado[i] = matriz_estado[i] + macros.INCIDENCIA[i][transicion]
        return 1
    return 0


def print_marcado():
    global matriz_estado

    print("-------------------  MARCADO  -------------------");
    str = []
    for i in range(0, macros.PLAZAS):
        str.append(matriz_estado[i])
    print(str)
    print()


def monitor_disparar(transicion):
    global monitor_lock
    global conditions

    monitor_lock.acquire();
    
    with conditions[transicion]:
        k = solicitud_disparo(transicion)
        while(k == 0):
            print(f"No sensibilizada: {transicion} -- esperando...")
            conditions[transicion].wait() # espera que otro hilo lo despierte
            k = solicitud_disparo(transicion)

        # disparar efectivamente - obtener el nuevo marcado
        incrementar_cant_disparos()
        print(f"Si sensibilizada, disparo: {transicion} #### CANT DISPAROS {cant_disparos}")
        red_disparar(transicion)

        # print marcado
        # print occupancy
        print_marcado()

        #for i in range(0, macros.TRANSICIONES):
            #conditions[i].notify()

        conditions[transicion].notify() # capaz se podria hacer un for que tenga internamente el wait y se iteran las condiciones
        #conditions[transicion].notify_all()

        #conditions[transicion].release()

    monitor_lock.release()


def thread_run(secuencia, id):
    while(1):
        for transicion in secuencia:
            if(transicion != macros.NULL_TRANSITION):
                print(f"HILO {id} ##### Intentando disparar transicion {transicion}")
                # intentar disparar el monitor
                monitor_disparar(transicion)


def main():
    # aca deberia inicializar el procesador de petri

    # aca deberia inicializar el lock del monitor
    #monitor_lock = threading.Lock()

    # aca deberia inicializar las variables de condicion de los thread  - cada transicion tiene una condicion con la que despierta al hilo que queria dispararla
    #condition = threading.Condition()
    #conditions = []
    for i in range(0, macros.TRANSICIONES):
        cond = threading.Condition()
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
    # create and start 10 threads and start them
    #threads = []
    #for n in range(1, 8):
    #    thr = Thread(target=thread_run, args=('id', n))
    #    threads.append(thr)
    #    thr.start()
    global threads

    thread_PROD = Thread(target=thread_run, args=(seqPROD, 'PROD'))
    thread_CONS = Thread(target=thread_run, args=(seqCONS, 'CONS'))
    threads.append(thread_PROD)
    threads.append(thread_CONS)
    thread_PROD.start()
    thread_CONS.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()







if __name__ == "__main__":
    main()
    #start_time = perf_counter()
    #end_time = perf_counter()
    #print(f'It took {end_time- start_time :0.2f} second(s) to complete.')
