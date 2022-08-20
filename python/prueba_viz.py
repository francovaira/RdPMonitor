from multiprocessing import Process, Lock, Queue
import threading
from threading import Thread, Lock
import random
import time
import numpy
from Visualizer import Visualizer

queue = Queue(100)
viz = Visualizer(800, 800, 20, 20, queue)

def thread_run(id, queue):
    while(1):
        value = random.randint(0,1)
        valueX = random.randint(1, 10-2)
        valueY = random.randint(1, 10-2)

        print(f"{time.time()} [{id}] ### Intentando modificar ...")
        if(not queue.full()):
            queue.put([valueX, valueY, value], True)
            #queue.put(["holis", value, id])

        #print(f"{time.time()} [{id}] ### FIN DE MODIFICAR")


if __name__ == "__main__":

    threads = []
    thread_A = Thread(target=thread_run, args=('THR_A', queue))
    thread_B = Thread(target=thread_run, args=('THR_B', queue))
    thread_C = Thread(target=thread_run, args=('THR_C', queue))
    threads.append(thread_A)
    threads.append(thread_B)
    threads.append(thread_C)
    thread_A.start()
    thread_B.start()
    thread_C.start()

    processVisualizer = Process(target=viz.run())
    processVisualizer.start()
    processVisualizer.join()
    thread_A.join()
    thread_B.join()
    thread_C.join()


