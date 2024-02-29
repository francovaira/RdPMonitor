from statemachine import StateMachine, State
import time

class RobotMachine(StateMachine):
    disparo_monitor = State(initial=True)
    send_setpoint_robot = State()
    espera_respuesta = State()
    finish_state = State()

    dispararMonitor = (
        disparo_monitor.to(send_setpoint_robot, cond="run_monitor")
        | disparo_monitor.to(disparo_monitor, unless="run_monitor")
        | send_setpoint_robot.to(espera_respuesta, cond="send_setpoint")
        | send_setpoint_robot.to(finish_state, unless="send_setpoint")
        | espera_respuesta.to(disparo_monitor, cond="wait_response")
        | espera_respuesta.to(finish_state, unless="wait_response")
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
        print(f'[STATE MACHINE] returned from RUN: {status}')
        if (status == "WORKING") or (status == "END"):
            return True
        elif status == "NO_JOBS":
            return False

    def send_setpoint(self):
        try:
            self.__velocities = self.__robot.traslatePath(self.__executor.getPathTuple())
            msg = self.__mqttClient.publish(self.__robot.getRobotTopic(), self.__velocities, qos=0)
            msg.wait_for_publish()
            return True
        except:
            print("[STATE MACHINE] No jobs available")
            return False

    def wait_response(self):
        try:
            robotMsg = self.__msgQueue.get(timeout=15)
            return True
        except:
            return False

    def on_exit_finish_state(self):
        print(f"@{self.__robotID} cycle completed")

