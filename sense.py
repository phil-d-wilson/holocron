from http import client
import time
import random
import os
import json
import paho.mqtt.client as mqtt_client
from sense_hat import SenseHat

sense = SenseHat()
broker = os.environ.get('MQTT_BROKER') or "mqtt"
port = 1883
commandTopic = os.environ.get('COMMAND_TOPIC') or "balena/light/set"
stateTopic = os.environ.get('STATE_TOPIC') or "balena/light"
clientId = f'mqtt-light-{random.randint(0, 1000)}'

r = 255
g = 0
b = 0
state = "OFF"

msleep = lambda x: time.sleep(x / 1000.0)

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(clientId)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def updateState(client: mqtt_client):
    global r
    global g
    global b
    global state
    currentState = {
  "state": state,
  "color_mode": "rgb",
  "color": {
    "r": r,
    "g": g,
    "b": b
  },
   "effect": "pulse"
}
    jsonString = json.dumps(currentState)

    client.publish(stateTopic, jsonString)

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global r
        global g
        global b
        global state
        values = json.loads(msg.payload.decode())
        print("Values: " + str(values))
        if "state" in values:
            if values["state"] == "OFF":
                sense.clear([0,0,0])
                state = "OFF"
            else:
                state = "ON"
                if "color" in values:
                    r = int(values["color"]["r"])
                    g = int(values["color"]["g"])
                    b = int(values["color"]["b"])
                sense.clear([r, g, b])
            updateState(client)

    client.subscribe(commandTopic)
    print("Listening on topic " + commandTopic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()