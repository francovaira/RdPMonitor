from statemachine import StateMachine, State
import time
# from .RobotThreadExecutor import RobotThreadExecutor

class RobotMachine(StateMachine):
    green = State(initial=True)
    yellow = State()
    red = State()
    # blue = State()
    # black = State()
    # dispararMonitor = green.to(yellow, cond="dispararMonitor")

    dispararMonitor = (
        green.to(yellow, cond="run_monitor")
        | green.to(green, unless="run_monitor")
    )

    mandarMensaje = (yellow.to(red))

    recibirMensaje = (red.to(green))

    def __init__(self, executor, robot):
        self.__executor = executor
        self.__robot = robot
        self.__robotID = robot.getRobotID()
        self.__mqttClient = robot.getMqttClient()
        self.__msgQueue = robot.getMsgQueue()
        self.__velocities = None
        super(RobotMachine, self).__init__()

    def run_monitor(self):
        return self.__executor.run()

    def on_enter_yellow(self):
        self.__velocities = self.__robot.traslatePath(self.__executor.getPathTuple())
        msg = self.__mqttClient.publish(self.__robot.getRobotTopic(), self.__velocities, qos=0)
        msg.wait_for_publish()
        print("FREE RED!")

    def on_enter_red(self):
        robotMsg = self.__msgQueue.get()
        print("FREE YELLOW!")