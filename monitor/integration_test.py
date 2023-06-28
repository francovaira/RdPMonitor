import multiprocessing
from multiprocessing import Process
import threading
from threading import Thread
import queue
import time
import numpy
import random
from decouple import config
import mqqt_client as mqtt
import macros_mapa
from RdP import RdP
from MonitorWithQueuesAndPriorityQueue import MonitorWithQueuesAndPriorityQueue
from Visualizer import Visualizer
from RobotThreadExecutor import RobotThreadExecutor
from JobManager import Path
from JobManager import Job
from JobManager import JobManager
from Map import Map

# muy buena explicacion de GIL https://pythonspeed.com/articles/python-gil/
# about yield = time.sleep(0) https://stackoverflow.com/a/790246

# IMPORTANTEEEEEE       -- se puede hacer con la misma RDP la cuestion de definir ciertas celdas para que entre un solo robot no mas,
#                          agregando una plaza conectada a las transiciones de entrada de esas plazas
class Setup:

    def __init__(self):
        self.main()

    def thread_run(self, robotID, jobQueue, monitor):

        robotThreadExecutor = RobotThreadExecutor(robotID, monitor)

        time.sleep(1.5) # esto es para que el hilo espere a que el visualizador inicie

        while(1):
            print(f"{robotID} || me voy a bloquear")
            nextJob = jobQueue.get() # se bloquea hasta que se ponga un elemento

            if(not type(nextJob) == Job):
                continue

            robotThreadExecutor.addJob(nextJob)
            robotThreadExecutor.startPaths()

            running = True
            while(running):
                running = robotThreadExecutor.run()
                #time.sleep(0.5)
                time.sleep(random.random())

            print(f"THREAD {robotID} STALL")


    def define_motor_direction(transSeq, transicion, plazasSeq):
        transicion_len = len(transSeq)-1
        transicion_index = transSeq.index(transicion)
        plaza = plazasSeq[transicion_index]

        if transicion_index < transicion_len:
            plaza_next = plazasSeq[transicion_index+1]
        else:
            plaza_next = plazasSeq[0]

        plaza_position = plaza_next - plaza
        mapHorizontalSize = (len(macros_mapa.MAPA[0])-2)*2
        motor_direction = None
        
        # match plaza_position:
        #     case 2:
        #         motor_direction = '{"setpoint" : 0.5, "vel_x" : 0, "vel_y" :  -0.3, "vel_ang" : 0}\0'
        #     case -2:
        #         motor_direction = '{"setpoint" : 0.5, "vel_x" : 0, "vel_y" : 0.3, "vel_ang" : 0}\0'
        #     case int(mapHorizontalSize):
        #         motor_direction = '{"setpoint" : 0.5, "vel_x" : 0.3, "vel_y" : 0, "vel_ang" : 0}\0'
        #     case _:
        #         motor_direction = '{"setpoint" : 0.5, "vel_x" : -0.3, "vel_y" : 0, "vel_ang" : 0}\0'

        return motor_direction

    # este hilo simula como se irian generando los jobs y enviando a cada robot
    def threadSendJobs(self, jobManager):
        jobA = Job()
        # path = Path(3,1,3,2)
        # jobA.addPath(path)
        # path = Path(3,2,4,5)
        # jobA.addPath(path)
        # path = Path(4,5,5,2)
        # jobA.addPath(path)
        path = Path(1,1,5,5)
        jobA.addPath(path)
        path = Path(5,5,1,1)
        jobA.addPath(path)
        jobManager.sendJobToRobot('ROB_A', jobA)

        #time.sleep(5)

        jobB = Job()
        # path = Path(1,3,5,1)
        # jobB.addPath(path)
        # path = Path(5,1,2,5)
        # jobB.addPath(path)
        # path = Path(2,5,1,5)
        # jobB.addPath(path)
        path = Path(5,1,1,5)
        jobB.addPath(path)
        path = Path(1,5,5,1)
        jobB.addPath(path)
        jobManager.sendJobToRobot('ROB_B', jobB)

        #time.sleep(20)

        jobC = Job()
        # path = Path(1,2,5,2)
        # jobC.addPath(path)
        # path = Path(5,2,2,5)
        # jobC.addPath(path)
        # path = Path(2,5,3,1)
        # jobC.addPath(path)
        path = Path(3,1,5,5)
        jobC.addPath(path)
        path = Path(5,5,3,1)
        jobC.addPath(path)
        jobManager.sendJobToRobot('ROB_C', jobC)

    def main(self):

        map = Map()
        mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
        mapVerticalSize = map.getMapDefinition().getVerticalSize()

        rdp = RdP(map)
        #mqttc, mqttc_queue =  mqtt.main()
        monitor = MonitorWithQueuesAndPriorityQueue(rdp, map.getPathFinder())

        viz = Visualizer(800, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

        # create threads for each robot
        threads = []
        jobQueueRobA = queue.Queue()
        jobQueueRobB = queue.Queue()
        jobQueueRobC = queue.Queue()
        thread_ROBOT_A = Thread(target=self.thread_run, args=('ROB_A', jobQueueRobA, monitor))
        thread_ROBOT_B = Thread(target=self.thread_run, args=('ROB_B', jobQueueRobB, monitor))
        thread_ROBOT_C = Thread(target=self.thread_run, args=('ROB_C', jobQueueRobC, monitor))
        threads.append(thread_ROBOT_A)
        threads.append(thread_ROBOT_B)
        threads.append(thread_ROBOT_C)
        thread_ROBOT_A.start()
        thread_ROBOT_B.start()
        thread_ROBOT_C.start()

        jobManager = JobManager()
        jobManager.addRobotJobQueue('ROB_A', jobQueueRobA)
        jobManager.addRobotJobQueue('ROB_B', jobQueueRobB)
        jobManager.addRobotJobQueue('ROB_C', jobQueueRobC)

        threadSendTrbjo = Thread(target=self.threadSendJobs, args=(jobManager,))
        threadSendTrbjo.start()


        # cualquier cosa que se ponga despues de esto no se va a ejecutar aunque los hilos terminen
        processVisualizer = multiprocessing.Process(target=viz.run())
        processVisualizer.start()

        # wait for the threads to complete
        for thread in threads:
            thread.join()
        threadSendTrbjo.join()
        processVisualizer.join()
