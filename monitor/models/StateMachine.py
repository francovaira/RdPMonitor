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
        super(RobotMachine, self).__init__()

    def run_monitor(self):
        # print(f"@{self.__robotID} || TRANSITION @{self.__executor.getPath()} - {type(self.__executor.getPath())}")
        self.__robot.traslatePath(self.__executor.getPathTuple())
        return self.__executor.run()

    def on_enter_yellow(self):
        topic = f'/topic/{self.__robotID}'
        msg = self.__mqttClient.publish(topic, '{"id":"searching"}', qos=2)
        msg.wait_for_publish()
        print("FREE RED!")

    def on_enter_red(self):
        robotMsg = self.__msgQueue.get()
        print("FREE YELLOW!")