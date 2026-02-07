import serial, struct, binascii

ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)
print("Listening... Ctrl+C quit")

cmds = {0x8f:'flags', 0x1c:'current', 0xb3:'voltage', 0xa7:'rudder', 0xf9:'ctrl_temp', 0x48:'motor_temp'}

while True:
    if ser.in_waiting >= 4:
        data = ser.read(4)
        if len(data) == 4:
            cmd, val_lo, val_hi, crc = data
            val = (val_hi << 8) | val_lo
            cmd_name = cmds.get(cmd, f'0x{cmd:02x}')
            print(f"{cmd_name}: {val} (0x{val:04x}) | raw: {binascii.hexlify(data)}")
