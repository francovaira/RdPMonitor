from multiprocessing import Process, Lock, Pipe
import threading
from threading import Thread, Lock
import random
import time
import numpy
from Visualizer import Visualizer



def updateMap(valueX, valueY, show, pipeTransmitter):
    pipeTransmitter.send([valueX, valueY, show])

def thread_run(id, pipeTransmitter):
    while(1):
        value = random.randint(0,1)
        valueX = random.randint(1, 10-2)
        valueY = random.randint(1, 10-2)

        #print(f"{time.time()} [{id}] ### Intentando modificar ...")
        updateMap(valueX, valueY, value, pipeTransmitter)

        #print(f"{time.time()} [{id}] ### FIN DE MODIFICAR")

if __name__ == "__main__":

    # create the pipe
    pipeReceiver, pipeTransmitter = Pipe()

    viz = Visualizer(800, 800, 20, 20, pipeReceiver)

    threads = []
    thread_A = Thread(target=thread_run, args=('THR_A', pipeTransmitter))
    thread_B = Thread(target=thread_run, args=('THR_B', pipeTransmitter))
    thread_C = Thread(target=thread_run, args=('THR_C', pipeTransmitter))
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


