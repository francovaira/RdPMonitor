from multiprocessing import Process, Lock, Queue
import threading
from threading import Thread, Lock
import random
import time
import numpy
from Visualizer import Visualizer

queue = Queue()
viz = Visualizer(800, 800, 20, 20, queue)

# def thread_run(visualizer, id, conditions):
#     while(1):
#         with conditions[0]:
#             print(f"{time.time()} [{id}] ### Intentando modificar ...")
#             # intenta modificar el estado de la grid
#             #while(visualizer.updateCell(5, 5, True) != 0):
#             #    conditions[0].wait() # espera que otro hilo lo despierte
#             value = random.randint(0,1)
#             visualizer.updateCell(5, 5, value)
#             conditions[0].wait()
#             print("HERE")
#             time.sleep(0.5)
#             self.conditions[transition].notify_all()

#             while(visualizer.updateCell(5, 5, False) != 0):
#                 conditions[0].wait() # espera que otro hilo lo despierte

#             time.sleep(0.5)
#             self.conditions[transition].notify_all()

#             # notify for other conditions and potential waiting threads # VALIDO SOLO SI HAY MAS DE UNA CONDICION
#             #for i in range(0, transitionCount):
#             #    with self.conditions[i]:
#             #        self.conditions[i].notify_all()


def thread_run(id, queue):
    while(1):
        #print(f"{time.time()} [{id}] ### Intentando modificar ...")
        # intenta modificar el estado de la grid
        value = random.randint(0,1)
        valueX = random.randint(1, 10-2)
        valueY = random.randint(1, 10-2)
        
        #while(visualizer.updateCell(5, 5, value)!=0):
        print(f"{time.time()} [{id}] ### Intentando modificar ...")
        #    pass
        #queue.put(["holis", value, id])
        if(not queue.full()):
            queue.put([valueX, valueY, value], True)


        #print(f"{time.time()} [{id}] ### FIN DE MODIFICAR")


if __name__ == "__main__":
    #main()
    #viz = Visualizer(800, 800, 20, 20)

    print("END")
    #processMain = Process(target=main())


    #lock = threading.Lock()
    threads = []
    thread_A = Thread(target=thread_run, args=('THR_A', queue))
    thread_B = Thread(target=thread_run, args=('THR_B', queue))
    thread_C = Thread(target=thread_run, args=('THR_C', queue))
    #thread_B = Thread(target=thread_run, args=(viz, 'THR_B', conditions))
    threads.append(thread_A)
    threads.append(thread_B)
    threads.append(thread_C)
    #time.sleep(0.5)
    thread_A.start()
    thread_B.start()
    thread_C.start()

    #time.sleep(2)
    processVisualizer = Process(target=viz.run())
    #processMain.start()
    processVisualizer.start()
    #processMain.join()
    processVisualizer.join()
    thread_A.join()
    thread_B.join()
    thread_C.join()
    print("END")
    #Process(target=main).start()

    #Process(target=viz.run()).start()
