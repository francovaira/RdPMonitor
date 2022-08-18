from multiprocessing import Process
import threading
from threading import Thread, Lock
import random
import time
import numpy
from Visualizer import Visualizer

#viz = Visualizer(800, 800, 20, 20)

def thread_run(visualizer, id, conditions):
    while(1):
        with conditions[0]:
            print(f"{time.time()} [{id}] ### Intentando modificar ...")
            # intenta modificar el estado de la grid
            #while(visualizer.updateCell(5, 5, True) != 0):
            #    conditions[0].wait() # espera que otro hilo lo despierte
            value = random.randint(0,1)
            visualizer.updateCell(5, 5, value)
            conditions[0].wait()
            print("HERE")
            time.sleep(0.5)
            self.conditions[transition].notify_all()

            while(visualizer.updateCell(5, 5, False) != 0):
                conditions[0].wait() # espera que otro hilo lo despierte

            time.sleep(0.5)
            self.conditions[transition].notify_all()

            # notify for other conditions and potential waiting threads # VALIDO SOLO SI HAY MAS DE UNA CONDICION
            #for i in range(0, transitionCount):
            #    with self.conditions[i]:
            #        self.conditions[i].notify_all()


def main():

    #global viz
    viz = Visualizer(800, 800, 20, 20)
    #Process(target=viz.run).start()
    #viz.run()

    # initialize conditions for transitions and their threads
    #conditions = []
    #cond = threading.Condition() # reference to the main lock
    #conditions.append(cond)

    #threads = []
    #thread_A = Thread(target=thread_run, args=(viz, 'THR_A', conditions))
    #thread_B = Thread(target=thread_run, args=(viz, 'THR_B', conditions))
    #threads.append(thread_A)
    #threads.append(thread_B)
    #time.sleep(0.5)
    #thread_A.start()
    #thread_B.start()

    while(1):
        value = random.randint(0,1)
        valueX = random.randint(1, 10-2)
        valueY = random.randint(1, 10-2)
        viz.updateCell(valueX, valueY, value)
        #time.sleep(0.5)
        viz.run()




if __name__ == "__main__":
    main()
    #viz = Visualizer(800, 800, 20, 20)

    #Process(target=main).start()
    #Process(target=viz.run()).start()
