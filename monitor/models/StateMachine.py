from statemachine import StateMachine, State
import json
import logging
import macros

class RobotMachine(StateMachine):
    def __init__(self, executor, robot):
        self.__executor = executor
        self.__robot = robot
        self.__robotID = robot.getRobotID()
        self.__robotFeedbackQueue = robot.getFeedbackQueue()
        super(RobotMachine, self).__init__()

    disparo_monitor = State(initial=True)
    calculate_move_vector = State()
    send_setpoint_robot = State()
    espera_respuesta = State()
    compensacion_kalman = State()
    finish_state = State(final=True)

    dispararMonitor = (
        disparo_monitor.to(calculate_move_vector, cond="run_monitor")
        | disparo_monitor.to(finish_state, unless="run_monitor")
    )

    calculateMovementVector = (
        calculate_move_vector.to(send_setpoint_robot, cond="calculate_movement_vector")
        | calculate_move_vector.to(finish_state, unless="calculate_movement_vector")
    )

    sendSetpointToRobot = (
        send_setpoint_robot.to(espera_respuesta, cond="send_setpoint")
        | send_setpoint_robot.to(finish_state, unless="send_setpoint")
    )

    esperaRespuesta = (
        espera_respuesta.to(compensacion_kalman, cond="is_compensation_time")
        | espera_respuesta.to(disparo_monitor, cond="robot_has_arrived")
        | espera_respuesta.to(espera_respuesta, cond="wait_response")
        | espera_respuesta.to(disparo_monitor, unless="wait_response")
    )

    compensationCalculation = (
        compensacion_kalman.to(send_setpoint_robot, cond="calculo_compensacion")
    )

    def run(self):
        if (self.finish_state.is_active == True):
            return False

        if(self.disparo_monitor.is_active == True):
            self.dispararMonitor()
            return True

        if(self.calculate_move_vector.is_active == True):
            self.calculateMovementVector()
            return True

        if(self.send_setpoint_robot.is_active == True):
            self.sendSetpointToRobot()
            return True

        if(self.espera_respuesta.is_active == True):
            self.esperaRespuesta()
            return True

        if(self.compensacion_kalman.is_active == True):
            self.compensationCalculation()
            return True

    def run_monitor(self):
        status = self.__executor.run()
        logging.debug(f'[{__name__} @ {self.__robotID}] returned from RUN: {status}')

        if (status == "WORKING"):
            return True
        elif ((status == "NO_JOBS") or (status == "END")):
            return False

    def calculate_movement_vector(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] calculating setpoint')
        return self.__executor.calculateMovementVector()

    def send_setpoint(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] sending setpoint to robot')
        return self.__executor.sendSetpointToRobot()

    def wait_response(self):
        try:
            logging.debug(f'[{__name__} @ {self.__robotID}] waiting next feedback')
            robotFeedback = self.__robotFeedbackQueue.get(timeout=macros.WAIT_ROBOT_FEEDBACK)
            return self.__executor.updateRobotFeedback(robotFeedback)

        except Exception as e:
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)}')
            return False

    def is_compensation_time(self):
        isCompensationTime = self.__executor.isCompensationTime()
        logging.debug(f'[{__name__} @ {self.__robotID}] is_compensation_time? {isCompensationTime}')
        return isCompensationTime

    def calculo_compensacion(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] calculo del vector de compensacion')
        self.__executor.calculateCompensatedVector()
        return True

    def robot_has_arrived(self):
        return self.__executor.robotIsNearOrPassOverDestinationCoordinate()


    def on_exit_finish_state(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] cycle completed')

    def output_image_state_machine(self):
        img_path = "./state_machine.png"
        self._graph().write_png(img_path)

