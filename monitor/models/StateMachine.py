from statemachine import StateMachine, State
import time
# from .RobotThreadExecutor import RobotThreadExecutor

class RobotMachine(StateMachine):
    disparo_monitor = State(initial=True)
    send_setpoint_robot = State()
    espera_respuesta = State()
    finish_state = State()

    dispararMonitor = (
        disparo_monitor.to(send_setpoint_robot, cond="run_monitor")
        | disparo_monitor.to(disparo_monitor, unless="run_monitor")
        | send_setpoint_robot.to(espera_respuesta, cond="mandar_mensaje")
        | send_setpoint_robot.to(finish_state, unless="mandar_mensaje")
        | espera_respuesta.to(disparo_monitor, cond="recibir_mensaje")
        | espera_respuesta.to(finish_state, unless="recibir_mensaje")
        | finish_state.to(disparo_monitor)
    )

    def __init__(self, executor, robot):
        self.__executor = executor
        self.__robot = robot
        self.__robotID = robot.getRobotID()
        self.__mqttClient = robot.getMqttClient()
        self.__msgQueue = robot.getMsgQueue()
        self.__velocities = None
        super(RobotMachine, self).__init__()

    def run_monitor(self):
        status = self.__executor.run()
        if (status == "WORKING") or (status == "END"):
            return True
        elif status == "NO_JOBS":
            return False

    def mandar_mensaje(self):
        try:
            self.__velocities = self.__robot.traslatePath(self.__executor.getPathTuple())
            msg = self.__mqttClient.publish(self.__robot.getRobotTopic(), self.__velocities, qos=0)
            msg.wait_for_publish()
            return True
        except:
            print("[STATE MACHINE] No jobs available")
            return False

    def recibir_mensaje(self):
        try:
            robotMsg = self.__msgQueue.get(timeout=15)
            return True
        except:
            return False

    def on_exit_finish_state(self):
        print(f"@{self.__robotID} cycle completed")