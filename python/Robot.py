    # thread_ROBOT_A = Thread(target=thread_run, args=(monitor, 'ROB_A', map.getPathFinder(), mqttc, mqttc_robot_queue))
import MQTTClient as mqttc
import random as rd

class Robot:
    def __init__(self, robotID):
        self._robotID = robotID
        self._prioridad = None
        self._caminoRecorrido = None
        self._mqtt_client = mqttc.create_client(self._robotID)

    def getRobotID(self):
        return self._robotID

    def _generate_id(self):
        identificador = "identificador_" + str(rd.randint(1, 10))
        return identificador

    # def getPrioridad(self):

    # def setPrioridad(self):

    # def getCaminoRecorrido(self):

    # def setCaminoRecorrido(self):