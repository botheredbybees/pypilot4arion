
# Pypilot for Arion

Open-source autopilot retrofit for 36ft yacht *Arion* using pypilot with hydraulic steering, Arduino motor controller, IBT-2 H-bridge, and Octopus Model 1012 hydraulic pump.

## Project Overview

This project documents the installation and configuration of a pypilot-based autopilot system on *Arion*, a 36-foot sailboat with existing hydraulic steering. The installation **replaces a non-functional TQM AP8 autopilot** (removing the relay-based H-bridge control system) with a modern solid-state system using:

- **Arduino Nano** running pypilot's motor.ino firmware for motor control
- **IBT-2 motor controller** with dual BTS7960B H-bridge chips
- **Octopus Model 1012 hydraulic pump** (12V DC reversible motor)

The system uses a dual-Raspberry Pi architecture combining reliability and functionality:
- **Tinypilot** on Raspberry Pi Zero W for dedicated autopilot control
- **Lysmarine** on Raspberry Pi 4 (8GB) for navigation, chartplotting, and marine data integration

## Technology Stack

### Hardware

#### Autopilot System (Tinypilot)
- **Computer**: Raspberry Pi Zero W
- **Operating System**: Tinypilot (TinyCore Linux-based, runs from RAM)
- **IMU**: Pypilot IMU with compass, gyroscope, and accelerometer
- **Motor Controller**: Arduino Nano running motor.ino firmware
  - Communicates with Pi Zero via USB serial (38400 × DIV_CLOCK baud)
  - Monitors voltage, current, temperature, and fault conditions
  - Provides safety features (over-current, over-temp, brownout detection)
  - Outputs PWM signals to IBT-2 H-bridge driver
- **H-Bridge Driver**: IBT-2 with dual BTS7960B chips
  - Continuous current: 43A per channel
  - Operating voltage: 5.5-27V (12V nominal for marine use)
  - PWM frequency: Up to 25kHz
  - Receives PWM from Arduino (D9, D10) and direction control (D2, D3)
  - Provides current sense feedback to Arduino (A1)
  - Integrated thermal protection
- **Hydraulic Pump**: Octopus Model 1012 (12V DC, 1000cc/min, retained from original installation)
  - Current draw: 4-6A average, 19A max
  - Two-wire reversible DC motor (polarity reversal for direction)
- **GPS Receiver**: USB GPS (NMEA 0183) connected directly to Pi Zero W for standalone GPS mode operation
- **Rudder Feedback**: Analog potentiometer or Hall effect sensor (optional, connects to Arduino A4)
- **Power**: 12V DC ship's power with 30A inline fuse protection

**Legacy Hardware Removed:**
- TQM AP8 autopilot control unit
- 4x 12V automotive relays (30-40A rated, used as H-bridge for pump motor polarity switching)
- Relay control wiring and driver circuits

#### Navigation System (Lysmarine)
- **Computer**: Raspberry Pi 4 (8GB RAM)
- **Case**: Argon ONE V2 Aluminium Case with passive cooling
- **Storage**: 512GB SSD
- **Operating System**: Lysmarine (BBN OS - Bareboat Necessities OS)
- **Display**: Compatible marine display or standard HDMI monitor
- **GPS**: Optional second GPS receiver for OpenCPN (NMEA 0183/2000 via USB or serial)
- **Wind Sensor** (planned future addition):
  - **Ecowit WS80** Ultrasonic 6-in-1 Sensor (Wind Speed/Direction, Solar Radiation, Light, Temperature, Humidity)
  - **RTL-SDR V3/V4 USB dongle** for 433MHz/915MHz reception
  - **rtl_433 software** for RF signal decoding
  - Integration via SignalK for apparent/true wind calculation

#### Network
- **WiFi Access Point**: [Google Pixel 2 Android phone mobile hotspot](docs/wireless_hotspot.md)
- **Network Architecture**: Both Raspberry Pis connect as WiFi clients to phone hotspot
- **IP Addressing**: Static DHCP reservation recommended (e.g., Pi4: 192.168.43.100, Pi Zero: 192.168.43.101)
- **Hotspot SSID**: "YachtArion" (configurable)
- **Phone Power**: DC-DC buck converter module (12V to 5V USB) for continuous ship's power

### Software

#### Core Autopilot
- **Pypilot**: Open-source marine autopilot software (https://pypilot.org)
- **Tinypilot**: Minimal, dedicated pypilot distribution running from RAM
- **Motor Controller Firmware**: motor.ino (Arduino-based pypilot motor driver)
  - Source: `arduino/motor/motor.ino` in pypilot repository
  - Compiled and uploaded to Arduino Nano via Arduino IDE
  - Configurable for H-bridge operation (pwm_style=0) or ESC/VNH2SP30 mode (pwm_style=2)
  - Supports current sensing, voltage monitoring, temperature sensing
  - Hardware configuration via GPIO pins (D4, D5, D6 set operating mode)
- **Control Modes**: 
  - Compass (magnetic heading) - **fully standalone, no network required**
  - GPS (track following) - **standalone with local GPS, no network required**
  - Wind (apparent wind angle) - requires wind sensor data (future)
  - True Wind (true wind angle) - requires GPS + wind data (future)
  - NAV (route following) - requires waypoint data from OpenCPN via network

#### Navigation & Integration
- **Lysmarine (BBN OS)**: Comprehensive marine computing platform
- **OpenCPN**: Electronic chart plotter and navigation software
- **SignalK**: Modern marine data server for sensor integration and data multiplexing
- **Pypilot OpenCPN Plugin**: Direct autopilot control and monitoring from OpenCPN
- **rtl_433**: Generic RF data receiver for 433MHz/915MHz ISM band sensors (future wind integration)
- **rtl_433 to SignalK bridge**: Converts decoded weather sensor data to SignalK format

#### Data Protocols
- **NMEA 0183**: GPS, wind, and sensor data (serial/USB on Pi Zero, TCP port 10110 over network)
- **Pypilot TCP Protocol**: Autopilot control and status (TCP port 20220)
- **Pypilot Serial Protocol**: Motor controller communication (38400 baud × DIV_CLOCK, USB serial)
- **SignalK WebSocket**: Real-time marine data distribution (TCP port 3000)
- **MQTT** (optional): Alternative data transport for rtl_433 sensor data

## System Architecture

### Network Topology

```
Pixel 2 Phone Hotspot (192.168.43.1)
         |
         |--- Raspberry Pi 4 (192.168.43.100)
         |    ├── Lysmarine OS
         |    ├── OpenCPN (chartplotter)
         |    ├── SignalK (data hub)
         |    ├── GPS receiver (optional) → NMEA data
         |    ├── RTL-SDR dongle + rtl_433 (future)
         |    │    └── Ecowit WS80 sensor (433/915MHz)
         |    └── Pypilot plugin (client)
         |
         └--- Raspberry Pi Zero W (192.168.43.101)
              ├── Tinypilot OS
              ├── Pypilot server (TCP 20220)
              ├── IMU (I2C)
              ├── GPS receiver (USB) → local NMEA for standalone GPS mode
              ├── Rudder feedback (optional, routed to Arduino)
              └── Arduino Nano (USB Serial, /dev/ttyUSB0)
                   ├── motor.ino firmware
                   ├── Pypilot serial protocol (4-byte packets with CRC8)
                   ├── Safety monitoring (voltage, current, temp)
                   ├── Fault detection (brownout, over-current, over-temp)
                   └── PWM generation for H-bridge control
                        |
                        └── IBT-2 H-Bridge (Solid-State PWM Control)
                             ├── RPWM (D9) ← Arduino PWM
                             ├── LPWM (D10) ← Arduino PWM  
                             ├── R_EN (D2) ← Arduino Direction
                             ├── L_EN (D3) ← Arduino Direction
                             ├── R_IS/L_IS → Arduino A1 (Current Sense)
                             └── Motor Output (+/-)
                                  |
                                  └── Octopus 1012 Hydraulic Pump (12V DC motor, 2 wires)
                                       |
                                       └── Hydraulic Steering Ram
```

### Motor Control Chain

**Pypilot → Arduino → IBT-2 → Hydraulic Pump**

1. **Pypilot** calculates steering correction based on IMU/GPS data
2. **Serial command** sent from Pi Zero to Arduino (USB serial, 4-byte packets)
3. **Arduino (motor.ino)** processes command:
   - Validates packet CRC8 checksum
   - Monitors safety limits (current, voltage, temperature)
   - Applies slew rate limiting for smooth rudder movement
   - Generates appropriate PWM signals for IBT-2
4. **IBT-2** receives PWM and drives hydraulic pump motor:
   - Forward: D9 (RPWM) active, D10 (LPWM) low, D2 high, D3 low
   - Reverse: D10 (LPWM) active, D9 (RPWM) low, D3 high, D2 low
   - Stop/Brake: Both PWM low, optional brake mode
5. **Hydraulic pump** moves steering ram based on motor direction and speed
6. **Arduino telemetry** reports back to pypilot:
   - Motor current (from IBT-2 current sense)
   - Supply voltage
   - Controller and motor temperature (if sensors installed)
   - Rudder position (if feedback sensor installed)
   - Fault flags (sync, over-temp, over-current, bad voltage, rudder limits)

### Arduino motor.ino Wiring

```
Arduino Nano          IBT-2           Function
────────────          ─────           ────────
D9  (PWM)       →     RPWM (pin 1)    Right/Forward PWM signal
D10 (PWM)       →     LPWM (pin 2)    Left/Reverse PWM signal  
D2  (GPIO)      →     R_EN (pin 3)    Right enable/direction
D3  (GPIO)      →     L_EN (pin 4)    Left enable/direction
A1  (ADC)       ←     R_IS (pin 5)    Right current sense
                      L_IS (pin 6)    (tie to R_IS for single reading)
5V              →     Vcc (pin 7)     Logic power (can use Arduino 5V)
GND             →     GND (pin 8)     Common ground

# Hardware configuration pins (set at boot):
D4  ────────────      Shunt resistance select (floating = 0.05Ω)
D5  ────────────      Low/high current mode (floating = low, 20A max)
D6  ────────────      **GROUND THIS** for H-bridge mode (pwm_style=0)
D7  (GPIO INPUT)      Port fault switch (optional limit switch)
D8  (GPIO INPUT)      Starboard fault switch (optional limit switch)
D11 (GPIO OUT)        Clutch output (not used with IBT-2)
D12 (GPIO INPUT)      Voltage sense mode (floating = 12V mode)
D13 (LED)             Status LED (on when engaged)

# Sensor inputs:
A0  (ADC)       →     Voltage divider (560Ω + 10kΩ to GND) for battery voltage
A1  (ADC)       →     Current sense from IBT-2 (R_IS/L_IS)
A2  (ADC)       →     Controller temp (100kΩ to 5V + 10kΩ NTC to GND)
A3  (ADC)       →     Motor temp (100kΩ to 5V + 10kΩ NTC to GND) - optional
A4  (ADC)       →     Rudder feedback sensor (potentiometer) - optional
A5  (GPIO)            Clutch sense PWM (not used with IBT-2)

# Pi Zero connection:
USB ───────────       Mini-USB port on Arduino Nano
                      Appears as /dev/ttyUSB0 on Pi Zero
                      Baud: 38400 × DIV_CLOCK (typically 153600)
```

**IBT-2 to Hydraulic Pump:**
```
Motor+ (out)  →  Octopus 1012 motor terminal (polarity determines initial direction)
Motor- (out)  →  Octopus 1012 motor terminal (reverse polarity if wrong direction)
B+ (power in) →  12V ship's power (30A fused)
B- (power in) →  12V ground/negative bus
```

### motor.ino Control Modes

The Arduino firmware supports multiple control modes selected by D6 pin state:

| D6 Pin State | pwm_style | Mode | Application |
|--------------|-----------|------|-------------|
| **LOW (GND)** | **0** | **H-bridge** | **IBT-2, direct MOSFET control** |
| HIGH (pullup) | 1 | RC PWM servo | Standard RC ESC (1-2ms pulses) |
| (compiled) | 2 | VNH2SP30 | Specific motor driver IC |

**For IBT-2: Ground pin D6 permanently** to select H-bridge mode (pwm_style=0).

### Arduino Serial Protocol

Motor.ino uses a simple 4-byte packet protocol with CRC8 validation:

```
Byte 0: Command code (e.g., 0xC7 for COMMAND_CODE)
Byte 1: Value low byte
Byte 2: Value high byte  
Byte 3: CRC8 of bytes 0-2
```

**Common commands (from pypilot to Arduino):**
- `0xC7` COMMAND_CODE: Motor command (0-2000, 1000=stop)
- `0x68` DISENGAGE_CODE: Stop motor and disengage
- `0x1E` MAX_CURRENT_CODE: Set current limit (units of 10mA)
- `0xA4` MAX_CONTROLLER_TEMP_CODE: Set temp limit (units of 0.01°C)
- `0x71` MAX_SLEW_CODE: Set slew rate limits
- `0xE7` RESET_CODE: Reset fault flags

**Telemetry responses (from Arduino to pypilot):**
- `0x1C` CURRENT_CODE: Motor current reading
- `0xB3` VOLTAGE_CODE: Supply voltage
- `0xF9` CONTROLLER_TEMP_CODE: Controller temperature
- `0x48` MOTOR_TEMP_CODE: Motor temperature (if sensor installed)
- `0xA7` RUDDER_SENSE_CODE: Rudder position (if sensor installed)
- `0x8F` FLAGS_CODE: Status and fault flags

**Flag bits:**
- SYNC (1): Serial communication synchronized
- OVERTEMP_FAULT (2): Temperature exceeded limit
- OVERCURRENT_FAULT (4): Current exceeded limit
- ENGAGED (8): Motor controller engaged
- INVALID (16): Invalid packet received
- PORT_PIN_FAULT (32): Port limit switch triggered
- STARBOARD_PIN_FAULT (64): Starboard limit switch triggered
- BADVOLTAGE_FAULT (128): Voltage out of range (< 9V or > max_voltage)
- MIN_RUDDER_FAULT (256): Rudder at minimum limit
- MAX_RUDDER_FAULT (512): Rudder at maximum limit
- CURRENT_RANGE (1024): High current mode active
- BAD_FUSES (2048): ATmega328P fuses incorrectly programmed
- REBOOTED (32768): Arduino recently rebooted

### Data Flow

**GPS to Autopilot (Standalone Mode):**
1. USB GPS receiver connected directly to Pi Zero W USB port
2. Pypilot reads NMEA sentences from USB serial device (auto-detected at 4800 or 38400 baud)
3. Pypilot uses GPS data for GPS track mode **without requiring network or Pi 4**
4. Pi Zero operates fully standalone for both Compass and GPS modes

**Autopilot Control Loop:**
1. User sets heading via OpenCPN or Tinypilot web interface
2. Command sent to pypilot server (TCP 20220)
3. Pypilot reads IMU (compass heading, heel, pitch) at 10-20Hz
4. PID controller calculates steering correction
5. Pypilot sends 4-byte serial command to Arduino (command value 0-2000, 1000=stop)
6. Arduino validates CRC8, checks safety limits, applies slew rate
7. Arduino generates PWM on D9/D10 and sets direction on D2/D3
8. IBT-2 receives PWM and drives hydraulic pump motor bidirectionally
9. Hydraulic pressure moves steering ram
10. Arduino reads rudder feedback sensor (if installed) via A4
11. Arduino reports telemetry back to pypilot (current, voltage, temp, rudder position, flags)
12. Pypilot adjusts command to reach target rudder angle
13. Loop continues at 10Hz control frequency

**Status Monitoring:**
1. Pypilot broadcasts heading, rudder angle, autopilot mode, motor current
2. OpenCPN pypilot plugin displays real-time status and allows mode changes
3. SignalK distributes autopilot data to other marine instruments
4. Arduino monitors current from IBT-2 current sense and reports to pypilot
5. Arduino monitors battery voltage and temperature sensors
6. Arduino sets fault flags if limits exceeded (stops motor automatically)

## Key Features

### Reliability
- **Standalone Operation**: Tinypilot operates independently in Compass and GPS modes without network or Pi 4
- **Local GPS**: USB GPS connected directly to Pi Zero enables GPS track mode without network dependency
- **RAM-based OS**: Tinypilot runs entirely from RAM after boot—safe power disconnection, no SD card corruption
- **Dual-System Redundancy**: Navigation computer failure doesn't affect autopilot operation
- **Minimal Power**: Pi Zero + Arduino + USB GPS consumes ~5W for extended offshore passages
- **Hardware Safety**: Arduino monitors voltage, current, temperature with automatic fault shutdown
- **Brownout Protection**: ATmega328P fuse configuration enables brownout detector to prevent flash corruption
- **CRC8 Validation**: All serial commands validated to prevent random data from moving rudder
- **No Relay Wear**: Solid-state IBT-2 eliminates relay contact degradation and mechanical failure modes
- **Proportional Control**: PWM allows smooth, proportional steering response (not just on/off bang-bang)
- **Unlimited Switching**: MOSFETs have no wear limit unlike relay contacts (millions of operations)

### Safety
- **Network Independence**: Core steering function never depends on WiFi connectivity
- **Rudder Feedback**: Continuous position monitoring prevents rudder runaway (if sensor installed)
- **Current Limiting**: Arduino monitors pump load via IBT-2 current sense and detects stall/overload
- **Voltage Monitoring**: Arduino detects low battery (< 9V) or over-voltage and disengages
- **Thermal Protection**: Arduino monitors temperature sensors and stops if over-temp
- **BTS7960B Thermal Shutdown**: IBT-2 chips have integrated over-temperature protection
- **Manual Override**: Hydraulic steering allows instant manual override at helm
- **Fuse Protection**: 30A inline fuse protects against electrical faults and short circuits
- **Emergency Shutdown**: Software can disable motor via disengage command
- **Fault Switches**: Optional limit switches (D7/D8) provide hardware stop at rudder limits
- **No Contact Arcing**: Solid-state switching eliminates electrical arcing fire risk
- **Watchdog Timer**: Arduino watchdog resets if firmware hangs (0.25 second timeout)

### Flexibility
- **Multiple Control Interfaces**:
  - OpenCPN pypilot plugin (graphical, route integration)
  - Tinypilot web interface (http://192.168.43.101)
  - Optional RF remote control
  - Optional GPIO physical buttons
  - Optional IR remote
- **Multiple Heading Modes**: Compass, GPS track, Wind angle, True wind, Route following (NAV)
- **Tack/Jibe Commands**: Automated sailing maneuvers with configurable angles
- **Custom Python Scripts**: Full Python API for advanced automation and integration
- **Smooth Proportional Control**: Variable PWM duty cycle for gentle, efficient steering corrections
- **Adjustable Response**: PWM frequency and duty cycle tunable in motor.ino for optimal pump performance
- **Configurable Slew Rates**: Separate speed_rate and slow_rate for acceleration vs deceleration
- **Tunable Safety Limits**: max_current, max_controller_temp, max_motor_temp adjustable via serial

## Installation Overview

### Phase 1: Hardware Removal & Preparation
1. **Remove legacy TQM AP8 system**:
   - Disconnect power to TQM AP8 control unit
   - Remove 4x 12V automotive relays from relay H-bridge circuit
   - Disconnect relay control wiring from TQM AP8
   - Remove TQM AP8 control unit and mounting hardware
   - Clean up wiring harnesses and document wire colors/connections for reference
2. **Verify Octopus 1012 hydraulic pump**:
   - Identify pump motor positive and negative terminals (2-wire DC motor)
   - Test pump motor operates on 12V DC (direct connection test with polarity reversal)
   - Measure pump current draw under load (typically 4-6A average, 19A peak)
   - Check hydraulic fluid level and condition
   - Verify hydraulic ram operates smoothly through full range
   - Confirm no hydraulic leaks in system

### Phase 2: Arduino Motor Controller Setup
1. **Flash motor.ino to Arduino Nano**:
   - Install Arduino IDE on Ubuntu (see [docs/flashing_motor_ino_to_arduino.md](docs/flashing_motor_ino_to_arduino.md))
   - Troubleshoot CH340 USB drivers for Chinese Arduino clones if needed
   - Clone pypilot4arion repository: `git clone https://github.com/botheredbybees/pypilot4arion.git`
   - Open `arduino/motor/motor.ino` in Arduino IDE
   - Select Tools → Board → Arduino Nano, Processor → ATmega328P (Old Bootloader)
   - Upload to Arduino
   - **Critical**: Verify or set ATmega328P fuse bits for brownout detection (see docs)
2. **Wire Arduino configuration pins**:
   - **Ground D6** permanently to select H-bridge mode (pwm_style=0)
   - Leave D4, D5 floating (pullups) for 0.05Ω shunt, low current (20A max)
   - Leave D12 floating for 12V voltage sense mode
   - Optionally connect D7/D8 to rudder limit switches (normally-high, pulled low by switch)
3. **Wire Arduino to IBT-2**:
   - D9 → RPWM (pin 1)
   - D10 → LPWM (pin 2)
   - D2 → R_EN (pin 3)
   - D3 → L_EN (pin 4)
   - A1 → R_IS (pin 5), optionally tie L_IS (pin 6) to R_IS for combined current sense
   - Arduino 5V → IBT-2 Vcc (pin 7) - **or use separate 5V supply if Arduino USB power insufficient**
   - Arduino GND → IBT-2 GND (pin 8)
4. **Wire Arduino sensors** (optional but recommended):
   - A0 ← Voltage divider (560Ω to 12V+ bus, 10kΩ to GND) for battery voltage monitoring
   - A2 ← Controller temp sensor (100kΩ to 5V + 10kΩ NTC thermistor to GND)
   - A4 ← Rudder position sensor (potentiometer: 5V, wiper to A4, GND)
5. **Test Arduino serial communication**:
   ```bash
   # Connect Arduino to computer via USB
   screen /dev/ttyUSB0 153600  # For DIV_CLOCK=4: 38400 × 4 = 153600 baud
   # Should see periodic binary telemetry packets
   # Press Ctrl+A then K to exit
   ```

### Phase 3: IBT-2 and Pump Wiring
1. **Mount IBT-2 near hydraulic pump** (minimize motor cable length, ensure ventilation)
2. **Wire IBT-2 to hydraulic pump**:
   - Use 12AWG or heavier wire for motor connections
   - Motor+ (IBT-2 output) → Octopus 1012 motor terminal
   - Motor- (IBT-2 output) → Octopus 1012 motor terminal  
   - **Note polarity**: If pump runs backward, swap Motor+/Motor- connections
3. **Wire IBT-2 power supply**:
   - B+ → 12V positive bus via **30A inline fuse** (close to battery)
   - B- → 12V negative/ground bus
   - Use 10AWG or heavier wire for power supply
   - Ensure solid crimped connections (not twist-on wire nuts)
4. **Initial motor test** (Arduino connected to bench power, NOT Pi yet):
   - Apply 12V to IBT-2 B+/B-
   - Use Arduino serial monitor or test sketch to manually command motor
   - Verify pump runs forward and reverse correctly
   - Measure current draw with multimeter (should be 4-6A under no-load)
   - Listen for unusual noises or vibrations

### Phase 4: Tinypilot Hardware Installation
1. Mount Raspberry Pi Zero W near compass location (away from magnetic interference)
2. Install pypilot IMU with proper orientation and calibration access
3. **Connect Arduino to Pi Zero via USB**:
   - Use quality USB cable (data+power, not power-only)
   - Arduino will appear as `/dev/ttyUSB0` (or `/dev/ttyACM0` with FTDI clone)
   - Pi Zero provides power to Arduino via USB (ensure total draw < 500mA)
   - If Arduino power draw too high (IBT-2 logic powered from Arduino 5V), use external 5V supply for IBT-2
4. **Connect USB GPS receiver to Pi Zero**:
   - Use USB GPS with NMEA 0183 output (4800 or 38400 baud)
   - Connect to Pi Zero USB port (may require micro-USB OTG adapter or hub)
   - GPS powers from Pi Zero USB port (verify power consumption < 500mA)
5. Optionally connect rudder feedback sensor to Arduino A4 (if not already done)

### Phase 5: Tinypilot Software Setup
1. Flash Tinypilot image to Pi Zero SD card
2. Configure WiFi client mode for Pixel 2 phone hotspot (SSID: "YachtArion")
3. Boot Pi Zero and connect to Tinypilot web interface (http://192.168.43.101)
4. **Configure motor controller for Arduino**:
   - Set motor driver type to "arduino" or "motor.ino"
   - Configure serial port (typically `/dev/ttyUSB0`, auto-detected)
   - Set baud rate: `38400 × DIV_CLOCK` (typically 153600 for DIV_CLOCK=4)
   - Set max_current based on pump specs (start conservatively at 15A = 1500 in units of 10mA)
   - Set max_controller_temp (e.g., 6000 = 60°C)
5. **Configure GPS receiver**:
   - Pypilot should auto-detect USB GPS device (appears as /dev/ttyUSB1 or /dev/ttyACM0)
   - Verify NMEA sentences are received (check for RMC, GGA, VTG sentences)
   - Test GPS fix acquisition (may take 1-5 minutes for cold start)
6. **Initial motor direction test**:
   - Engage autopilot in manual control mode (or use web interface sliders)
   - Command small starboard turn → verify rudder moves starboard
   - Command small port turn → verify rudder moves port
   - If reversed, swap Motor+/Motor- wires on IBT-2 outputs
   - **Note**: Response should be much faster and smoother than old relay system
7. Calibrate IMU (compass, accelerometer, alignment)
8. Configure rudder feedback sensor range and calibration (if installed)
9. Tune PID parameters for hydraulic system response

### Phase 6: Testing and Tuning

See [Installation Overview - Phase 6](#phase-6-testing-and-tuning) section for detailed testing procedures.

## Repository Contents

- `/docs/` - Detailed installation guides, wiring diagrams, and Arduino/IBT-2 setup
  - **[Arduino motor.ino Installation Guide](docs/flashing_motor_ino_to_arduino.md)** - Complete guide for Ubuntu
  - [TinyPilot Setup Guide](docs/tinypilot_setup.md)
  - [Lysmarine Integration Guide](docs/lysmarine_integration.md)
  - [motor.ino Configuration Reference](docs/motor_ino_configuration.md)
  - [Wind Sensor Integration (Ecowit WS80)](docs/wind_sensor_integration.md)
- `/arduino/motor/` - motor.ino source code from pypilot repository
  - `motor.ino` - Main firmware file
  - `crc.h` - CRC8 implementation
  - `Makefile` - Command-line compilation (alternative to Arduino IDE)
  - `README` - Original motor.ino documentation
- `/config/` - Sample pypilot configuration files for Arduino motor controller
- `/scripts/` - Python utilities for motor testing, current monitoring, and diagnostics
- `/hardware/` - Hardware specifications, IBT-2 datasheet, Arduino pinouts, component datasheets
- `/calibration/` - Calibration procedures, PID tuning guides, and reference data

## Configuration Notes

### Motor Controller Settings (Arduino/motor.ino)

```python
# Pypilot servo configuration for Arduino motor.ino with IBT-2
servo.controller = 'arduino'  # Uses motor.ino firmware
servo.device = '/dev/ttyUSB0'  # Auto-detected, or specify manually
servo.baud = 153600  # For DIV_CLOCK=4: 38400 × 4 (verify with dmesg)

servo.max_current = 1500  # Units of 10mA, so 1500 = 15A (conservative for Octopus 1012)
servo.max_controller_temp = 6000  # 0.01°C units, so 6000 = 60°C
servo.max_motor_temp = 7000  # 70°C (if motor temp sensor installed)
servo.max_slew_speed = 15  # deg/sec rudder movement (tune for smooth response)
servo.max_slew_slow = 5   # deg/sec rudder movement in heavy conditions

# Rudder feedback (if sensor installed)
servo.rudder_min = 5000   # ADC value at port limit (calibrate)
servo.rudder_max = 60000  # ADC value at starboard limit (calibrate)
```

### Arduino Hardware Configuration

Set these at compile time or via hardware pins:

```cpp
// In motor.ino source (typically auto-detected via pins):
#define DIV_CLOCK 4  // Clock divider: 4 = 4MHz (power savings), 2 = 8MHz, 1 = 16MHz

// Hardware pin detection (read at boot):
// D4: shunt_resistance (floating/HIGH = 0.05Ω, grounded/LOW = 0.01Ω)
// D5: low_current (floating/HIGH = low 20A, grounded/LOW = high 40A)
// D6: pwm_style (GROUND THIS for H-bridge mode, floating for RC PWM)
// D12: voltage_sense (floating = 12V mode, grounded = 24V mode)

uint16_t max_current = 2000; // 20A default, adjust based on pump
uint16_t max_controller_temp= 7000; // 70C
uint16_t max_motor_temp = 7000; // 70C
uint8_t max_slew_speed = 50; // Internal slew rate (0-250)
uint8_t max_slew_slow = 75;
```

### GPIO Pin Assignment Table

| Arduino Pin | Function | Connection | Notes |
|-------------|----------|------------|-------|
| **D2** | H-bridge A bottom | IBT-2 R_EN | Direction control (H-bridge mode) |
| **D3** | H-bridge B bottom | IBT-2 L_EN | Direction control (H-bridge mode) |
| D4 | Shunt resistance | Config (floating) | HIGH=0.05Ω, LOW=0.01Ω |
| D5 | Low current mode | Config (floating) | HIGH=20A max, LOW=40A max |
| **D6** | PWM style | **Config (GROUND)** | **LOW=H-bridge, HIGH=RC PWM** |
| D7 | Port fault input | Optional limit switch | Pulled HIGH internally, switch pulls LOW |
| D8 | Starboard fault input | Optional limit switch | Pulled HIGH internally, switch pulls LOW |
| **D9** | PWM output / H-bridge A top | **IBT-2 RPWM** | Right/Forward PWM signal |
| **D10** | Enable / H-bridge B top | **IBT-2 LPWM** | Left/Reverse PWM signal |
| D11 | Clutch output | Not used | Can repurpose for LED indicator |
| D12 | Voltage sense mode | Config (floating) | HIGH=12V mode, LOW=24V mode |
| D13 | Status LED | Onboard LED | ON when engaged, OFF when disengaged |
| **A0** | Voltage sense | Voltage divider | 560Ω to 12V+, 10kΩ to GND |
| **A1** | Current sense | **IBT-2 R_IS** | Analog voltage proportional to motor current |
| A2 | Controller temp | NTC thermistor | 100kΩ to 5V + 10kΩ NTC to GND |
| A3 | Motor temp | NTC thermistor (opt) | 100kΩ to 5V + 10kΩ NTC to GND |
| A4 | Rudder sense | Potentiometer (opt) | 5V, wiper to A4, GND |
| A5 | Clutch sense PWM | Not used | Can repurpose |
| **USB** | Serial to Pi Zero | **/dev/ttyUSB0** | **38400 × DIV_CLOCK baud (153600)** |

## Performance Characteristics

- **Heading Hold Accuracy**: ±2-5° (dependent on sea state, heel angle, and PID tuning)
- **Rudder Response Time**: ~0.5-2 seconds (Arduino + IBT-2 response time < 50ms, limited by hydraulic flow)
- **Motor Switching Speed**: <1µs (solid-state) vs ~10-20ms (relay-based legacy system)
- **Serial Protocol Latency**: ~100ms (4-byte packets at 153600 baud, with CRC validation)
- **Safety Response Time**: ~100ms (Arduino monitors current/voltage/temp at 10-50Hz)
- **Power Consumption**: 
  - Pi Zero: ~2.4W (200mA @ 12V)
  - Arduino Nano: ~0.6W (50mA @ 12V via USB)
  - USB GPS: ~0.6W (50mA @ 12V via USB)
  - Pi 4: ~7.5W (625mA @ 12V) 
  - Hydraulic pump (active steering): 48-72W average (4-6A @ 12V), 228W peak (19A @ 12V)
  - Hydraulic pump (holding course): ~24-60W intermittent
  - IBT-2 standby: <1W (vs ~2-4W for relay coils in legacy system)
  - **Total standby**: ~12W (both Pis + Arduino + GPS)
- **IMU Update Rate**: 10-20 Hz
- **GPS Update Rate**: 1-10 Hz (typical 1Hz)
- **Arduino Telemetry Rate**: Matches pypilot command rate, typically 10-20Hz
- **Control Loop Frequency**: 10 Hz (pypilot)
- **PWM Frequency**: Configurable in motor.ino: 1kHz, 16kHz, or 62.5Hz (for high duty cycles)
- **Maximum Rudder Slew Rate**: 10-20°/sec (configurable, limited by hydraulic flow rate and max_slew_speed)

## Bill of Materials (BOM)

### Core Autopilot Components
- Raspberry Pi Zero W - ~$22 AUD
- Pypilot IMU (MPU9250 or ICM-20948 based) - ~$75-150 AUD
- **Arduino Nano (clone with CH340 USB)** - ~$7-15 AUD
- **IBT-2 Motor Controller (dual BTS7960B)** - ~$22-30 AUD
- USB GPS receiver (NMEA 0183, USB interface) - ~$30-75 AUD
- Rudder feedback sensor (potentiometer 5kΩ linear) - ~$15-30 AUD (optional)
- NTC thermistors (10kΩ, 3950K) for temp sensing - ~$5 AUD (optional)
- MicroSD card (16GB+, high endurance recommended) - ~$15 AUD
- Power wiring (10-12AWG), 30A inline fuse, connectors - ~$45 AUD
- **Total Core System**: ~$236-387 AUD

### Legacy Hardware Removed (For Reference)
- TQM AP8 control unit - removed
- 4x 12V automotive relays (30-40A SPDT) - removed
- Relay control wiring and driver circuits - removed
- Approximate legacy component value: ~$50-100 AUD (recyclable/resellable)

**Comparison**: Arduino + IBT-2 (~$44 AUD) replaces relay H-bridge (~$50-100 AUD) with improved performance.

## Resources

### Pypilot Motor Controller Documentation
- [motor.ino Source Code](https://github.com/pypilot/pypilot/tree/master/arduino/motor)
- [motor.ino README](https://github.com/pypilot/pypilot/blob/master/arduino/motor/README)
- [Arduino Motor Controller Installation Guide](docs/flashing_motor_ino_to_arduino.md) (this repository)

### IBT-2 and BTS7960B Resources
- [BTS7960B Datasheet (Infineon)](https://www.infineon.com/dgdl/bts7960b.pdf)
- [IBT-2 with Arduino - Dr. Rainer Hessmer](https://www.hessmer.org/blog/2013/12/28/ibt-2-h-bridge-with-arduino/)
- [DCC-EX IBT_2 Motor Board Setup](https://dcc-ex.com/reference/hardware/motorboards/IBT_2-motor-board-setup.html)

### Community Forums
- [OpenMarine Forum - IBT-2 with Pypilot](https://forum.openmarine.net/showthread.php?tid=3388)
- [Pypilot GitHub - Motor Controller Discussions](https://github.com/pypilot/pypilot/discussions)

## License

This documentation is released under MIT License. Pypilot software (including motor.ino) is licensed under GPLv3.

## Acknowledgments

- **Sean d'Epagnier** - Creator of pypilot and motor.ino firmware (RIP - his legacy lives on)
- **OpenMarine community** - Ongoing pypilot support and development
- **Dr. Rainer Hessmer** - IBT-2 Arduino integration documentation
- The broader open-source marine navigation community

---

**Project Status**: Hardware acquisition and bench testing phase (January 2026)

**Maintainer**: botheredbybees  
**Vessel**: SY Arion (36ft)  
**Location**: Cygnet, Tasmania, Australia

**Last Updated**: January 20, 2026
```
