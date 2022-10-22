import multiprocessing
from multiprocessing import Process
import threading
from threading import Thread
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
        coordenadasPathFinder = pathFinder.calculatePath(1,1,5,5) # FIXME deberia tener un lock para acceder uno por vez
        if(coordenadasPathFinder == None):
            print("PATH FINDER ERROR - No path found for given coordinates")
            coordenadasSequence = [(1,1)]
        else:
            coordenadasSequence = coordenadasPathFinder
            secondPart = pathFinder.calculatePath(5,5,1,1)
            secondPart.pop(0)
            coordenadasSequence.extend(secondPart)
    elif(robotID == "ROB_B"):
        #coordenadasSequence = [(1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (5,1), (4,1), (3,1), (2,1), (1,1)]
        coordenadasPathFinder = pathFinder.calculatePath(1,5,5,1) # FIXME deberia tener un lock para acceder uno por vez
        if(coordenadasPathFinder == None):
            print("PATH FINDER ERROR - No path found for given coordinates")
            coordenadasSequence = [(1,1)]
        else:
            coordenadasSequence = coordenadasPathFinder
            secondPart = pathFinder.calculatePath(5,1,1,5)
            secondPart.pop(0)
            coordenadasSequence.extend(secondPart)

    transSeq = monitor.getTransitionSequence(coordenadasSequence)
    monitor.setRobotInCoordinate(coordenadasSequence[0], robotID)

    print(f"COORDENADAS {robotID} {coordenadasSequence}")
    print(f"TRANSICIONES {robotID} {transSeq}")

    while(1):
        # FIXME poner una cola para recibir trabajos y que otro hilo se los mande (simulando el hilo de comm)
        for transicion in transSeq:
            if(transicion != int(config('NULL_TRANSITION'))):
                # print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                # intenta disparar el monitor
                cliente_queue.acquire()
                monitor.monitorDisparar(transicion, robotID)
                # motor_direction = define_motor_direction(transSeq, transicion, plazasSeq)
                msg = cliente.publish("/topic/qos0", "motor_direction", qos=2)
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
    map = Map()

    mapHorizontalSize = map.getMapDefinition().getHorizontalSize()
    mapVerticalSize = map.getMapDefinition().getVerticalSize()

    rdp = RdP(map)
    mqttc, mqttc_queue =  mqtt.main()
    monitor = Monitor(rdp)
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