# import context  # Ensures paho is in PYTHONPATH
import paho.mqtt.client as mqtt
import threading
import queue

mqttc_queue = queue.Queue()

def on_connect(mqttc, obj, flags, rc):
    # print("rc: " + str(rc))
    print(" ")

def on_message(mqttc, obj, msg):
    print("topic: " + str(msg.topic) + " " + str(msg.qos) + " " + str(msg.payload))
    # print(a + "thread id_2: ", threading.get_ident())
    mqttc_queue.put_nowait("Mensaje de la QQ")

def on_publish(mqttc, obj, mid):
    # print("mid: " + str(mid) + "aa")
    print(" ")
    pass

def on_subscribe(mqttc, obj, mid, granted_qos):
    # print("Subscribed: " + str(mid) + " " + str(granted_qos))
    print(" ")

def on_log(mqttc, obj, level, string):
    print(string)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

# def 

def main():
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_disconnect = on_disconnect
    # Uncomment to enable debug messages
    mqttc.on_log = on_log
    mqttc.connect("localhost", 1883, 60)
    mqttc.loop_start()
    mqttc.subscribe("topic", 2)

    return mqttc, mqttc_queue
    # print("tuple")
    # (rc, mid) = mqttc.publish("tuple", "bayyyr", qos=2)
    # print("class")
    # infot = mqttc.publish("class", "bar", qos=2)
    
    # print("asdasdkasd")
