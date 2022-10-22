# import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt
import threading
import queue
import time

mqttc_condition = threading.Condition()

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
    # print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
    mqttc_condition.acquire()
    mqttc_condition.notify()
    mqttc_condition.release()

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid) + "aa")
    pass

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    print(" ")

def on_log(mqttc, obj, level, string):
    print(string)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


def thread_run():
    mqttc = mqtt.Client()
    mqttc.max_inflight_messages_set(1)
    try:
        mqttc.connect("localhost", 1883, 60)
        mqttc.loop_start()
    except:
        print("No se pudo conectar al broker.")

    while True:
        msg = mqttc.publish("/topic/ping", "motor_direction", qos=2)
        msg.wait_for_publish()
        time.sleep(1)

def main():
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_disconnect = on_disconnect
    # Uncomment to enable debug messages
    # mqttc.on_log = on_log
    mqttc.max_inflight_messages_set(1)
    try:
        mqttc.connect("localhost", 1883, 60)
        mqttc.loop_start()
        mqttc.subscribe("/topic/robot", 2)
    except:
        print("No se pudo conectar al broker.")

    # thread_ping = threading.Thread(target=thread_run)
    # thread_ping.start()

    return mqttc, mqttc_condition