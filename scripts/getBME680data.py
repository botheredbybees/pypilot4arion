#!/usr/bin/env python3
import json
import time
import socket

import board
import busio
import adafruit_bme680
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "arion/sensors/cabin/bme680"
MQTT_CLIENT_ID = f"bme680-{socket.gethostname()}"
I2C_ADDRESS = 0x77
INTERVAL = 10

i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=I2C_ADDRESS)

client = mqtt.Client(client_id=MQTT_CLIENT_ID)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

while True:
    payload = {
        "temperature": round(bme.temperature, 2),   # C
        "humidity": round(bme.humidity, 2),         # %
        "pressure": round(bme.pressure, 2),         # hPa
        "gas_ohms": int(bme.gas),                   # Ohms
    }
    client.publish(MQTT_TOPIC, json.dumps(payload), qos=0, retain=True)
    time.sleep(INTERVAL)