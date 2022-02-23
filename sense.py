from http import client
import time
import random
import os
import json
import threading
import paho.mqtt.client as mqtt_client
from sense_hat import SenseHat

sense = SenseHat()
broker = os.environ.get('MQTT_BROKER') or "mqtt"
port = 1883
commandTopic = os.environ.get('COMMAND_TOPIC') or "balena/light/set"
stateTopic = os.environ.get('STATE_TOPIC') or "balena/light"
clientId = f'mqtt-light-{random.randint(0, 1000)}'
decay = 0.5

r = 255
g = 0
b = 0
state = "OFF"
effect = "none"

def next_colour():
    global r
    global g
    global b

    if (r == 255 and g < 255 and b == 0):
        g += 1

    if (g == 255 and r > 0 and b == 0):
        r -= 1

    if (g == 255 and b < 255 and r == 0):
        b += 1

    if (b == 255 and g > 0 and r == 0):
        g -= 1

    if (b == 255 and r < 255 and g == 0):
        r += 1

    if (r == 255 and b > 0 and g == 0):
        b -= 1

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

def sendState(client: mqtt_client):
    global r
    global g
    global b
    global state
    global effect 
    currentState = {
  "state": state,
  "color_mode": "rgb",
  "color": {
    "r": r,
    "g": g,
    "b": b
  },
   "effect": effect
}
    jsonString = json.dumps(currentState)

    client.publish(stateTopic, jsonString)

def light():
    global r
    global g
    global b
    global state
    global effect
    while True:
        while effect == "none":
            sense.clear([r, g, b])
            time.sleep(1)
        while effect == "rainbow":
            sense.clear([r, g, b])
            time.sleep(0.002)
            next_colour()
        while effect == "fading":
            fade_r = r
            fade_g = g
            fade_b = b
            while fade_r > 0 or fade_g > 0 or fade_b > 0:
                sense.clear([fade_r, fade_g, fade_b])
                if fade_r > 0:
                    fade_r = fade_r - 1
                if fade_g > 0:
                    fade_g = fade_g - 1
                if fade_b > 0:
                    fade_b = fade_b - 1
                time.sleep(0.005)
            while fade_r != 255 and fade_g != 255 and fade_b != 255:
                # print("r: " + str(r) + ", g: " + str(g) + ", b: " + str(b))
                if fade_r < r:
                    fade_r = fade_r + 1
                if fade_g < g:
                    fade_g = fade_g + 1
                if fade_b < b:
                    fade_b = fade_b + 1
                sense.clear([fade_r, fade_g, fade_b])
                time.sleep(0.005)

        time.sleep(1)

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global r
        global g
        global b
        global state
        global effect
        values = json.loads(msg.payload.decode())
        print("Values: " + str(values))
        if "state" in values:
            if values["state"] == "OFF":
                r = 0
                g = 0
                b = 0
                state = "OFF"
            else:
                state = "ON"
                if "color" in values:
                    r = int(values["color"]["r"])
                    g = int(values["color"]["g"])
                    b = int(values["color"]["b"])
                if "effect" in values:
                    effect = values["effect"]
                else:
                    effect = "none"
                # sense.clear([r, g, b])
            sendState(client)

    client.subscribe(commandTopic)
    print("Listening on topic " + commandTopic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    thread = threading.Thread(target=light)
    thread.start()
    client.loop_forever()

if __name__ == '__main__':
    run()