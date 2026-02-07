import serial, time, threading
ser = serial.Serial('/dev/ttyUSB0', 38400)

def keep_engaged():
    pkt = b'\xc7\xe8\x03\x9d'
    while True:
        ser.write(pkt)
        time.sleep(0.5)

threading.Thread(target=keep_engaged, daemon=True).start()
print("Engaged... Run nano_test.py in NEW terminal!")
input()
