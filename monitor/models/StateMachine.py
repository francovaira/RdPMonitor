from statemachine import StateMachine, State
import time
import json
import logging
import macros

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
        self.__robotFeedbackQueue = robot.getFeedbackQueue()
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
            setpoint_message = self.__robot.traslatePathToMessage(self.__executor.getPathTuple())
            msg = self.__mqttClient.publish(self.__robot.getRobotSendSetpointTopic(), setpoint_message, qos=0)
            msg.wait_for_publish()
            return True
        except:
            print("[STATE MACHINE] No jobs available")
            return False

    def wait_response(self):
        try:
            robotFeedback = self.__robotFeedbackQueue.get(timeout=macros.WAIT_ROBOT_FEEDBACK)
            logging.debug(f'[{__name__}] {self.__robotID} received feedback <{robotFeedback}>')

            if(self.check_feedback_message(robotFeedback)):
                # aca deberia avisarle al executor del feedback para que pueda actualizar el kalman y despues tomar la compensacion
                return True

        except Exception as e:
            logging.error(f'[{__name__}] EXCEPTION RAISED: {repr(e)}')
            return False

    def on_exit_finish_state(self):
        print(f"@{self.__robotID} cycle completed")

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
