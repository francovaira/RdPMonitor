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

    recibirMensaje = (yellow.to(red))

    mandarMensaje = (red.to(green))
    # cycle = (
    #     green.to(yellow)
    #     | yellow.to(red)
    #     | red.to(green)
    # )

    # def before_cycle(self, event: str, source: State, target: State, message: str = ""):
    #     message = ". " + message if message else ""
    #     return f"Running {event} from {source.id} to {target.id}{message}"
    def __init__(self, executor, msgQueue):
        self.__executor = executor
        self.__msgQueue = msgQueue
        super(RobotMachine, self).__init__()

    def run_monitor(self):
        return self.__executor.run()
                # running = self.robotThreadExecutor.run()
        # return sum(self.payments) + amount >= self.order_total

    def blocked_thread(self):
        print("BLOCKED!")

    def on_enter_yellow(self):
        robotMsg = self.__msgQueue.get()
        print("FREE YELLOW!")

    def on_enter_red(self):
        print("FREE RED!")
    # def on_enter_yellow(self):
    #     print("BLOCKED YELLOW!")
    #     try:
    #         robotMsg = self.__msgQueue.get(timeout=10)
    #     except:
    #         print("FREE YELLOW!")
        # robotMsg = msgQueue.get()
        # # exit()

    # def on_exit_yellow(self):
    #     robotMsg = self.__msgQueue.get()
