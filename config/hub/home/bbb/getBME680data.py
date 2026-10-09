#!/usr/bin/env python3
import json
import time
import socket
import signal
import sys
import logging

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

running = True

def handle_signal(signum, frame):
    global running
    logging.info("Received signal %s, stopping...", signum)
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

def main():
    logging.info("Starting BME680 MQTT publisher")

    i2c = busio.I2C(board.SCL, board.SDA)
    bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=I2C_ADDRESS)

    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        while running:
            payload = {
                "temperature": round(bme.temperature, 2),  # C
                "humidity": round(bme.humidity, 2),        # %
                "pressure": round(bme.pressure, 2),        # hPa
                "gas_ohms": int(bme.gas),                  # Ohms
            }
            client.publish(MQTT_TOPIC, json.dumps(payload), qos=0, retain=True)
            logging.info("Published: %s", payload)
            time.sleep(INTERVAL)
    finally:
        logging.info("Stopping MQTT loop and disconnecting")
        client.loop_stop()
        client.disconnect()
        logging.info("Exiting")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Fatal error in BME680 publisher: %s", e)
        sys.exit(1)
