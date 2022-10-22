import multiprocessing
from multiprocessing import Process, Lock, Pipe
import threading
from threading import Thread, Lock
import time
import numpy
import random
from decouple import config
import macros_mapa
from RdP import RdP
from Monitor import Monitor
from Visualizer import Visualizer
from Map import Map
import mqqt_client as mqtt
import ws_server as ws

def thread_run(monitor, robotID, pathFinder, cliente, cliente_queue):

    # FIXME hacer que el robot tenga una "posicion/coordenada actual"

    coordenadasPathFinder = []
    if(robotID == "ROB_A"):
        coordenadasPathFinder = pathFinder.calculatePath(1,1,6,6) # FIXME deberia tener un lock para acceder uno por vez
        placeSequence = monitor.getPlacesSequence(coordenadasPathFinder)

        plazasSeq = [0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0]
        # plazasSeq = None
        #plazasSeq = [0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82, 80, 78, 76, 74, 72, 70, 56, 42, 28, 14, 0]
        # plazasSeq = placeSequence
    elif(robotID == "ROB_B"):
        #plazasSeq = [82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82]
        plazasSeq = [82, 80, 78, 76, 62, 48, 34, 20, 6, 4, 2, 0, 2, 4, 6, 8, 10, 12, 26, 40, 54, 68, 82]

    transSeq = monitor.getTransitionSequence(plazasSeq)
    monitor.setRobotInPlace(plazasSeq[0], robotID)

    while(1):
        for transicion in transSeq:
            if(transicion != int(config('NULL_TRANSITION'))):
                # print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                # intenta disparar el monitor
                cliente_queue.acquire()
                monitor.monitorDisparar(transicion, robotID)
                motor_direction = define_motor_direction(transSeq, transicion, plazasSeq)
                msg = cliente.publish("/topic/qos0", motor_direction, qos=2)
                msg.wait_for_publish()
                # msg.is_published()
                cliente_queue.wait()
                cliente_queue.release()

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
    
    match plaza_position:
        case 2:
            motor_direction = '{"setpoint" : 0.5, "vel_x" : 0, "vel_y" :  -0.3, "vel_ang" : 0}\0'
        case -2:
            motor_direction = '{"setpoint" : 0.5, "vel_x" : 0, "vel_y" : 0.3, "vel_ang" : 0}\0'
        case int(mapHorizontalSize):
            motor_direction = '{"setpoint" : 0.5, "vel_x" : 0.3, "vel_y" : 0, "vel_ang" : 0}\0'
        case _:
            motor_direction = '{"setpoint" : 0.5, "vel_x" : -0.3, "vel_y" : 0, "vel_ang" : 0}\0'

    return motor_direction

def main():
    mapHorizontalSize = len(macros_mapa.MAPA[0])
    mapVerticalSize = len(macros_mapa.MAPA)

    map = Map(mapHorizontalSize, mapVerticalSize)
    rdp = RdP(map)
    mqttc, mqttc_queue =  mqtt.main()
    monitor = Monitor(threading.Lock(), rdp)
    viz = Visualizer(800, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

    # create threads for each robot
    threads = []
    thread_ROBOT_A = Thread(target=thread_run, args=(monitor, 'ROB_A', map.getPathFinder(), mqttc, mqttc_queue))
    # thread_ROBOT_B = Thread(target=thread_run, args=(monitor, 'ROB_B', map.getPathFinder(), mqttc, mqttc_queue))
    threads.append(thread_ROBOT_A)
    # threads.append(thread_ROBOT_B)
    thread_ROBOT_A.start()
    # thread_ROBOT_B.start()

    processVisualizer = multiprocessing.Process(target=viz.run())
    processVisualizer.start()

    # wait for the threads to complete
    for thread in threads:
        thread.join()
    processVisualizer.join()


if __name__ == "__main__":
    main()
