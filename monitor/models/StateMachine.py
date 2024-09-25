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

    wait_next_path_job = State(initial=True)
    disparo_monitor = State()
    calculate_move_vector = State()
    send_setpoint_robot = State()
    espera_respuesta = State()
    espera_fin_rotacion = State()
    compensacion_kalman = State()
    impactar_cambio_de_estado = State()
    finish_state = State(final=True)

    waitNextPathJob = (
        wait_next_path_job.to(disparo_monitor, cond="is_new_path_job")
        | wait_next_path_job.to(wait_next_path_job, unless="is_new_path_job")
    )

    dispararMonitor = (
        disparo_monitor.to(calculate_move_vector, cond="run_monitor")
        | disparo_monitor.to(wait_next_path_job, unless="run_monitor")
    )

    calculateMovementVector = (
        calculate_move_vector.to(send_setpoint_robot, cond="calculate_movement_vector")
        | calculate_move_vector.to(finish_state, unless="calculate_movement_vector")
    )

    sendSetpointToRobot = (
        send_setpoint_robot.to(espera_respuesta, cond="send_setpoint")
        | send_setpoint_robot.to(finish_state, unless="send_setpoint")
    )

    esperaFinRotacion = (
        espera_fin_rotacion.to(calculate_move_vector, cond="received_fin_rotacion_response")
        | espera_fin_rotacion.to(espera_fin_rotacion, unless="received_fin_rotacion_response")
    )

    esperaRespuesta = (
        espera_respuesta.to(espera_fin_rotacion, cond="is_rotacion_movement")
        | espera_respuesta.to(impactar_cambio_de_estado, cond="robot_has_arrived")
        | espera_respuesta.to(compensacion_kalman, cond="is_compensation_time")
        | espera_respuesta.to(espera_respuesta, cond="wait_response")
        | espera_respuesta.to(disparo_monitor, unless="wait_response")
    )

    impactarCambioEstado = (
        impactar_cambio_de_estado.to(disparo_monitor, cond="send_confirmacion_monitor")
    )

    compensationCalculation = (
        compensacion_kalman.to(send_setpoint_robot, cond="calculo_compensacion")
    )

    def run(self):
        if (self.finish_state.is_active == True):
            return False

        if(self.wait_next_path_job.is_active == True):
            self.waitNextPathJob()
            return True

        if(self.disparo_monitor.is_active == True):
            self.dispararMonitor()
            return True

        if(self.calculate_move_vector.is_active == True):
            self.calculateMovementVector()
            return True

        if(self.send_setpoint_robot.is_active == True):
            self.sendSetpointToRobot()
            return True

        if(self.espera_fin_rotacion.is_active == True):
            self.esperaFinRotacion()
            return True

        if(self.espera_respuesta.is_active == True):
            self.esperaRespuesta()
            return True

        if(self.impactar_cambio_de_estado.is_active == True):
            self.impactarCambioEstado()
            return True

        if(self.compensacion_kalman.is_active == True):
            self.compensationCalculation()
            return True

    def is_rotacion_movement(self):
        isRotacionMovement = self.__executor.isRotacionMovement()
        logging.debug(f'[{__name__} @ {self.__robotID}] is_rotacion_movement? {isRotacionMovement}')
        return isRotacionMovement

    def is_new_path_job(self):
        status = self.__executor.isNewPathJob()
        return status

    def run_monitor(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] running monitor')
        status = self.__executor.run()
        logging.debug(f'[{__name__} @ {self.__robotID}] returned from RUN: {status}')

        if (status == "WAIT_CONF"):
            return True
        elif (status == "WORKING"):
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
            logging.debug(f'[{__name__} @ {self.__robotID}] waiting next feedback\n\n\n\n')
            robotFeedback = self.__robotFeedbackQueue.get(timeout=macros.WAIT_ROBOT_FEEDBACK)
            return self.__executor.updateRobotFeedback(robotFeedback)

        except Exception as e:
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)}')
            return False

    def received_fin_rotacion_response(self):
        try:
            logging.debug(f'[{__name__} @ {self.__robotID}] waiting fin rotacion\n\n')
            robotFeedback = self.__robotFeedbackQueue.get(timeout=macros.WAIT_ROBOT_FEEDBACK)
            value = self.__executor.processRobotFeedback(robotFeedback)
            return (value == 2)
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
        value = self.__executor.robotIsNearOrPassOverDestinationCoordinate()
        logging.debug(f'[{__name__} @ {self.__robotID}] robot has arrived ? {value}')
        return value

    def send_confirmacion_monitor(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] sending confirmation to monitor')
        return self.__executor.setCoordinateConfirmation(False)

    def on_exit_finish_state(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] cycle completed')

    def output_image_state_machine(self):
        img_path = "./state_machine.png"
        self._graph().write_png(img_path)

