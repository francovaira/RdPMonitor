from statemachine import StateMachine, State
import time
# from .RobotThreadExecutor import RobotThreadExecutor

class RobotMachine(StateMachine):
    green = State(initial=True)
    yellow = State()
    red = State()
    blue = State()

    dispararMonitor = (
        green.to(yellow, cond="run_monitor")
        | green.to(green, unless="run_monitor")
        | yellow.to(red, cond="mandar_mensaje")
        | yellow.to(blue, unless="mandar_mensaje")
        | red.to(green, cond="recibir_mensaje")
        | red.to(blue, unless="recibir_mensaje")
        | blue.to(green)
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

    def on_exit_blue(self):
        print(f"@{self.__robotID} cycle completed")