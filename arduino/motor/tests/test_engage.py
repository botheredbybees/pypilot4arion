import serial, time
ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)
ser.reset_input_buffer()  # Clear garbage

pkt = b'\xc7\xe8\x03\x9d'  # Raw bytes!
for i in range(20):
    ser.write(pkt)
    time.sleep(0.05)  # 50ms spacing
    print(f"Sent #{i+1}")

print("Check LED now...")
time.sleep(5)
data = ser.read(1000)
print("Response:", data.hex() if data else "NO RESPONSE")
ser.close()
