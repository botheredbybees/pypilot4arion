# Pypilot for Arion

Open-source autopilot and integrated marine data network for the 36ft yacht Arion. This README describes the current installation (Tri‑Pi architecture) and retains the detailed wiring, motor controller, and installation guidance from the prior version while adding the updated setup: the Pi 3B now runs the latest Raspbian with a compiled pypilot (not OpenPlotter). It also documents the current 12V → USB cigarette-plug style power supplies in use and the recommended power-stability precautions.

Last Updated: 2026-03-21  
Maintainer: Peter Shanks (botheredbybees)  
Location: Cygnet, Tasmania, Australia

---

## Project Overview

This project retrofits a modern pypilot-based autopilot into SY Arion (36ft) replacing a failed TQM AP8 relay-based system with a solid-state solution using:

- Arduino Nano running motor.ino (motor driver, safety monitoring)
- IBT-2 (dual BTS7960B) H-bridge motor driver
- Octopus Model 1012 hydraulic pump (12V reversible motor)
- Pypilot autopilot server on Raspberry Pi 3B (latest Raspbian, compiled from source)
- Raspberry Pi 4 acting as Navigation/Hub (Signal K, InfluxDB, Grafana, OpenCPN)
- Raspberry Pi Zero WX as Wind Bridge for Ecowit WS80 via rtl_433 → Signal K

Design goal: separate responsibilities across three nodes so navigation or sensor failures do not affect core steering reliability.

---

## High-level Architecture

- Steering Node (Pi 3B): pypilot server, IMU, local USB GPS, serial to Arduino motor controller.
- Analysis / Hub Node (Pi 4): Signal K master, InfluxDB, Grafana, OpenCPN charting, rtl_433 or MQTT bridges.
- Wind Bridge (Pi Zero WX): solar-powered remote node for Ecowit WS80, rtl_433 → MQTT/Signal K.

Network:
- SSID: YachtArion (EZR23 4G Router or equivalent)
- Pi 4 (Hub): 192.168.20.101
- Pi 3B (Pilot): 192.168.20.100
- Pi Zero (Wind): client to Hub (MQTT/Signal K)

---

## Important: Power and IMU stability

You are using 12V → USB cigarette-plug style power supplies for the Pi 4 and Pi 3B. These are convenient but vary widely in quality.

Recommendations and cautions:
- IMU noise/false outputs and CPU throttling are commonly caused by voltage droop or noisy 5V rails. A high-quality DC‑DC converter (buck) with adequate current rating and low output ripple is strongly preferred for the Pi 3B IMU/Steering node.
- If using cigarette-plug USB supplies:
  - Choose units rated for >3A with low-voltage-drop cables and reputable brands.
  - Prefer 12V→5V USB adapters that specify stable output under transient loads.
  - Keep USB cable lengths short; use quality shielded cables.
  - Ensure a common chassis/ground between IBT-2 battery ground and Pi grounds.
  - Add a small LC/R-C filter or ferrite on the IMU/I2C power lines if you see noise.
  - If you observe IMU anomalies (heading jumps, poor calibration), switch the Pi 3B supply to a dedicated buck converter or an isolated 5V regulator and re-check.
- Always fuse the IBT-2 main supply (30A inline fuse close to battery) regardless of the Pi supply method.

(If you want, I can add a short recommended parts list of proven 12V→5V converters and USB adapters.)

---

## Technology Stack — Hardware (detailed)

### Steering Node (Pi 3B; now Raspbian + compiled pypilot)
- Raspberry Pi 3B running latest Raspbian (Bullseye/Bookworm as appropriate). Pypilot compiled from source for better integration and performance.
- IMU: ICM-20948 (I2C @ 0x68) connected directly to Pi GPIO (3.3V).
- Motor controller: Arduino Nano (motor.ino).
- H-Bridge driver: IBT-2 (BTS7960B) driving Octopus 1012 hydraulic pump.
- USB GPS: NMEA 0183 (local USB connected to Pi 3B).
- Power: 12V ship supply → 12V→USB adapter for Pi (see power notes above) OR dedicated buck converter for best stability.

### Hub / Analysis Node (Pi 4)
- Raspberry Pi 4 (8GB), 512GB SSD (InfluxDB writes), Argon ONE V2 case.
- Lysmarine / OpenCPN / Signal K / Grafana stack. RTL-SDR + rtl_433 for wireless sensors (WS80), or run rtl_433 on Wind Bridge.

### Wind Bridge (Pi Zero WX)
- Pi Zero WX (solar remote).
- Ecowit WS80 ultrasonic sensor via 433MHz RF decoded by rtl_433 → MQTT / Signal K.

---

## Software (summary + Pi 3B changes)

- Pypilot: compiled from source and run as a systemd service on Pi 3B (replaces the prior OpenPlotter-based flow).
  - Benefits: lighter image footprint, direct control, easier dependency management for a compiled pypilot version tailored to the Pi 3B.
  - Typical compile/install steps (summary):
    1. Install prerequisites (python3-dev, libboost, libprotobuf, cmake, git, etc.).
    2. Clone pypilot upstream and build per pypilot build docs (cmake/make or pip wheel if available).
    3. Install systemd unit to run pypilot at boot and enable on startup.
    4. Configure pypilot to use /dev/ttyUSB0 for motor controller and to serve on TCP 20220.
- Signal K: master server on Pi 4; derived-data plugin for ground/true wind calculations.
- InfluxDB 1.8 + Grafana: data logging and dashboards.
- rtl_433: for Ecowit WS80 on Pi Zero or Pi 4.

Notes retained from previous documentation: all low-level motor.ino, wiring, serial protocol, and safety logic remain unchanged — see the detailed sections below.

---

## Motor Controller (Arduino motor.ino) — wiring and configuration

### IBT-2 (Arduino → IBT-2)
- D9 (PWM) → RPWM (IBT-2 pin 1)
- D10 (PWM) → LPWM (IBT-2 pin 2)
- D2 → R_EN (pin 3)
- D3 → L_EN (pin 4)
- A1 → R_IS (pin 5) (current sense), optionally tie L_IS to R_IS
- Arduino 5V → IBT-2 Vcc or use separate regulated 5V if Arduino USB power insufficient
- GND common between Arduino, Pi, and IBT-2

### Hardware configuration pins (set at boot)
- D4: shunt resistance detection (floating → 0.05Ω)
- D5: low/high current mode (floating → low 20A)
- D6: pwm_style select — GROUND for H‑bridge (IBT-2/hydraulic) mode (pwm_style=0)
- D7 / D8: optional limit switches for port/starboard
- D12: voltage sense mode (floating = 12V mode)
- D13: status LED

### Sensor inputs
- A0: voltage sense (voltage divider)
- A1: current sense (IBT-2 R_IS)
- A2: controller temp (NTC)
- A3: motor temp (optional)
- A4: rudder feedback (potentiometer), optional

### Pi 3B connection
- USB connection to Arduino appears as /dev/ttyUSB0
- Baud: 38400 × DIV_CLOCK (typical DIV_CLOCK=4 → 153600). Ensure pypilot servo.baud matches.

### Serial protocol (motor.ino)
- 4-byte commands:
  - Byte 0: command code (e.g., 0xC7 motor command)
  - Byte 1: low byte of value
  - Byte 2: high byte of value
  - Byte 3: CRC8 over bytes 0–2
- Common commands: motor command, disengage, set max current, set temperature limits, set slew rates, reset.
- Telemetry frames: current, voltage, controller temp, motor temp, rudder position, status flags.

---

## Pypilot / Servo configuration (example)

servo.controller = 'arduino'  
servo.device = '/dev/ttyUSB0'  
servo.baud = 153600  # For DIV_CLOCK=4  
servo.max_current = 1500  # 15A (units ×10mA)  
servo.max_controller_temp = 6000  # 60°C (units 0.01°C)  
servo.max_motor_temp = 7000  
servo.max_slew_speed = 15  
servo.max_slew_slow = 5  
# Rudder feedback if installed:
# servo.rudder_min / servo.rudder_max — calibrate ADC endpoints

---

## Installation Overview (phased, retaining detailed steps)

### Phase 0 — Pi 3B: Raspbian + compiled pypilot (updated)
- Flash Raspbian image (latest recommended).
- Install build dependencies (python3-dev, pip, setuptools, cmake, libusb, protobuf dev packages, etc.).
- Clone pypilot and compile/install per upstream instructions (or build wheel and pip install).
- Create and enable a systemd service for pypilot (ensure it starts after network-online.target if needed).
- Configure pypilot to use /dev/ttyUSB0, correct baud, and ensure the Arduino motor.ino is running.

(If you want, I can paste an example systemd unit and build commands.)

### Phase 1 — Legacy hardware removal & preparation
- Remove TQM AP8 and relay H-bridge; tidy wiring.
- Bench-test Octopus pump on 12V; measure current and verify smooth motion.

### Phase 2 — Arduino motor controller setup
- Flash motor.ino to Arduino Nano (Arduino IDE or Makefile).
- Ground D6 permanently for H‑bridge mode.
- Wire PWM and direction pins to IBT-2 as above.
- Verify brownout fuse/resets if required for ATmega328P.

### Phase 3 — IBT-2 and pump wiring
- Mount IBT-2 near pump, use 10–12 AWG motor power wiring.
- B+ → battery through 30A inline fuse (close to battery).
- B- → common ground.
- Bench test forward/reverse with Arduino commands before ship installation.

### Phase 4 — Pi hardware & sensors
- Mount Pi 3B close to IMU location, away from high-current cables.
- Connect ICM-20948 (3.3V, SDA → GPIO2, SCL → GPIO3), keep wires <15 cm where possible.
- Connect USB GPS and Arduino to Pi 3B.

### Phase 5 — Software tuning & calibration
- Start pypilot, calibrate IMU (compass/level), configure servo and motor parameters, tune PID in calm conditions, then progressively validate sailing behavior.

### Phase 6 — Logging & dashboards
- Configure Signal K on Pi 4 to receive pypilot data.
- Configure InfluxDB retention policy:
  CREATE RETENTION POLICY "one_year" ON "signalk" DURATION 52w REPLICATION 1 DEFAULT
- Configure Grafana dashboards for wind triangles, system health, and WS80 metrics.

---

## Testing, safety, and operational notes

- Arduino enforces current, voltage, and temperature safety limits and will disengage on fault flags.
- Always bench-test the motor + IBT-2 + Arduino before connecting to the vessel hydraulic system.
- Ensure common ground across battery, IBT-2, Arduino, and Pi to avoid stray voltages on serial lines.
- Use the 30A inline fuse on IBT-2 positive near the battery regardless of Pi supply method.
- If you see IMU errors after switching to cigarette-plug USB adapters, try swapping to a dedicated buck converter for the Pi 3B — IMU stability is critical to safe autopilot operation.
- Watchdog timer resets exist in motor.ino to recover from firmware hangs.

---

## Wiring reference & pin tables (retained)

(See the full pin tables, wiring diagrams, and sample voltage-divider / NTC circuits in the repository docs: /docs/ and /hardware/ — these files include full tables for Arduino pins, IMU wiring, and IBT-2 connections.)

Key highlights preserved:
- D6 grounded = H-bridge mode
- D9 = RPWM, D10 = LPWM
- D2/D3 = direction/enables
- A1 = IBT-2 current sense
- A4 = optional rudder pot

---

## Repository contents (high level)

- /docs/ — flashing_motor_ino_to_arduino.md, openplotter_setup.md (kept for reference), testing_and_tuning.md, wind_sensor_integration.md, etc.
- /arduino/motor/ — motor.ino, crc.h, Makefile
- /config/ — sample pypilot config
- /scripts/ — diagnostics utilities
- /hardware/ — wiring and datasheets
- /calibration/ — PID tuning and calibration logs

Note: openplotter_setup.md remains in /docs for historical reference, but the current Steering Node workflow uses Raspbian + compiled pypilot. The Navigation/HUB node may still run Lysmarine / OpenPlotter style setups if you prefer.

---

## Bill of Materials (core)

- Raspberry Pi 3B (pilot)  
- ICM-20948 IMU  
- Raspberry Pi 4 (hub) + Argon ONE V2 + 512GB SSD  
- Raspberry Pi Zero WX (wind)  
- Arduino Nano (CH340 clone common)  
- IBT-2 (BTS7960B) motor driver  
- Octopus Model 1012 hydraulic pump (12V)  
- USB GPS (NMEA)  
- 30A inline fuse, 10–12 AWG power cables, voltage divider components, NTC thermistors, rudder pot (optional)

---

## Performance expectations

- Heading hold: ±2–5° (depends on sea state and tuning)
- Control loop: ~10 Hz pypilot
- IMU update: 10–20 Hz
- Typical steering power draw: 4–6A active, peaks near 19A (pump dependent)
- Pi 3B/4 standby: ~5–8W each; Pi 3B + Arduino + GPS ~7–9W

---

## Alternative configurations / notes

- Pi Zero W trial documented in docs/tinypilot_setup.md — not recommended for production due to CPU and environment complexity. Retained for reference.

---

## Resources & Links

- Pypilot upstream and motor.ino: https://github.com/pypilot/pypilot (arduino/motor)
- motor.ino README and build notes in /docs/
- IBT-2 / BTS7960B datasheets and references (links in /docs/hardware_review.md)
- OpenPlotter and Lysmarine docs (kept for Hub/reference uses)

---

## License & Acknowledgments

- Documentation: MIT License  
- Pypilot and motor.ino: GPLv3
- Thanks to Sean d'Epagnier (pypilot, motor.ino), OpenMarine community, and contributors.

---

Project status: Hardware installation and initial testing phase (March 2026)  
Maintainer: Peter Shanks (botheredbybees) — Cygnet, Tasmania, Australia

---

If you want:
- I can insert the exact compile/build commands and a sample systemd unit for compiled pypilot on the Pi 3B.
- I can produce a short changelog that lists what changed from HEAD~1 → HEAD → this merged README.
- I can prepare this README as a branch commit in the repo (Option B) if you'd like me to push it.