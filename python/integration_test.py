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
from Monitor import Monitor
from MonitorWithQueues import MonitorWithQueues
from Visualizer import Visualizer
from Map import Map


def thread_run(monitor, robotID, cliente, cliente_queue):

    if(robotID == "ROB_A"):
        coordenadasSequence = monitor.calculatePath(3,1,3,3)
        secondPart = monitor.calculatePath(3,3,3,1)
        secondPart.pop(0)
        coordenadasSequence.extend(secondPart)
    elif(robotID == "ROB_B"):
        #coordenadasSequence = [(1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (5,1), (4,1), (3,1), (2,1), (1,1)]
        coordenadasSequence = monitor.calculatePath(1,3,5,3)
        secondPart = monitor.calculatePath(5,3,1,3)
        secondPart.pop(0)
        coordenadasSequence.extend(secondPart)
    elif(robotID == "ROB_C"):
        coordenadasSequence = monitor.calculatePath(3,3,3,4)
        secondPart = monitor.calculatePath(3,4,3,3)
        #thirdPart = monitor.calculatePath(3,1,3,2)
        #fourthPart = monitor.calculatePath(3,2,3,1)
        secondPart.pop(0)
        #thirdPart.pop(0)
        #fourthPart.pop(0)
        coordenadasSequence.extend(secondPart)
        #coordenadasSequence.extend(thirdPart)
        #coordenadasSequence.extend(fourthPart)

    transSeq = monitor.getTransitionSequence(coordenadasSequence)
    monitor.setRobotInCoordinate(coordenadasSequence[0], robotID)

    print(f"COORDENADAS {robotID} {coordenadasSequence}")
    print(f"TRANSICIONES {robotID} {transSeq}")

    time.sleep(1.5) # esto es para que el hilo espere a que el visualizador inicie

    # while(1):
    #     # FIXME poner una cola para recibir trabajos y que otro hilo se los mande (simulando el hilo de comm)
    #     for transicion in transSeq:
    #         if(transicion != int(config('NULL_TRANSITION'))):
    #             # print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
    #             # intenta disparar el monitor
    #             #cliente_queue.acquire()
    #             monitor.monitorDisparar(transicion, robotID)
    #             # motor_direction = define_motor_direction(transSeq, transicion, plazasSeq)
    #             #msg = cliente.publish("/topic/qos0", "motor_direction", qos=2)
    #             #msg.wait_for_publish()
    #             # msg.is_published()
    #             #cliente_queue.wait()
    #             #cliente_queue.release()
    #             #time.sleep(random.random()/2)
    #             time.sleep(0.1)

    a = 0

    while(1):
        for transicion in transSeq:
            if(transicion != int(config('NULL_TRANSITION'))):
                # print(f"{time.time()} [{id}] ### Intentando disparar transicion {transicion}")
                monitor.monitorDisparar(transicion, robotID)
                time.sleep(0.2*(random.random()+1))

                if(robotID == "ROB_C"):
                    a = a + 1
                    if(a % 2 == 0):
                        time.sleep(2)

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
    mqttc, mqttc_queue =  mqtt.main()
    # monitor = Monitor(rdp, map.getPathFinder())
    monitor = MonitorWithQueues(rdp, map.getPathFinder())

    viz = Visualizer(800, 800, mapHorizontalSize, mapVerticalSize, map.getMapInSharedMemory())

    # create threads for each robot
    threads = []
    thread_ROBOT_A = Thread(target=thread_run, args=(monitor, 'ROB_A', mqttc, mqttc_queue))
    thread_ROBOT_B = Thread(target=thread_run, args=(monitor, 'ROB_B', mqttc, mqttc_queue))
    thread_ROBOT_C = Thread(target=thread_run, args=(monitor, 'ROB_C', mqttc, mqttc_queue))
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