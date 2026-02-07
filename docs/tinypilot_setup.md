# TinyPilot Setup & Configuration

## Overview

**TinyPilot** refers to the pypilot autopilot software running on a Raspberry Pi Zero W (or Zero 2 W) with minimal OS configuration. On *Arion*, this Pi acts as the **Autopilot Core**.

**Important**: This installation uses **standard Raspberry Pi OS Lite** (not the TinyPilot RAM-based image) with pypilot installed from source, allowing for easier customization and debugging.

The TinyPilot Pi handles:

1. Reading sensors (IMU via I2C, optional rudder feedback)
2. Running the PID control loop
3. Sending drive commands to the motor controller
4. Providing web interface for autopilot control
5. Publishing autopilot data via TCP for Signal K integration

It functions independently of the navigation computer (Lysmarine Pi 4), ensuring you still have steering even if the main computer fails.

## Core Logic & Functionality

The pypilot system operates on a continuous control loop (typically 10-20Hz):

1. **State Estimation**: Reads the Inertial Measurement Unit (IMU) to determine current Heading, Pitch, Roll, and Rate of Turn
2. **Error Calculation**: Compares current Heading vs. Target Heading to calculate the "Heading Error"
3. **PID Control**: A Proportional-Integral-Derivative (PID) controller processes this error to determine the required rudder correction:
    * *Proportional*: "We are 10° off, turn rudder 10°"
    * *Integral*: "We have been 2° off for a long time, add more rudder slowly"
    * *Derivative*: "We are turning too fast, counter-steer to stop the swing"
4. **Output Generation**: Converts the desired rudder angle into PWM/UART commands for the motor controller

### Power Architecture

The TinyPilot Pi Zero is powered via a **12V to 5V Buck Converter** connected to **House Bus A** of the 12V electrical system. This ensures stable 5V power even when the engine cranks or heavy loads dip the battery voltage.

**Power Specifications**:
- **Input**: 12V DC from House Bus A
- **Buck Converter**: 12V→5V, minimum 2A continuous output
- **Fuse**: 1A on 12V positive line (see power distribution docs)
- **Wire Gauge**: 18 AWG from fuse block to buck converter
- **Output**: 5V via USB cable to Pi Zero (recommended) or GPIO pins 2/4

> [!IMPORTANT]
> **Power Stability**: Poor power supplies are the #1 cause of random autopilot disconnects. Use a quality buck converter with low ripple.

## Network Configuration

The TinyPilot Pi is configured with a **static IP address** on the YachtArion network:

- **SSID**: `YachtArion` (EZR23 4G Router)
- **IP Address**: `192.168.20.101` (static)
- **Gateway**: `192.168.20.1` (EZR23 Router)
- **DNS**: `8.8.8.8`, `1.1.1.1`
- **Subnet**: `255.255.255.0` (/24)

This static IP makes it easy to:
- Access the web interface at `http://192.168.20.101`
- Configure Signal K to connect at `192.168.20.101:20220`
- Swap failed hardware with pre-configured replacement Pis

## Installation Hardware Setup

### Required Components

**Core**:
- Raspberry Pi Zero W or Zero 2 W
- MicroSD Card (16GB+ Class 10 recommended)
- 12V to 5V Buck Converter (2A+ output, e.g., LM2596 or Pololu D24V22F5)
- USB power cable (micro USB for Pi Zero)

**Sensors & Control**:
- IMU Module: MPU-9250, ICM-20948, or BNO-055 (I2C interface)
- Arduino Nano/Uno running motor.ino firmware
- IBT-2 Motor Controller (BTS7960B H-Bridge)
- Rudder feedback sensor (optional but recommended)

**Wiring** (no HAT used):
- Dupont jumper wires for I2C connections
- USB cable for Arduino connection
- Connectors and heat shrink

### Wiring the Power Supply

1. **12V Input to Buck Converter**:
   - Connect **House Bus A positive** (12V) through a **1A fuse** to buck converter input (+)
   - Connect **Common negative bus** to buck converter input (-)
   - Use **18 AWG** marine-grade wire
   - Label connections clearly

2. **5V Output to Raspberry Pi**:
   - **Recommended method**: USB cable from buck converter 5V USB output to Pi Zero micro USB port
   - **Alternative**: Solder/crimp 5V and GND wires directly to GPIO:
     - 5V to Pin 2 or Pin 4
     - GND to Pin 6, 9, 14, 20, 25, 30, 34, or 39
     - **Warning**: No fuse protection when using GPIO power input; use USB method if possible

3. **Power Distribution Reference**:
   - See [12V Solar System](./12v_solar_system.md) for complete electrical system
   - See [Network Map](./network_map.md) for power distribution table

### Wiring the IMU (Manual I2C Connection)

**Important**: Since we're not using a pypilot HAT, you'll wire the IMU directly to the Pi Zero's GPIO header.

**Standard I2C Connection** (MPU-9250, ICM-20948, BNO-055):

| IMU Pin | Pi Zero GPIO | Pin Number | Wire Color (suggested) |
| :--- | :--- | :--- | :--- |
| VCC (3.3V) | 3.3V Power | Pin 1 or 17 | Red |
| GND | Ground | Pin 6, 9, 14, etc. | Black |
| SDA | GPIO 2 (SDA) | Pin 3 | Blue or Green |
| SCL | GPIO 3 (SCL) | Pin 5 | Yellow or White |

**Notes**:
- Use **short wires** (< 15cm if possible) to minimize I2C noise
- IMU must use **3.3V**, not 5V (will damage sensor)
- Keep IMU away from high-current motor wires to reduce magnetic interference
- Orient IMU with clear reference to boat's centerline (document orientation for calibration)

**I2C Address Detection**:
```bash
# After wiring, test I2C connection
sudo i2cdetect -y 1

# Should show device at address:
# MPU-9250: 0x68 or 0x69
# BNO-055: 0x28 or 0x29
# ICM-20948: 0x68 or 0x69
```

### Wiring the Arduino Motor Controller

**Connection**:
- Connect Arduino via **USB cable** to any USB port on Pi Zero (use USB OTG adapter)
- Arduino should appear as `/dev/ttyUSB0` or `/dev/ttyACM0`
- No additional GPIO wiring needed for motor control (handled via serial)

**Motor Controller Reference**:
- See [Flashing motor.ino to Arduino](./flashing_motor_ino_to_arduino.md) for complete Arduino setup
- See [Hardware Review](./hardware_review.md) for IBT-2 wiring to Arduino and hydraulic pump

## Software Installation

### 1. Prepare Raspberry Pi OS

1. **Download Raspberry Pi OS Lite** (64-bit recommended for Pi Zero 2 W):
   - Use [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
   - Select "Raspberry Pi OS Lite (64-bit)" or "Raspberry Pi OS Lite (32-bit)" for original Pi Zero W

2. **Configure OS settings** in Imager (gear icon):
   - Set hostname: `tinypilot`
   - Enable SSH
   - Set username/password (e.g., `bbb` / strong password)
   - Configure WiFi: SSID `YachtArion`, password, country AU
   - Set locale/timezone: Australia/Hobart

3. **Flash to SD card** and boot Pi Zero

### 2. Initial System Setup

```bash
# SSH into Pi (will initially have DHCP address)
ssh bbb@tinypilot.local
# or find DHCP address and: ssh bbb@192.168.20.x

# Update system
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3-pip python3-dev python3-setuptools \
  python3-numpy python3-scipy python3-pil python3-flask python3-socketio \
  git i2c-tools python3-smbus python3-smbus2 cmake libpython3-dev \
  python3-gpiozero pipx

# Enable I2C interface
sudo raspi-config nonint do_i2c 0

# Configure pipx path
pipx ensurepath

# Reboot
sudo reboot
```

**Important**: We removed `wiringpi` (deprecated) and added `pipx` for proper Python package installation.

### 3. Configure Static IP Address

**After reboot, configure the static IP**:

```bash
# SSH back in
ssh bbb@tinypilot.local

# Configure static IP using nmcli
sudo nmcli con mod "YachtArion" ipv4.addresses 192.168.20.101/24
sudo nmcli con mod "YachtArion" ipv4.gateway 192.168.20.1
sudo nmcli con mod "YachtArion" ipv4.dns "8.8.8.8 1.1.1.1"
sudo nmcli con mod "YachtArion" ipv4.method manual
sudo nmcli con up "YachtArion"

# Verify configuration
ip addr show wlan0
ping 192.168.20.1
ping 192.168.20.100  # Test Lysmarine connectivity
ping google.com      # Test internet via 4G

# Reboot and verify IP persists
sudo reboot
```

**Alternative method** (if nmcli not available):
```bash
sudo nano /etc/dhcpcd.conf

# Add at end:
interface wlan0
static ip_address=192.168.20.101/24
static routers=192.168.20.1
static domain_name_servers=8.8.8.8 1.1.1.1

# Save and restart
sudo systemctl restart dhcpcd
```

### 4. Install Pypilot Software

> [!IMPORTANT]
> **Understanding Pypilot Repositories**:
> - **pypilot** = Main autopilot software (steering logic, motor control, IMU handling)
> - **pypilot_data** = Calibration data files and configuration templates
> 
> You need to install **pypilot** first, then **pypilot_data**. Don't confuse them!

> [!WARNING]
> **Why pipx?** Modern Raspberry Pi OS uses "externally-managed-environment" which blocks direct `pip install` commands. Using `pipx` creates isolated environments for each application, avoiding conflicts and system breakage.

```bash
# SSH to tinypilot
ssh bbb@192.168.20.101

# Clone the MAIN pypilot repository
cd ~
git clone https://github.com/pypilot/pypilot.git
cd pypilot

# Install pypilot using pipx (handles Python environment isolation)
pipx install .

# Verify installation
pypilot --version

# Clone pypilot_data repository (configuration and calibration data)
cd ~
git clone https://github.com/pypilot/pypilot_data.git
cd pypilot_data

# Inject pypilot_data into pypilot's environment
pipx inject pypilot .
```

**What just happened?**
- `pipx install .` created an isolated Python environment for pypilot
- Pypilot executables (`pypilot`, `pypilot_web`) are now in your PATH
- `pipx inject` added pypilot_data into pypilot's environment
- No conflicts with system Python packages

### 5. Create Pypilot Service

Create systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/pypilot.service
```

**Add the following content**:
```ini
[Unit]
Description=Pypilot Autopilot Service
After=network.target

[Service]
Type=simple
User=bbb
WorkingDirectory=/home/bbb
ExecStart=/home/bbb/.local/bin/pypilot
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pypilot.service
sudo systemctl start pypilot.service

# Check status
sudo systemctl status pypilot.service

# View logs
sudo journalctl -u pypilot.service -f
```

### 6. Create Pypilot Web Service

Create service for the web interface:

```bash
sudo nano /etc/systemd/system/pypilot_web.service
```

**Content**:
```ini
[Unit]
Description=Pypilot Web Interface
After=network.target pypilot.service
Requires=pypilot.service

[Service]
Type=simple
User=bbb
WorkingDirectory=/home/bbb
ExecStart=/home/bbb/.local/bin/pypilot_web
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pypilot_web.service
sudo systemctl start pypilot_web.service
sudo systemctl status pypilot_web.service
```

## Configuration

### 1. Access Web Interface

From any device on the YachtArion network:

```
http://192.168.20.101
```

You should see the pypilot web interface.

### 2. Motor Controller Setup

Pypilot communicates with your Arduino-based motor controller via serial.

**Prerequisites**:
- Arduino flashed with `motor.ino` firmware
- **[Guide: Flashing motor.ino to Arduino](flashing_motor_ino_to_arduino.md)**
- Arduino connected via USB to Pi Zero

**Configuration**:
1. In the web interface, go to **Configuration → Servo**
2. Set `Driver` to **Arduino**
3. Pypilot should auto-detect serial port (e.g., `/dev/ttyUSB0` or `/dev/ttyACM0`)
4. If not detected, check connection:
   ```bash
   ls /dev/ttyUSB* /dev/ttyACM*
   dmesg | grep tty
   ```

### 3. IMU Configuration

**Verify IMU is detected**:
```bash
# Check I2C bus
sudo i2cdetect -y 1

# Should show device at expected address
# Check pypilot logs
sudo journalctl -u pypilot.service | grep -i imu
```

**In web interface**:
1. Go to **Configuration → IMU**
2. Verify IMU type is detected (MPU9250, ICM20948, or BNO055)
3. Check that heading, pitch, roll values are updating

### 4. IMU Calibration

**Critical for accurate autopilot operation**:

1. **Level Calibration**:
   - Motor boat in calm water
   - Ensure boat is sitting at normal waterline
   - Go to **Configuration → Calibration**
   - Click **"Level"** to zero pitch and roll

2. **Compass Calibration**:
   - Go to **Configuration → Calibration**
   - Click **"Compass Calibration"**
   - Motor boat in slow circles (360° turn)
   - Alternatively, motor in figure-8 pattern
   - Watch the calibration scope plot
   - Goal: 2D plot should form a circle, not an oval or distorted shape
   - Complete when plot is circular and "Calibration" indicator shows good
   - Click **"Save"**

**Tips**:
- Perform compass calibration away from docks and other boats (magnetic interference)
- Repeat calibration if you move large metal objects near IMU
- Re-level if boat's waterline changes significantly (fuel, water, stores)

### 5. Configure Servo Parameters

Go to **Configuration → Servo** and configure for your hydraulic system:

**For IBT-2 with Octopus 1012 pump**:
- **Driver**: Arduino
- **Max Current**: 15-20A (monitor actual draw and adjust)
- **Max Controller Temp**: 60°C
- **Voltage**: 12V
- **Max Slew Speed**: Start with 10 deg/s, adjust based on testing
- **Rudder Range**: ±35° (or your boat's actual range)

**Motor Direction**:
- Test with manual control (port/starboard buttons)
- If rudder moves opposite to command, check **"Invert Motor"** setting

### 6. Configure PID Gains

Initial conservative values:

- **P (Proportional)**: 0.005-0.01
- **I (Integral)**: 0.0 (start with zero)
- **D (Derivative)**: 0.1-0.2

These will be tuned during sea trials. See [Testing and Tuning Guide](./testing_and_tuning.md) for detailed procedure.

## Testing

Complete testing and tuning procedures are detailed in:

**[→ Testing and Tuning Guide](testing_and_tuning.md)**

### Quick Dockside Test

1. **Web Interface Access**:
   - Open `http://192.168.20.101`
   - Verify interface loads and shows sensor data

2. **Manual Control**:
   - Click port/starboard arrows
   - **Verify**: Rudder moves in correct direction
   - **Check**: Rudder reaches expected range (±35°)
   - **Listen**: Pump should run smoothly without cavitation

3. **Direction Test**:
   - Command "Port" (left)
   - Rudder should move to port (boat would turn left)
   - If reversed, enable "Invert Motor" in Configuration → Servo

4. **Endstops** (if rudder feedback installed):
   - Command hard over both directions
   - Verify autopilot stops before mechanical limits

### Sea Trial Procedure

1. **Compass Mode Test**:
   - Motor to safe area with clear water
   - Steer to desired heading manually
   - Engage **Auto** (Compass mode)
   - Observe boat holds course (within ±5-10° initially)

2. **Response Assessment**:
   - **Good**: Smooth corrections, minimal wandering
   - **Oscillation** (zig-zag): Reduce P gain
   - **Wandering** (slow drift off course): Increase P gain
   - **Overshoot** (turns past target): Increase D gain

3. **Different Conditions**:
   - Test in calm water first
   - Progress to light chop, then moderate seas
   - Test in various wind conditions
   - Document settings that work for each condition

## Troubleshooting

### "Externally Managed Environment" Error

If you see this error when trying to use `pip install`:

```
error: externally-managed-environment
```

**Solution**: Use `pipx` instead of `pip` for installing applications:
```bash
# Wrong:
pip3 install pypilot

# Correct:
pipx install pypilot
```

### Web Interface Not Loading

```bash
# Verify Pi is on network
ping 192.168.20.101

# Check web service status
ssh bbb@192.168.20.101
sudo systemctl status pypilot_web.service

# Check if web service is listening
sudo netstat -tlnp | grep 80

# View logs
sudo journalctl -u pypilot_web.service -f
```

### "No Motor Controller" Error

```bash
# Check USB connection
ls /dev/ttyUSB* /dev/ttyACM*

# Check if Arduino is detected
dmesg | tail -20

# Verify permissions
sudo usermod -a -G dialout bbb

# Check pypilot logs
sudo journalctl -u pypilot.service | grep -i motor
```

### IMU Not Detected

```bash
# Verify I2C is enabled
lsmod | grep i2c

# Check I2C devices
sudo i2cdetect -y 1

# Check wiring:
# - 3.3V on Pin 1 or 17
# - GND on Pin 6, 9, 14, etc.
# - SDA on Pin 3 (GPIO 2)
# - SCL on Pin 5 (GPIO 3)

# Verify I2C bus speed (should be 100kHz or 400kHz)
sudo nano /boot/config.txt
# Look for: dtparam=i2c_arm=on,i2c_arm_baudrate=100000
```

### Erratic Compass Readings

**Causes**:
- IMU too close to high-current motor wires
- IMU near magnetic materials (engine, steel fittings)
- Poor I2C wiring (long wires, no shielding)
- Vibration from pump/engine

**Solutions**:
- Move Pi/IMU away from motor controller and pump
- Use shorter, twisted pair wires for I2C
- Add vibration damping under Pi mounting
- Re-run compass calibration

### Pypilot Service Won't Start

```bash
# Check service status
sudo systemctl status pypilot.service

# View detailed logs
sudo journalctl -u pypilot.service -n 50

# Try running manually
~/.local/bin/pypilot

# Check pypilot installation
pipx list
```

### Power Issues (Random Reboots)

**Symptoms**: Pi reboots unexpectedly, especially when pump engages

**Solutions**:
1. Check buck converter output with multimeter under load
2. Ensure buck converter can supply 2A continuous
3. Add capacitor (1000µF, 16V) across buck converter output
4. Verify all power connections are tight
5. Check for voltage drops in 12V supply wiring
6. Consider larger gauge wire (16 AWG) if voltage drop detected

## Backup and Recovery

See [Backup and Recovery](./backup_and_recovery.md) for SD card imaging procedures.

**Quick backup**:
```bash
# From another Linux system with SD card reader
sudo dd if=/dev/sdX of=tinypilot-backup-$(date +%Y%m%d).img bs=4M status=progress
gzip tinypilot-backup-*.img
```

**Prepare spare SD card**:
1. Image new card with Raspberry Pi OS Lite
2. Follow installation steps above
3. Configure static IP `192.168.20.101`
4. Label card "TinyPilot Spare - .101"
5. Test boot and network connectivity
6. Store in waterproof case

## References

- [Pypilot GitHub](https://github.com/pypilot/pypilot)
- [Pypilot Data GitHub](https://github.com/pypilot/pypilot_data)
- [Pypilot Documentation](https://pypilot.org/)
- [Flashing Arduino Firmware](./flashing_motor_ino_to_arduino.md)
- [Testing and Tuning Guide](./testing_and_tuning.md)
- [Hardware Review](./hardware_review.md)
- [Network Map](./network_map.md)
- [12V Solar System](./12v_solar_system.md)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [Button Control Setup](./button_control.md)
