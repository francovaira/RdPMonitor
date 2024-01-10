from statemachine import StateMachine, State
from .RobotThreadExecutor import RobotThreadExecutor

class RobotMachine(StateMachine):
    green = State(initial=True)
    yellow = State()
    # red = State()
    # dispararMonitor = green.to(yellow, cond="dispararMonitor")

    dispararMonitor = (
        green.to(yellow, cond="run_monitor")
        | green.to(green, unless="run_monitor")
    )

    # cycle = (
    #     green.to(yellow)
    #     | yellow.to(red)
    #     | red.to(green)
    # )

    # def before_cycle(self, event: str, source: State, target: State, message: str = ""):
    #     message = ". " + message if message else ""
    #     return f"Running {event} from {source.id} to {target.id}{message}"
    def __init__(self, executor):
        self.__executor = executor

    def run_monitor(self):
        return self.__executor.run()
                # running = self.robotThreadExecutor.run()
        # return sum(self.payments) + amount >= self.order_total

    def blocked_thread(self):
        print("BLOCKED!")

    def on_enter_red(self):
        print("Don't move.")

    def on_exit_red(self):
        print("Go ahead!")