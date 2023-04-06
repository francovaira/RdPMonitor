import multiprocessing
from multiprocessing import Process
import threading
from threading import Thread
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
from RobotThreadExecutor import Path
from Map import Map

# muy buena explicacion de GIL https://pythonspeed.com/articles/python-gil/
# about yield = time.sleep(0) https://stackoverflow.com/a/790246


def thread_run(robotID, monitor):

    robotThreadExecutor = RobotThreadExecutor(robotID, monitor)

    if(robotID == "ROB_A"):
        path = Path(3,1,3,3)
        robotThreadExecutor.addPath(path)
        path = Path(3,3,5,5)
        robotThreadExecutor.addPath(path)
        path = Path(5,5,5,1)
        robotThreadExecutor.addPath(path)
        robotThreadExecutor.startPaths()
    if(robotID == "ROB_B"):
        path = Path(1,3,1,1)
        robotThreadExecutor.addPath(path)
        path = Path(1,1,2,5)
        robotThreadExecutor.addPath(path)
        path = Path(2,5,1,1)
        robotThreadExecutor.addPath(path)
        robotThreadExecutor.startPaths()
    if(robotID == "ROB_C"):
        path = Path(5,5,3,1)
        robotThreadExecutor.addPath(path)
        path = Path(3,1,3,5)
        robotThreadExecutor.addPath(path)
        path = Path(3,5,3,1)
        robotThreadExecutor.addPath(path)
        robotThreadExecutor.startPaths()

    time.sleep(1.5) # esto es para que el hilo espere a que el visualizador inicie

    running = True
    while(running):
        running = robotThreadExecutor.run()
        time.sleep(1)
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

def main():

    map = Map()
    mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
    mapVerticalSize = map.getMapDefinition().getVerticalSize()

    rdp = RdP(map)
    #mqttc, mqttc_queue =  mqtt.main()
    monitor = MonitorWithQueuesAndPriorityQueue(rdp, map.getPathFinder())

    viz = Visualizer(800, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

    # create threads for each robot
    threads = []
    thread_ROBOT_A = Thread(target=thread_run, args=('ROB_A', monitor))
    thread_ROBOT_B = Thread(target=thread_run, args=('ROB_B', monitor))
    thread_ROBOT_C = Thread(target=thread_run, args=('ROB_C', monitor))
    threads.append(thread_ROBOT_A)
    threads.append(thread_ROBOT_B)
    threads.append(thread_ROBOT_C)
    thread_ROBOT_A.start()
    thread_ROBOT_B.start()
    thread_ROBOT_C.start()

    processVisualizer = multiprocessing.Process(target=viz.run())
    processVisualizer.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()
    processVisualizer.join()


if __name__ == "__main__":
    main()