# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a fork of the open-source [pypilot](https://github.com/pypilot/pypilot) autopilot (GPLv3, by Sean D'Epagnier), customized for SY Arion — a 36ft pilothouse yacht. Most Python source files are upstream pypilot code. Arion-specific work lives in `docs/`, `scripts/`, and the locally-modified `arduino/motor/` firmware.

**Three-node architecture:**
- **Steering Node (Pi 3B, 192.168.20.100):** pypilot server, ICM-20948 IMU, USB GPS, Arduino Nano motor controller via `/dev/ttyUSB0`
- **Hub Node (Pi 4, 192.168.20.101):** Signal K, InfluxDB, Grafana, OpenCPN
- **Wind Bridge (Pi Zero WX):** Ecowit WS80 ultrasonic wind sensor via rtl_433 → MQTT → Signal K

## Build & Install

### Python (pypilot) — runs on Raspberry Pi

```bash
# Check/install dependencies
python3 dependencies.py

# Build C extensions (linebuffer, arduino_servo, ugfx — uses SWIG)
python3 setup.py build_ext

# Install system-wide
sudo python3 setup.py install
```

Build requires: `python3-dev`, `swig`, `libpython3-dev`, `python3-numpy`, `python3-scipy`, and RTIMULib2 (installed via `scripts/install_rtimulib.sh`).

### Arduino firmware

```bash
# Using Arduino IDE (recommended for clones):
# Board: Arduino Nano, Processor: ATmega328P (Old Bootloader), Port: /dev/ttyUSB0

# Using Makefile (requires arduino 1.8.x at /usr/share/arduino):
cd arduino/motor
make           # compile
make upload    # flash via /dev/ttyAMA0 (edit DEVICE= for USB)
make serial    # monitor serial output at 38400 baud
```

## Running Services

```bash
# Systemd services (on Pi 3B):
sudo systemctl start pypilot          # Full autopilot (autopilot + IMU + servo)
sudo systemctl start pypilot_boatimu  # IMU-only mode (conflicts with pypilot)

# Run directly (for debugging):
pypilot                  # Main autopilot
pypilot_boatimu          # IMU subsystem
pypilot_servo            # Servo/motor controller
pypilot_web              # Web UI (port varies)
pypilot_client           # CLI client
```

## Testing the Motor Controller

```bash
# Listen to raw Arduino serial telemetry:
python3 arduino/motor/tests/nano_test.py   # /dev/ttyUSB0 @ 38400

# Full motor engagement test:
python3 arduino/motor/tests/test_engage.py

# Keep-alive test:
python3 arduino/motor/tests/keep_alive.py

# Servo test mode built into pypilot:
python3 -m pypilot.servo -t /dev/ttyUSB0
```

## Architecture

### pypilot/ — Core Autopilot (upstream)
- `autopilot.py` — Main process: orchestrates IMU, pilots, servo, sensors. See below.
- `server.py` / `client.py` — pypilot's own internal pub/sub bus (not Signal K). See below.
- `boatimu.py` — IMU driver (RTIMULib2); ICM-20948 on I2C @ 0x68
- `servo.py` — Motor controller abstraction; handles Arduino serial protocol, current/temp limits, slew rates
- `sensors.py` — Aggregates GPS, wind, AIS, NMEA inputs
- `signalk.py` — Bridges pypilot ↔ Signal K; acts as a pypilot client while connecting outward to the Signal K server on the Pi 4
- `pilots/` — Pluggable pilot algorithms: `basic`, `simple`, `wind`, `gps`, `vmg`, `fuzzy`, `learning`, `autotune`

### autopilot.py — The Main Loop

Subsystems are constructed in dependency order, all sharing one `client` pipe to the server:

```
pypilotServer → pypilotClient → BoatIMU(client)
                              → Sensors(client, boatimu)
                              → Servo(client, sensors)
```

After init, the main process requests realtime scheduling (`SCHED_FIFO priority 1`) to reduce servo latency.

`iteration()` runs at ~10 Hz, gated by IMU availability:

```
1. server.poll()                     flush server subprocess (no-op if multiprocessed)
2. client.receive()                  drain messages from server bus
3. sensors.poll()                    read GPS, NMEA, Signal K, wind
4. boatimu.read()                    block-wait up to 14×(period/10) for fresh IMU data
                                     ← the main timing gate; everything waits on the IMU
5. fix_compass_calibration_change()  adjust heading_command if IMU recalibrated mid-flight
6. compute_offsets()                 update GPS/wind/true-wind compass offset filters
7. pilot.compute_heading()           active pilot computes heading reference for current mode
8. compute_heading_error()           error = heading − heading_command (sign reversed for wind)
                                     also integrates error for the I gain term
9. tack.process()                    if tacking, override pilot; else pilot.process() → servo cmd
10. servo.poll()                     send command to Arduino (only when ap.enabled)
11. boatimu.poll()                   run IMU calibration (deferred until after critical path)
12. tack.poll()                      update tack state machine
```

**Key behaviours to know:**

- **`enabled` splits the loop.** In standby, `servo.poll()` runs before sensors (step 3 position) for lower-latency manual steering response. When enabled it runs after the full pilot calculation (step 10).
- **Compass recalibration mid-flight.** `fix_compass_calibration_change()` detects IMU recalibration and adjusts `heading_command` to compensate, so the actual course held doesn't change.
- **I-windup prevention.** `heading_error_int` is actively decayed when `heading_command_rate` is non-zero, preventing accumulated error from the old heading from pushing the rudder after a course change.
- **Timing is instrumented.** `ap.timings` publishes `[t1-t0, t2-t1, t3-t2, t4-t3, t5-t4, total]` every tick, visible in `pypilot_scope`. Each phase prints a warning if it exceeds `period/2`.

### server.py / client.py — pypilot's Internal Pub/Sub Bus

These implement pypilot's own named-value pub/sub protocol on **TCP port 23322** — separate from Signal K. The design serves double duty:

**Internal (subprocess) communication:** `pypilotServer` runs in its own process (`use_multiprocessing = True`). Subsystems (`autopilot`, `boatimu`, `servo`) connect via `NonBlockingPipe` — fast in-memory channels created before the server starts, bypassing TCP entirely.

**External TCP interface:** The same server accepts TCP connections from the web UI, desktop clients (`pypilot_control`, `pypilot_calibration`), the hat keypad, and `signalk.py`. Protocol is line-delimited JSON: `name=value\n`. Clients call `watch` with a period (seconds) to subscribe; `False` unsubscribes.

```
boatimu ──pipe──┐
servo   ──pipe──┤  pypilotServer           ┌── web UI (TCP 23322)
pilots  ──pipe──┤  (port 23322)  ──────────┤── hat interface (TCP)
                └────────────────           ├── pypilot_client (TCP)
                                            └── signalk.py (TCP) ──► Signal K (Pi 4)
```

Persistent state is stored to `~/.pypilot/pypilot.conf` every 60 seconds and watched via `inotify` so external edits are hot-reloaded.

### arduino/motor/ — Motor Controller Firmware (locally modified)
Configuration is in `config.h` (not hardware jumpers — this is the modified version). Key hardware wiring:
- D9 → IBT-2 RPWM, D10 → LPWM
- **D6 must be grounded** to select H-bridge mode (IBT-2); floating = RC servo PWM mode
- Serial protocol: 4-byte packets (cmd, val_lo, val_hi, CRC8)
- Default baud: 38400 × DIV_CLOCK (DIV_CLOCK=4 → 153600); pypilot `servo.baud` must match

### web/ — Web Browser Interface (active)
Flask + gevent-websocket + flask-socketio server. Served by `pypilot_web` on the Pi 3B. Accessed at `192.168.20.100:8000` from any device on the YachtArion network. This is the primary way to monitor and control pypilot on Arion.

### scripts/
- `scripts/debian/` — Systemd unit files and config for Raspbian deployment
- `scripts/getBME680data.py` — BME680 cabin sensor → MQTT (topic: `arion/sensors/cabin/bme680`)
- `scripts/gpsdate.py` / `gpsprobe.py` — GPS utilities

### hat/ — NOT USED on Arion (upstream only)
SPI LCD + button keypad interface using `ugfx` C extension (requires wiringPi). ESP32 variant in `*_esp32.py` files. Carried from upstream but no hat hardware is installed on Arion.

### ui/ — NOT USED on Arion (upstream only)
wxPython-based desktop tools: `autopilot_control.py`, `autopilot_calibration.py`, `scope_wx.py`. Carried from upstream; the web interface is used instead for all monitoring and control.

## Key Configuration

Pypilot stores runtime config in `~/.pypilot/`. Servo parameters set via client or Signal K:

```python
servo.controller = 'arduino'
servo.device = '/dev/ttyUSB0'
servo.baud = 153600          # DIV_CLOCK=4
servo.max_current = 1500     # 15A (units: ×10mA)
servo.max_controller_temp = 6000  # 60°C (units: 0.01°C)
```

## Critical Hardware Notes

- **D6 must be grounded** on the Arduino Nano for IBT-2 H-bridge mode. Floating = RC servo output (won't drive pump).
- **BOD fuses** on ATmega328P must be set (`efuse: 0x04`) to prevent flash corruption in marine power environments.
- **Baud rate mismatch** (pypilot `servo.baud` vs DIV_CLOCK in firmware) is the most common cause of silent motor failure.
- IMU calibration is stored persistently; re-calibrate after any physical relocation of the Pi 3B.
