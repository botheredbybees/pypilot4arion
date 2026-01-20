# TinyPilot Setup & Configuration

## Overview

**TinyPilot** is the minimal, robust operating system that runs the core pypilot autopilot software. It is designed to run on a Raspberry Pi Zero W (or similar) from RAM, making it extremely resilient to power failures and corruption.

On *Arion*, the TinyPilot Pi Zero W acts as the **Autopilot Core**. It handles:
1.  Reading sensors (IMU, optional GPS, Rudder Feedback).
2.  Running the PID control loop.
3.  Sending drive commands to the motor controller.

It functions independently of the navigation computer (Lysmarine Pi 4), ensuring you still have steering even if the main computer fails.

## Core Logic & Functionality

The TinyPilot system operates on a continuous control loop (typically 10-20Hz):

1.  **State Estimation**: Reads the Inertial Measurement Unit (IMU) to determine current Heading, Pitch, Roll, and Rate of Turn.
2.  **Error Calculation**: Compares current Heading vs. Target Heading to calculate the "Heading Error".
3.  **PID Control**: A Proportional-Integral-Derivative (PID) controller processes this error to determine the required rudder correction.
    *   *Proportional*: "We are 10° off, turn rudder 10°."
    *   *Integral*: "We have been 2° off for a long time, add more rudder slowly."
    *   *Derivative*: "We are turning too fast, counter-steer to stop the swing."
4.  **Output Generation**: Converts the desired rudder angle into a command for the motor controller (PWM signal or serial command).

### Power Architecture
The TinyPilot Pi Zero is powered via a **24V to 5V Buck Converter** connected to the 24V House Bank (or 12V supply if separate). This ensures stable 5V power even when the main engine cranks or heavy loads dip the battery voltage.

> [!IMPORTANT]
> **Power Stability**: The 24V->5V converter must supply at least 2A continuously. Poor power supplies are the #1 cause of random autopilot disconnects.

## Installation Hardware Setup

### Required Components
*   Raspberry Pi Zero W (or Zero 2 W).
*   MicroSD Card (8GB+).
*   **Pypilot HAT** or manual wiring for:
    *   IMU (MPU9250 or ICM20948) via I2C.
    *   Motor Controller connection (UART or PWM).
    *   IR Receiver (optional).
*   **24V to 5V Buck Converter** (e.g., LM2596 HV module or dedicated USB weatherproof supply).

### Wiring the Power Supply
1.  **Input**: Connect the **24V House Bank** (+ and -) to the input of your 24V->5V Buck Converter.
    *   *Fuse*: Install a 2A-5A fuse on the 24V positive line near the battery.
2.  **Output**: Connect the 5V output to the Raspberry Pi:
    *   *Via MicroUSB*: Easiest, uses standard cable.
    *   *Via GPIO*: Connect 5V to Pin 2/4 and GND to Pin 6. **Warning: No fuse protection on GPIO power input.**

[See System Diagram in README](../README.md#network-topology)

## Software Installation

1.  **Download Image**: Get the latest `tinypilot` image from [pypilot.org](https://pypilot.org).
2.  **Flash SD Card**: Use BalenaEtcher or Raspberry Pi Imager to flash the `.img` file to your MicroSD card.
3.  **Boot**: Insert card into Pi Zero W and power up.
4.  **Connect**:
    *   TinyPilot creates a WiFi Hotspot named `pypilot` by default.
    *   Connect your phone/laptop to this network.
    *   Open browser to `http://192.168.14.1` (or `pypilot.local`).

### Connecting to Main Network
To make TinyPilot join your main *YachtArion* network (Pixel 2 Hotspot):
1.  Go to **Configuration -> WiFi**.
2.  Select Client Mode.
3.  Enter SSID: `YachtArion` and Password.
4.  Reboot. The Pi should now appear on the main network (e.g., `192.168.43.101`).

## Configuration

### 1. Motor Controller Setup
TinyPilot communicates with your Arduino-based motor controller.

*   **Firmware**: Ensure your Arduino is flashed with `motor.ino`.
    *   👉 **[Guide: Flashing motor.ino to Arduino](flashing_motor_ino_to_arduino.md)**
*   **Connection**: Connect the Arduino via USB to the Pi Zero W.
*   **TinyPilot Settings**:
    1.  Go to **Configuration -> Servo**.
    2.  Sets `Driver` to `Arduino`.
    3.  TinyPilot should auto-detect the serial port (e.g., `/dev/ttyUSB0`).

### 2. IMU Calibration
The compass must be calibrated to your boat's magnetic environment.
1.  Go to **Configuration -> Calibration**.
2.  **Level**: With boat at rest in calm water, click "Level" to zero pitch/roll.
3.  **Compass**: Click "Calibration". Only needs to be done once.
    *   drive the boat in slow circles.
    *   Ideally do a "figure 8" or turn 360° slowly.
    *   Watch the "Scope" plot until the 2D plot looks like a circle, not an oval.

## Testing

Complete testing and tuning procedures are detailed in a separate comprehensive guide:

**[→ Testing and Tuning Guide](testing_and_tuning.md)**

### Dockside Test
1.  **Manual Control**:
    *   Open the Web UI (`http://192.168.43.101`).
    *   Click arrows left/right (Port/Starboard).
    *   **Verify**: Does the rudder move? Does it move in the *correct* direction?
        *   *If reversed*: Invert the motor wires or use the "Invert Motor" setting in config.
2.  **Endstops**:
    *   Command hard over. confirm the rudder stops before hitting mechanical limits (if rudder feedback is installed and calibrated).

### Sea Trial
1.  **Compass Mode**:
    *   Steer manually to a safe heading.
    *   Engage "Auto" (Compass mode).
    *   Verify the boat holds course.
    *   *Tuning*: If it zig-zags (oscillates), reduce `P` gain. If it wanders off course, increase `P` gain.

## Troubleshooting

*   **Web UI not loading**: Check WiFi connection. Try accessing via IP address.
*   **"No Motor Controller"**: Check USB cable to Arduino. Check `dmesg` on Pi Zero to see if Arduino is detected.
*   **Erratic Compass**: IMU might be too close to power cables or the motor itself. Move Pi Zero away from high-current wires.

---

**Next Steps**:
*   [Flash Arduino Firmware](flashing_motor_ino_to_arduino.md)
*   [Review System Architecture](../README.md)
