from statemachine import StateMachine, State
import time
import json
import logging
import macros

class RobotMachine(StateMachine):
    disparo_monitor = State(initial=True)
    send_setpoint_robot = State()
    espera_respuesta = State()
    finish_state = State(final=True)

    dispararMonitor = (
        disparo_monitor.to(send_setpoint_robot, cond="run_monitor")
        | disparo_monitor.to(finish_state, unless="run_monitor")
        | send_setpoint_robot.to(espera_respuesta, cond="send_setpoint")
        | send_setpoint_robot.to(finish_state, unless="send_setpoint")
        | espera_respuesta.to(disparo_monitor, cond="wait_response")
        | espera_respuesta.to(finish_state, unless="wait_response")
    )

    def __init__(self, executor, robot):
        self.__executor = executor
        self.__robot = robot
        self.__robotID = robot.getRobotID()
        self.__mqttClient = robot.getMqttClient()
        self.__robotFeedbackQueue = robot.getFeedbackQueue()
        super(RobotMachine, self).__init__()

    def run_monitor(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] entre a RUN_MONITOR')
        status = self.__executor.run()
        logging.debug(f'[{__name__} @ {self.__robotID}] returned from RUN: {status}')

        if (status == "WORKING"):
            return True
        elif ((status == "NO_JOBS") or (status == "END")):
            return False

    def send_setpoint(self):
        try:
            setpoint_message = self.__robot.traslateMovementVectorToMessage(self.__executor.getMovementVector())
            msg = self.__mqttClient.publish(self.__robot.getRobotSendSetpointTopic(), setpoint_message, qos=0)
            msg.wait_for_publish()
            return True
        except Exception as e:
            logging.error(f'[{__name__} @ {self.__robotID}] EXCEPTION RAISED: {repr(e)}')
            return False

    def wait_response(self):
        try:
            robotFeedback = self.__robotFeedbackQueue.get(timeout=macros.WAIT_ROBOT_FEEDBACK)
            if(self.check_feedback_message(robotFeedback)):
                # aca deberia avisarle al executor del feedback para que pueda actualizar el kalman y despues tomar la compensacion
                self.__executor.updateRobotFeedback(robotFeedback)
                return True

        except Exception as e:
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)}')
            return False

    def on_exit_finish_state(self):
        logging.debug(f'[{__name__} @ {self.__robotID}] cycle completed')

    def check_feedback_message(self, feedback_message):
        # feedback: '{"dx":0.06, "vx":0.23, "dy":0.07, "vy":0.24}'
        data = json.loads(feedback_message)
        dx = data['dx']
        vx = data['vx']
        dy = data['dy']
        vy = data['vy']
        if(type(dx)!=float or type(vx)!=float or type(dy)!=float or type(vy)!=float):
            logging.error(f'[{__name__}] {self.__robotID} json contains invalid data')
            return False
        return True


    def output_image_state_machine(self):
        img_path = "./state_machine.png"
        self._graph().write_png(img_path)

