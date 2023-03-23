# import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt
import threading
import queue
import time
import json
import traceback
import logging

mqttc_condition = threading.Condition()
mqttc_event = threading.Event()
mqttc_ping_event = threading.Event()
mqttc_queue = queue.Queue()
mqttc_ping_flag = 1

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
    print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
    mqttc_condition.acquire()
    mqttc_condition.notify()
    mqttc_condition.release()

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid) + "aa")
    pass

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_subscribe_thread(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

def on_log_thread(mqttc, obj, level, string):
    print(string)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def on_ping_message(mqttc, obj, msg):
    str_data = str(msg.payload)
    str_data = str_data[2:(len(str_data)-1)]
    try:
        json_data_response = json.loads(str_data)
        if 'id' in json_data_response.keys():
            getMqttcQueue().put(json_data_response.get('id'))
            mqttc_event.clear()
    except Exception:
        logging.exception('Error al obtener el id del robot')

def thread_run():
    mqttc = mqtt.Client()
    # mqttc.on_log = on_log_thread
    mqttc.on_subscribe = on_subscribe_thread
    mqttc.message_callback_add('/topic/ping_response', on_ping_message)

    try:
        mqttc.connect('localhost', 1883, 60)
        mqttc.loop_start()
        mqttc.subscribe('/topic/ping_response', 2)
    except:
        logging.error('No se pudo conectar al broker')

    while True:
        mqttc_event.wait()
        while mqttc_event.isSet():
            msg = mqttc.publish('/topic/ping', '{"id":"searching"}', qos=2)
            msg.wait_for_publish()
            time.sleep(1)

def getMqttcEvent():
    return mqttc_event

def getMqttcQueue():
    return mqttc_queue

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

    thread_ping = threading.Thread(target=thread_run)
    thread_ping.start()

    return mqttc, mqttc_condition