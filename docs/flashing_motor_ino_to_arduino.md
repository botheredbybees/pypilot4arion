# Understanding and Installing motor.ino

## Overview

The `motor.ino` sketch is pypilot's motor controller firmware for Arduino Nano/Uno that interfaces between pypilot and motor controllers [arduino/motor/motor.ino](https://github.com/botheredbybees/pypilot4arion/blob/main/arduino/motor/motor.ino). Your Octopus Model 1012 is a reversible DC piston pump with only two motor wires - direction is controlled by reversing polarity, making the IBT_2 (BTS7960) H-bridge an ideal controller. [marinedirect.com](https://www.marinedirect.com.au/octaf1212-octopus-autopilot-pump-type-2-adjustable)

### Your Hardware Configuration

| Component | Specification |
|-----------|--------------|
| Pump | Octopus Model 1012 - 12V DC, 1000 cu.cm/min  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/d2aaa3b6-e700-4b91-b83b-b8c3505beee9/PXL_20260116_002621737.jpg) |
| Current Draw | 4-6A average, 19A max  [marinedirect.com](https://www.marinedirect.com.au/octaf1212-octopus-autopilot-pump-type-2-adjustable) |
| Motor Controller | IBT_2 (BTS7960) - 43A capability |
| Microcontroller | Arduino Nano (CH340 clone) |
| Control Mode | H-bridge (pwm_style = 0 or 2) |

The old TMQ AP8 autopilot used 4 solenoids to create an external H-bridge for polarity reversal. The IBT_2 replaces this entirely with an integrated H-bridge chip, greatly simplifying the wiring. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/c08c67dc-f137-44cb-8c9b-b0f3e2177826/PXL_20260116_002615056.jpg)

## Part 1: Installing Arduino IDE on Ubuntu

### Method 1: Arduino IDE 2.x (Recommended)

```bash
# Download latest AppImage
cd ~/Downloads
wget https://downloads.arduino.cc/arduino-ide/arduino-ide_latest_Linux_64bit.AppImage

# Make executable and install
chmod +x arduino-ide_*_Linux_64bit.AppImage
mkdir -p ~/.local/bin
mv arduino-ide_*_Linux_64bit.AppImage ~/.local/bin/arduino-ide

# Add user to dialout group for serial port access
sudo usermod -a -G dialout $USER

# Log out and back in for group membership to take effect
```

### Method 2: Arduino IDE 1.8.x (For Makefile Compatibility)

```bash
# Download from arduino.cc
cd ~/Downloads
wget https://downloads.arduino.cc/arduino-1.8.19-linux64.tar.xz
tar -xf arduino-1.8.19-linux64.tar.xz
sudo mv arduino-1.8.19 /opt/arduino
sudo ln -s /opt/arduino/arduino /usr/local/bin/arduino

# Add user to dialout group
sudo usermod -a -G dialout $USER
```

## Part 2: CH340 Driver for Chinese Arduino Clones

Most modern Linux kernels (4.x+) include CH340 drivers, but some cheap clones have counterfeit chips that require additional steps. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/bbf498a4-6155-4a7b-8d38-79137efa08d1/PXL_20260116_064310365.jpg)

### Verify CH340 Recognition

```bash
# Plug in Arduino, then check kernel messages
dmesg | tail -n 20

# Look for:
# [xxxxx.xxxxxx] ch341-uart converter now attached to ttyUSB0
```

### If Not Recognized: Troubleshooting Steps

1. **Check if module is loaded:**
   ```bash
   lsmod | grep ch341
   ```

2. **If no CH341 module, install driver:**
   ```bash
   sudo apt update
   sudo apt install build-essential linux-headers-$(uname -r)
   
   # Clone and build CH341 driver
   cd ~/Downloads
   git clone https://github.com/juliagoda/CH341SER.git
   cd CH341SER
   make
   sudo make load
   ```

3. **For counterfeit CH340 chips** (common on very cheap clones):
   - Some boards have chips that appear as CH340 but don't work with standard drivers
   - Try different USB ports (USB 2.0 ports sometimes work better than USB 3.0)
   - Use a powered USB hub
   - If still failing, consider purchasing a genuine Arduino or quality clone with FTDI chip

### Verify Serial Port Access

```bash
# List serial ports
ls -l /dev/ttyUSB* /dev/ttyACM*

# Check you're in dialout group
groups | grep dialout

# If permission denied after adding to dialout, try:
sudo chmod 666 /dev/ttyUSB0  # Temporary fix
```

## Part 3: Downloading and Compiling motor.ino

### Clone Repository

```bash
cd ~
git clone https://github.com/botheredbybees/pypilot4arion.git
cd pypilot4arion/arduino/motor
ls -la
# Should show: motor.ino, crc.h, Makefile, README
```

### Compile and Upload via Arduino IDE

1. **Launch Arduino IDE:**
   ```bash
   arduino
   # or: ~/.local/bin/arduino-ide
   ```

2. **Configure Board Settings:**
   - `Tools → Board → Arduino AVR Boards → Arduino Nano`
   - `Tools → Processor → ATmega328P (Old Bootloader)` ← **Critical for most clones**
   - `Tools → Port → /dev/ttyUSB0`

3. **Open and Upload:**
   - `File → Open → ~/pypilot4arion/arduino/motor/motor.ino`
   - Click Verify (checkmark) to compile
   - Click Upload (arrow) to flash

### Compile via Makefile (Alternative)

```bash
cd ~/pypilot4arion/arduino/motor

# Edit Makefile for your setup
nano Makefile
# Set: BOARD_TAG = nano
# Set: BOARD_SUB = atmega328old
# Set: MONITOR_PORT = /dev/ttyUSB0

make
make upload
```

## Part 4: Configuring motor.ino for IBT_2 Controller

The IBT_2 uses the BTS7960 dual H-bridge chip with built-in current sensing. The motor.ino firmware supports this via `pwm_style = 2` (VNH2SP30 mode) which works similarly. [dcc-ex](https://dcc-ex.com/reference/hardware/motorboards/IBT_2-motor-board-setup.html)

### IBT_2 Pin Configuration

Based on the motor.ino source and IBT_2 specifications: [instructables](https://www.instructables.com/Motor-Driver-BTS7960-43A/)

```
IBT_2 Pin     →  Arduino Pin    →  motor.ino Definition
─────────────────────────────────────────────────────────
RPWM (pin 1)  →  D9             →  pwm_output_pin / hbridge_a_top_pin
LPWM (pin 2)  →  D10            →  enable_pin / hbridge_b_top_pin
R_EN (pin 3)  →  D2 or tied HIGH→  hbridge_a_bottom_pin
L_EN (pin 4)  →  D3 or tied HIGH→  hbridge_b_bottom_pin
R_IS (pin 5)  →  A1 (optional)  →  Current sense
L_IS (pin 6)  →  A1 (optional)  →  Current sense (tie together)
Vcc (pin 7)   →  5V             →  Logic power
GND (pin 8)   →  GND            →  Common ground
```

### Wiring Diagram (ASCII)

```
                    ┌─────────────────────────────────────┐
                    │           IBT_2 Module              │
                    │  ┌─────────────────────────────┐    │
   Arduino Nano     │  │  BTS7960    BTS7960         │    │   Octopus 1012
   ┌──────────┐     │  │   (A)        (B)            │    │   ┌──────────┐
   │          │     │  └─────────────────────────────┘    │   │          │
   │       D9 ├─────┼──► RPWM (1)                         │   │          │
   │      D10 ├─────┼──► LPWM (2)                         │   │   Motor  │
   │          │     │                                     │   │    (+)   │
   │       D2 ├─────┼──► R_EN (3)  ─┐                     │   │     │    │
   │       D3 ├─────┼──► L_EN (4)  ─┴─ (or tie to 5V)    │   │     │    │
   │          │     │                         M+ ─────────┼───┼─────┘    │
   │       A1 ├─────┼──► R_IS (5) ─┬─► Current Sense     │   │          │
   │          │     │   L_IS (6) ─┘   (optional)         │   │   Motor  │
   │          │     │                         M- ─────────┼───┼─────(-)  │
   │       5V ├─────┼──► Vcc (7)                          │   │          │
   │      GND ├─────┼──► GND (8)                          │   └──────────┘
   │          │     │                                     │
   │       A0 ├──┐  │            B+ ──────────────────────┼──► 12V Battery +
   └──────────┘  │  │            B- ──────────────────────┼──► 12V Battery -
                 │  └─────────────────────────────────────┘
                 │
                 └──► Voltage divider (560Ω + 10kΩ to GND)
                      for battery voltage monitoring
```

### Hardware Configuration Pins

The motor.ino uses hardware pins to detect configuration at startup [arduino/motor/motor.ino](https://github.com/botheredbybees/pypilot4arion/blob/main/arduino/motor/motor.ino):

| Pin | Function | For IBT_2 |
|-----|----------|-----------|
| D4 | Shunt resistance select | Leave floating (pullup = 0.05Ω) |
| D5 | Low/high current mode | Leave floating (low current, 20A max) |
| D6 | PWM style select | **Ground this pin** for H-bridge mode |
| D7 | Port fault input | Optional limit switch |
| D8 | Starboard fault input | Optional limit switch |
| D11 | Clutch output | Not used with IBT_2 |
| D12 | Voltage sense mode | Leave floating for 12V mode |
| D13 | Status LED | Shows engaged state |

**Critical:** Ground pin D6 to select H-bridge mode (pwm_style = 0). If left floating, motor.ino defaults to RC servo PWM output which won't work with IBT_2.

### Simple IBT_2 Wiring (Minimum Required)

For basic operation with the Octopus pump:

```
Arduino Nano          IBT_2
────────────          ─────
D9  ─────────────────► RPWM
D10 ─────────────────► LPWM
5V  ────────┬────────► Vcc
            └────────► R_EN (tie high)
            └────────► L_EN (tie high)
GND ─────────────────► GND
D6  ─────────────────► GND (select H-bridge mode)

IBT_2                 Octopus 1012
─────                 ────────────
M+  ─────────────────► Motor +
M-  ─────────────────► Motor -

IBT_2                 12V Battery
─────                 ───────────
B+  ─────────────────► Positive
B-  ─────────────────► Negative (common with Arduino GND)
```

## Part 5: Setting Correct Fuse Bits

The motor.ino README emphasizes brown-out detection (BOD) to prevent flash corruption during power fluctuations - critical in marine environments [arduino/motor/README](https://github.com/botheredbybees/pypilot4arion/blob/main/arduino/motor/README).

### Check Fuse Settings

Using a second Arduino as ISP programmer:

```bash
# Read current efuse
avrdude -c avrisp -b 19200 -P /dev/ttyUSB0 -p m328p -U efuse:r:-:h

# Expected: 0x04 or 0xFD (BOD enabled)
# Bad: 0xFF or 0x07 (BOD disabled)
```

### Set Correct Fuses (If Needed)

```bash
# Low fuse (clock settings)
avrdude -c avrisp -b 19200 -P /dev/ttyUSB0 -u -p m328p -U lfuse:w:0x7f:m

# High fuse (boot settings)  
avrdude -c avrisp -b 19200 -P /dev/ttyUSB0 -u -p m328p -U hfuse:w:0xda:m

# Extended fuse (BOD at 4.3V)
avrdude -c avrisp -b 19200 -P /dev/ttyUSB0 -u -p m328p -U efuse:w:0x04:m
```

## Part 6: Testing the Installation

### Serial Communication Test

```bash
# Install screen
sudo apt install screen

# Connect at 38400 baud (motor.ino default × DIV_CLOCK)
# For DIV_CLOCK=4 (default): 38400 × 4 = 153600 baud
screen /dev/ttyUSB0 153600

# You should see periodic binary packets (not human-readable)
# Press Ctrl+A then K to exit
```

### Using pypilot_servo_test

pypilot includes a test utility for the motor controller:

```bash
cd ~/pypilot4arion
python3 -m pypilot.servo -t /dev/ttyUSB0
```

### Manual Motor Test (Without pypilot)

Create a simple test sketch to verify IBT_2 wiring:

```cpp
// IBT_2 Motor Test - save as ibt2_test.ino
#define RPWM 9
#define LPWM 10

void setup() {
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  Serial.begin(9600);
  Serial.println("IBT_2 Test - Commands: f=forward, r=reverse, s=stop");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    switch(c) {
      case 'f': // Forward (port)
        analogWrite(LPWM, 0);
        analogWrite(RPWM, 128); // 50% speed
        Serial.println("Forward");
        break;
      case 'r': // Reverse (starboard)
        analogWrite(RPWM, 0);
        analogWrite(LPWM, 128);
        Serial.println("Reverse");
        break;
      case 's': // Stop
        analogWrite(RPWM, 0);
        analogWrite(LPWM, 0);
        Serial.println("Stopped");
        break;
    }
  }
}
```

Upload this test sketch, open Serial Monitor at 9600 baud, and send 'f', 'r', or 's' to test motor direction.

## Part 7: Troubleshooting

### Upload Fails with "programmer not responding"

- Select `Tools → Processor → ATmega328P (Old Bootloader)`
- Press reset button on Arduino just as upload starts
- Try different USB cable (some are power-only)

### CH340 Not Recognized

- Check `dmesg | grep ch34` after plugging in
- Try USB 2.0 port instead of USB 3.0
- Install CH341SER driver manually (see Part 2)

### Motor Runs One Direction Only

- Check IBT_2 enable pins (R_EN, L_EN) are HIGH
- Verify D6 is grounded for H-bridge mode
- Swap RPWM/LPWM connections

### BAD_FUSES Flag in pypilot

- Use ISP programmer to set correct fuses (see Part 5)
- This is important for reliability but won't prevent operation

### Motor Doesn't Respond to pypilot

1. Verify serial communication with test utility
2. Check pypilot servo configuration matches hardware
3. Ensure voltage is within range (9-20V for 12V mode)
4. Check for fault flags in pypilot client

## Part 8: pypilot Configuration for IBT_2

Once motor.ino is running, configure pypilot:

```python
# In pypilot client or via SignalK
servo.max_current = 1500  # 15A - below Octopus 19A max
servo.max_controller_temp = 6000  # 60°C
servo.period = 0.4  # Adjust for pump response
```

The IBT_2 with Octopus 1012 provides proportional control - pypilot can vary pump speed via PWM for smoother steering corrections compared to on/off solenoid systems. [octopusdrives](https://octopusdrives.com/products/hydraulic-reversing-piston-pumps/)

## Safety Reminders

⚠️ **Critical for Marine Use:**

1. **Add inline fuse** (15-20A) between battery and IBT_2
2. **Test on land** before sea trials
3. **Maintain manual steering** capability
4. **Set rudder limits** to prevent mechanical damage
5. **Waterproof all electronics** - conformal coating recommended
6. **Monitor battery voltage** - low voltage causes erratic behavior

***

*Last updated: 2026-01-18*  
*Part of pypilot4arion documentation*.

**Next Step:** Once the motor controller is ready, proceed to **[TinyPilot Setup & Configuration](tinypilot_setup.md)** to configure the main autopilot computer.
```