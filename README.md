# Pypilot for Arion

Open-source autopilot retrofit for 36ft yacht *Arion* using pypilot with hydraulic steering, modern IBT-2 motor controller, and legacy Octopus hydraulic pump.

## Project Overview

This project documents the installation and configuration of a pypilot-based autopilot system on *Arion*, a 36-foot sailboat with existing hydraulic steering. The installation **replaces a non-functional TQM AP8 autopilot** (removing the relay-based H-bridge control system) with a modern solid-state system using an **IBT-2 motor controller with dual BTS7960B H-bridge chips** driving the existing **Octopus Model 1012 hydraulic pump** directly.

The system uses a dual-Raspberry Pi architecture combining reliability and functionality:
- **Tinypilot** on Raspberry Pi Zero W for dedicated autopilot control
- **Lysmarine** on Raspberry Pi 4 (8GB) for navigation, chartplotting, and marine data integration

## Technology Stack

### Hardware

#### Autopilot System (Tinypilot)
- **Computer**: Raspberry Pi Zero W
- **Operating System**: Tinypilot (TinyCore Linux-based, runs from RAM)
- **IMU**: Pypilot IMU with compass, gyroscope, and accelerometer
- **Motor Controller**: IBT-2 with dual BTS7960B H-bridge chips
  - Continuous current: 43A per channel
  - Operating voltage: 5.5-27V (12V nominal for marine use)
  - PWM frequency: Up to 25kHz
  - Direct 3.3V GPIO compatible (no level shifters required)
  - Dual current sense outputs (R_IS, L_IS)
  - Integrated thermal protection
- **Hydraulic Pump**: Octopus Model 1012 (12V DC, retained from original installation)
- **Motor Connection**: Direct PWM control from IBT-2 to hydraulic pump motor (no relays)
- **GPS Receiver**: USB GPS (NMEA 0183) connected directly to Pi Zero W for standalone GPS mode operation
- **Rudder Feedback**: Analog or digital rudder position sensor
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
- **Motor Controller Firmware**: Arduino-based pypilot motor driver with IBT-2 support
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
              ├── Rudder feedback sensor (analog/digital)
              └── Motor controller (GPIO PWM)
                   |
                   └── IBT-2 H-Bridge (Solid-State PWM Control)
                        ├── RPWM (Right PWM) ← GPIO PWM
                        ├── LPWM (Left PWM) ← GPIO PWM
                        ├── R_EN/L_EN (Enable) ← GPIO Digital
                        ├── R_IS/L_IS (Current Sense) → ADC
                        └── Motor Output (+/-)
                             |
                             └── Octopus 1012 Hydraulic Pump (12V DC motor)
                                  |
                                  └── Hydraulic Steering Ram
```

### IBT-2 Motor Controller Connection

The IBT-2 provides **direct bidirectional PWM control** of the hydraulic pump motor using solid-state MOSFET switching. The legacy TQM AP8 used **4x 12V automotive relays wired as an H-bridge** to control pump motor polarity (on/off switching only). The IBT-2 replaces this entire relay-based circuit with **solid-state proportional PWM control** for smooth, efficient steering.

**Pi Zero GPIO to IBT-2 Wiring:**
```
Pi Zero GPIO    IBT-2 Pin       Function
-----------     ---------       --------
GPIO 18 (PWM)   RPWM (pin 1)   Right/Forward PWM signal
GPIO 19 (PWM)   LPWM (pin 2)   Left/Reverse PWM signal
GPIO 23         R_EN (pin 3)   Right enable (hold HIGH)
GPIO 24         L_EN (pin 4)   Left enable (hold HIGH)
ADC/GPIO        R_IS (pin 5)   Right current sense (optional)
ADC/GPIO        L_IS (pin 6)   Left current sense (optional)
GND             GND            Common ground
```

**IBT-2 to Hydraulic Pump:**
```
Motor+ (out)  →  Hydraulic pump motor positive terminal
Motor- (out)  →  Hydraulic pump motor negative terminal
B+ (power in) →  12V ship's power (30A fused)
B- (power in) →  12V ground/negative bus
```

**Control Logic:**
- **Forward (starboard turn)**: RPWM=PWM duty cycle (0-100%), LPWM=0%, both EN=HIGH
- **Reverse (port turn)**: LPWM=PWM duty cycle (0-100%), RPWM=0%, both EN=HIGH
- **Brake/Stop**: Both RPWM=0% and LPWM=0%, both EN=HIGH
- **Emergency stop**: Both EN=LOW (disables all outputs)

### Legacy Relay H-Bridge (Being Replaced)

The TQM AP8 used a classic **4-relay H-bridge configuration** for motor polarity reversal:

```
        +12V ────┬────────────┬────
                 │            │
              Relay1       Relay3
              (SPDT)       (SPDT)
              30A NO       30A NO
                 │            │
                 ├─── M+ ─────┤
                 │  (Motor)   │
                 ├─── M- ─────┤
                 │            │
              Relay2       Relay4
              (SPDT)       (SPDT)
              30A NO       30A NO
                 │            │
        GND ─────┴────────────┴────

Forward/Starboard: Relay1 + Relay4 energized (M+ to +12V, M- to GND)
Reverse/Port:      Relay2 + Relay3 energized (M- to +12V, M+ to GND)
Stop:              All relays de-energized (motor floating)
```

**Limitations of Relay-Based System:**
- **Bang-bang control only**: On/off switching with no proportional control
- **Mechanical wear**: Relay contacts degrade from arcing (typical lifespan 100,000-1M operations)
- **Slow response**: ~10-20ms switching time per relay activation
- **Electrical noise**: Contact arcing generates RF interference
- **Power consumption**: Relay coils draw ~100-200mA each when energized
- **Contact welding risk**: High inrush current can weld relay contacts closed

**Advantages of IBT-2 Solid-State Replacement:**
- **Proportional PWM control**: Variable speed control (0-100% duty cycle)
- **Unlimited lifespan**: No mechanical wear on MOSFET switching
- **Ultra-fast response**: <1µs switching time (20,000x faster than relays)
- **Clean switching**: No electrical arcing or RF interference
- **Lower standby power**: MOSFETs draw minimal gate current
- **Current sensing**: Real-time motor current monitoring via R_IS/L_IS outputs
- **Thermal protection**: Automatic shutdown on over-temperature
- **Smooth operation**: Variable PWM eliminates jerky bang-bang steering

### Data Flow

**GPS to Autopilot (Standalone Mode):**
1. USB GPS receiver connected directly to Pi Zero W USB port
2. Pypilot reads NMEA sentences from USB serial device (auto-detected at 4800 or 38400 baud)
3. Pypilot uses GPS data for GPS track mode **without requiring network or Pi 4**
4. Pi Zero operates fully standalone for both Compass and GPS modes

**GPS to Navigation System (Optional):**
1. Second GPS receiver → Lysmarine Pi 4 (USB/serial) for OpenCPN chartplotting
2. SignalK processes and broadcasts NMEA data for other instruments
3. GPS data also available via network to Tinypilot if needed

**Wind Data to Autopilot (Future):**
1. Ecowit WS80 sensor transmits 433/915MHz RF signals
2. RTL-SDR dongle on Pi 4 receives RF transmission
3. rtl_433 decodes weather sensor protocol
4. rtl_433-to-SignalK bridge converts to marine format
5. SignalK broadcasts wind data (apparent wind speed/direction)
6. Pypilot receives wind data via network for Wind mode calculations
7. Pypilot calculates true wind using local GPS speed/heading

**Autopilot Control Loop:**
1. User sets heading via OpenCPN or Tinypilot web interface
2. Command sent to pypilot server (TCP 20220)
3. Pypilot reads IMU (compass heading, heel, pitch) at 10-20Hz
4. PID controller calculates steering correction
5. PWM command sent via GPIO to IBT-2 controller
6. IBT-2 drives hydraulic pump motor bidirectionally with proportional control
7. Hydraulic pressure moves steering ram
8. Rudder feedback sensor reports position
9. Pypilot adjusts PWM duty cycle to reach target rudder angle
10. Loop continues at 10Hz control frequency

**Status Monitoring:**
1. Pypilot broadcasts heading, rudder angle, autopilot mode, motor current
2. OpenCPN pypilot plugin displays real-time status and allows mode changes
3. SignalK distributes autopilot data to other marine instruments
4. Current sense from IBT-2 monitors pump load and detects faults

## Key Features

### Reliability
- **Standalone Operation**: Tinypilot operates independently in Compass and GPS modes without network or Pi 4
- **Local GPS**: USB GPS connected directly to Pi Zero enables GPS track mode without network dependency
- **RAM-based OS**: Tinypilot runs entirely from RAM after boot—safe power disconnection, no SD card corruption
- **Dual-System Redundancy**: Navigation computer failure doesn't affect autopilot operation
- **Minimal Power**: Pi Zero + USB GPS consumes ~3W for extended offshore passages
- **No Relay Wear**: Solid-state IBT-2 eliminates relay contact degradation and mechanical failure modes
- **Proportional Control**: PWM allows smooth, proportional steering response (not just on/off bang-bang)
- **Unlimited Switching**: MOSFETs have no wear limit unlike relay contacts (millions of operations)

### Safety
- **Network Independence**: Core steering function never depends on WiFi connectivity
- **Rudder Feedback**: Continuous position monitoring prevents rudder runaway
- **Current Limiting**: IBT-2 current sense monitors pump load and detects stall/overload
- **Thermal Protection**: BTS7960B chips have integrated over-temperature shutdown
- **Manual Override**: Hydraulic steering allows instant manual override at helm
- **Fuse Protection**: 30A inline fuse protects against electrical faults and short circuits
- **Emergency Shutdown**: Software can disable IBT-2 via EN pins for immediate motor stop
- **No Contact Arcing**: Solid-state switching eliminates electrical arcing fire risk

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
- **Adjustable Response**: PWM frequency and duty cycle tunable for optimal pump performance

## Installation Overview

### Phase 1: Hardware Removal & Preparation
1. **Remove legacy TQM AP8 system**:
   - Disconnect power to TQM AP8 control unit
   - Remove 4x 12V automotive relays from relay H-bridge circuit
   - Disconnect relay control wiring from TQM AP8
   - Remove TQM AP8 control unit and mounting hardware
   - Clean up wiring harnesses and document wire colors/connections for reference
2. **Verify Octopus 1012 hydraulic pump**:
   - Identify pump motor positive and negative terminals (formerly connected to relay H-bridge)
   - Test pump motor operates on 12V DC (direct connection test with polarity reversal)
   - Measure pump current draw under load (typically 15-25A)
   - Check hydraulic fluid level and condition
   - Verify hydraulic ram operates smoothly through full range
   - Confirm no hydraulic leaks in system

### Phase 2: Autopilot Hardware Installation
1. Mount Raspberry Pi Zero W near compass location (away from magnetic interference)
2. Install pypilot IMU with proper orientation and calibration access
3. Mount IBT-2 motor controller near hydraulic pump (minimize motor cable length)
4. **Wire IBT-2 to Pi Zero GPIO** (see connection diagram above)
5. **Wire IBT-2 to hydraulic pump motor**:
   - Use 12AWG or heavier wire for motor power connections
   - Keep motor cables as short as practical (minimize voltage drop)
   - Connect Motor+/Motor- to pump terminals (polarity determines initial direction)
   - Note: These connect directly where the relay H-bridge outputs were connected
6. **Wire IBT-2 power supply**:
   - Connect B+ to 12V positive bus via 30A inline fuse
   - Connect B- to 12V negative/ground bus
   - Use 10AWG or heavier wire for power supply
7. **Connect USB GPS receiver to Pi Zero W**:
   - Use USB GPS with NMEA 0183 output (4800 or 38400 baud)
   - Connect to Pi Zero USB port (may require micro-USB OTG adapter)
   - GPS powers from Pi Zero USB port (verify power consumption < 500mA)
8. Install rudder feedback sensor on rudder shaft or hydraulic ram
9. Connect rudder sensor to Pi Zero (analog ADC or digital encoder interface)

### Phase 3: Tinypilot Software Setup
1. Flash Tinypilot image to Pi Zero SD card
2. Configure WiFi client mode for Pixel 2 phone hotspot (SSID: "YachtArion")
3. Boot Pi Zero and connect to Tinypilot web interface (http://192.168.43.101)
4. **Configure motor controller for IBT-2**:
   - Set motor driver type to "IBT-2" or "dual PWM H-bridge"
   - Configure GPIO pin assignments (RPWM, LPWM, R_EN, L_EN)
   - Set PWM frequency (typically 10-20kHz for DC motors)
   - Enable current sense inputs if wired (R_IS, L_IS)
5. **Configure GPS receiver**:
   - Pypilot should auto-detect USB GPS device (appears as /dev/ttyUSB0 or /dev/ttyACM0)
   - Verify NMEA sentences are received (check for RMC, GGA, VTG sentences)
   - Test GPS fix acquisition (may take 1-5 minutes for cold start)
6. **Initial motor direction test**:
   - Engage autopilot in manual control mode
   - Command small starboard turn → verify rudder moves starboard
   - Command small port turn → verify rudder moves port
   - If reversed, swap RPWM/LPWM pins or invert in software
   - Note: Response should be much faster and smoother than old relay system
7. Calibrate IMU (compass, accelerometer, alignment)
8. Configure rudder feedback sensor range and calibration
9. Tune PID parameters for hydraulic system response

### Phase 4: Lysmarine Integration
1. Verify Lysmarine Pi 4 connects to Pixel 2 phone hotspot
2. Install OpenCPN pypilot plugin
3. Configure plugin to connect to Tinypilot IP (192.168.43.101:20220)
4. Configure SignalK to receive autopilot data from Tinypilot
5. Test Compass mode and GPS track mode via OpenCPN interface
6. (Optional) Connect second GPS to Pi 4 for independent OpenCPN navigation

### Phase 5: Wind Sensor Integration (Future)
1. Install Ecowit WS80 sensor at masthead or suitable location
2. Power WS80 via solar panel (integrated) or external 12V supply
3. Connect RTL-SDR dongle to Lysmarine Pi 4 USB port
4. Install and configure rtl_433 software on Pi 4:
   ```bash
   sudo apt-get install rtl_433
   rtl_433 -f 433.92M -R 156  # Test Ecowit sensor reception
   ```
5. Configure rtl_433 to output to SignalK:
   - Install rtl_433-to-signalk bridge or MQTT integration
   - Map WS80 wind speed/direction to SignalK paths
   - Configure apparent wind calculation in SignalK
6. Test Wind mode and True Wind mode in pypilot (via network data from Pi 4)

### Phase 6: Testing and Tuning
1. **Dockside testing**: 
   - Verify motor controller responds to all commands
   - Check current sense readings match expectations
   - Test emergency stop functionality
   - Verify GPS acquisition and position reporting
   - Compare response time vs old relay-based system (should be noticeably faster and smoother)
2. **Motoring trials**: 
   - Test compass mode stability in straight-line motoring
   - Test GPS track mode following straight line waypoint
   - Verify manual override functions properly
   - Tune PID gains for smooth response without oscillation
   - Adjust PWM frequency if motor noise is excessive
   - Compare power consumption vs relay system (should be similar or lower)
3. **Sailing trials**: 
   - Test in various sea states and wind conditions
   - Tune PID gains for heel compensation
   - Verify power consumption acceptable for long passages
   - Test GPS track mode following curved routes
   - Evaluate smoothness of steering vs old bang-bang relay system
4. **Advanced mode testing**: 
   - GPS track following accuracy over multiple waypoints
   - Wind mode performance (after sensor installation)
   - NAV mode route following from OpenCPN
5. **Emergency procedures**: 
   - Verify manual override and fail-safe behavior
   - Test autopilot disengage under load
   - Confirm fuse protection operates correctly if pump stalls

## Repository Contents

- `/docs/` - Detailed installation guides, wiring diagrams, and IBT-2 setup
  - [TinyPilot Setup Guide](docs/tinypilot_setup.md)
  - [Lysmarine Integration Guide](docs/lysmarine_integration.md)
  - [Wind Sensor Integration (Ecowit WS80)](docs/wind_sensor_integration.md)
  - [House Rewiring Plan](docs/rewiring_house_loads.md)
  - [Arduino Motor Controller Flashing Guide](docs/flashing_motor_ino_to_arduino.md)
  - [24V Solar System Design](docs/24v_solar_system.md)
  - [Emergency Procedures](docs/emergency_procedures.md)
  - [Maintenance Schedule](docs/maintenance_schedule.md)
  - [Backup & Recovery](docs/backup_and_recovery.md)
  - [Network Map](docs/network_map.md)
  - [Cockpit Quick Ref](docs/cockpit_quick_ref.md)
  - [Project Shopping List](docs/shopping_list.md)
- `/config/` - Sample pypilot configuration files for IBT-2 motor controller
- `/scripts/` - Python utilities for motor testing, current monitoring, and diagnostics
- `/hardware/` - Hardware specifications, IBT-2 datasheet, Ecowit WS80 info, component datasheets, legacy relay H-bridge photos
- `/calibration/` - Calibration procedures, PID tuning guides, and reference data
- `/wind_integration/` - rtl_433 configuration, SignalK integration, WS80 setup (future)

## Configuration Notes

### Motor Controller Settings (IBT-2)
```python
# Pypilot servo configuration for IBT-2 H-bridge with direct motor control
servo.controller = 'arduino'  # or 'tinypilot' depending on hardware
servo.driver = 'IBT2'  # Dual PWM H-bridge mode
servo.max_current = 20  # Amps, set based on pump current draw (typically 15-25A)
servo.max_controller_temp = 60  # Celsius (BTS7960B has thermal shutdown)
servo.max_slew_speed = 15  # deg/sec rudder movement (tune for smooth response)
servo.max_slew_slow = 5   # deg/sec rudder movement in heavy conditions

# GPIO pin assignments for Pi Zero
servo.pins.rpwm = 18  # Right/Forward PWM (BCM GPIO 18)
servo.pins.lpwm = 19  # Left/Reverse PWM (BCM GPIO 19)
servo.pins.r_en = 23  # Right enable (BCM GPIO 23)
servo.pins.l_en = 24  # Left enable (BCM GPIO 24)
servo.pins.r_is = 17  # Right current sense (optional, ADC or GPIO)
servo.pins.l_is = 27  # Left current sense (optional, ADC or GPIO)

# PWM parameters
servo.pwm_frequency = 15000  # Hz (10-20kHz typical for DC motors)
servo.min_speed = 0.1  # Minimum PWM duty cycle (deadband compensation)
```

### GPS Configuration
```python
# GPS auto-detection on Pi Zero
# Pypilot will scan for USB serial devices and detect NMEA output
# Common device names: /dev/ttyUSB0, /dev/ttyACM0
# Supported baud rates: 4800, 38400 (auto-detected)

# Manual configuration if needed:
gps.device = '/dev/ttyUSB0'  # or /dev/ttyACM0
gps.baud = 4800  # or 38400
gps.enabled = true
```

### Network Configuration
```bash
# /etc/wpa_supplicant/wpa_supplicant.conf on Tinypilot Pi Zero
country=AU
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YachtArion"
    psk="your_hotspot_password"
    priority=10
}

# Optional: Add additional networks for marina/home WiFi
network={
    ssid="Marina_WiFi"
    psk="marina_password"
    priority=5
}
```

### rtl_433 Configuration (Future Wind Sensor)
```bash
# /etc/rtl_433/rtl_433.conf
frequency 433.92M
protocol 156  # Ecowit/Ambient Weather protocol
output json
output mqtt://localhost:1883,retain=0,events=rtl_433/devices[/model][/id]

# Alternative: Output directly to SignalK
# output http://localhost:3000/signalk/v1/api/vessels/self
```

## Failsafe Behavior

| Component Failure | Autopilot Status | Available Modes | Motor Control | Notes |
|------------------|------------------|-----------------|---------------|-------|
| Pixel 2 phone hotspot offline | **Continues normally** | Compass, GPS (local) | **Fully operational** | No Wind/NAV modes, no OpenCPN integration |
| Lysmarine Pi 4 offline | **Continues normally** | Compass, GPS (local) | **Fully operational** | No OpenCPN, no network wind data |
| Both network systems offline | **Continues normally** | Compass, GPS (local) | **Fully operational** | Fully autonomous with local GPS |
| Pi Zero power loss | **Stops immediately** | None | **No control** | Manual steering required |
| Motor controller fault | **Stops immediately** | None | **No control** | Check IBT-2, fuses, connections |
| IBT-2 thermal shutdown | **Stops temporarily** | Resumes when cool | **Disabled until cool** | Reduce max_current or improve cooling |
| Hydraulic pump stall | **Current sense detects** | Error state | **Reduced power** | Check hydraulic fluid, ram binding |
| IMU failure | **Error state** | None | **No reliable heading** | Manual steering required |
| USB GPS failure | **Compass mode only** | Compass only | **Fully operational** | GPS and NAV modes unavailable |

**Critical Safety Note**: Compass and GPS modes are fully standalone and require only:
- Pi Zero with power
- Functional IMU (compass heading)
- USB GPS receiver (for GPS mode)
- IBT-2 motor controller
- Rudder feedback sensor
- Hydraulic pump and steering system

Network connectivity is **optional** for Wind mode and NAV route following only.

## Performance Characteristics

- **Heading Hold Accuracy**: ±2-5° (dependent on sea state, heel angle, and PID tuning)
- **Rudder Response Time**: ~0.5-2 seconds (much faster than relay system, limited by hydraulic flow)
- **Motor Switching Speed**: <1µs (solid-state) vs ~10-20ms (relay-based legacy system)
- **Power Consumption**: 
  - Pi Zero: ~2.4W (200mA @ 12V)
  - USB GPS: ~0.6W (50mA @ 12V via USB)
  - Pi 4: ~7.5W (625mA @ 12V) 
  - Hydraulic pump (active steering): 180-300W (15-25A @ 12V)
  - Hydraulic pump (holding course): ~60-120W intermittent
  - IBT-2 standby: <1W (vs ~2-4W for relay coils in legacy system)
- **IMU Update Rate**: 10-20 Hz
- **GPS Update Rate**: 1-10 Hz (typical 1Hz)
- **Control Loop Frequency**: 10 Hz
- **PWM Frequency**: 10-20 kHz (configurable, affects motor noise and efficiency)
- **PWM Resolution**: 8-16 bit (256-65536 discrete levels for smooth proportional control)
- **Maximum Rudder Slew Rate**: 10-20°/sec (configurable, limited by hydraulic flow rate)

## Bill of Materials (BOM)

### Core Autopilot Components
- Raspberry Pi Zero W - ~$A22 AUD
- Pypilot IMU (MPU9250 or ICM-20948 based) - ~$A75-150 AUD
- IBT-2 Motor Controller (dual BTS7960B) - ~$A22-30 AUD
- USB GPS receiver (NMEA 0183, USB interface) - ~$A30-75 AUD
- Rudder feedback sensor (potentiometer or Hall effect) - ~$A30-75 AUD
- MicroSD card (16GB+, high endurance recommended) - ~$A15 AUD
- Power wiring, fuses, connectors - ~$A45 AUD
- **Total Core System**: ~$A239-397 AUD

### Navigation System (Existing)
- Raspberry Pi 4 (8GB) - ~$A110 AUD
- Argon ONE V2 case - ~$A37 AUD
- 512GB SSD - ~$A75 AUD
- GPS receiver (optional second unit) - ~$A45-150 AUD
- **Total Navigation**: ~$A267-372 AUD (already owned)

### Future Wind Sensor Addition
- Ecowit WS80 6-in-1 sensor - ~$A150-225 AUD
- RTL-SDR V3/V4 USB dongle - ~$A37-60 AUD
- Mounting hardware, cabling - ~$A30 AUD
- **Total Wind System**: ~$A217-315 AUD

### Network
- Google Pixel 2 phone (already owned) - $A0 AUD
- DC-DC buck converter (12V to 5V USB, 3A) - ~$A15-25 AUD
- Mobile data plan (optional for weather) - varies

### Legacy Hardware Removed (For Reference)
- TQM AP8 control unit - removed
- 4x 12V automotive relays (30-40A SPDT) - removed
- Relay control wiring and driver circuits - removed
- Approximate legacy component value: ~$A50-100 AUD (recyclable/resellable)

**Total Project Cost**: ~$A239-397 AUD (core autopilot only, excluding navigation system and wind sensor)

**Total with Future Wind Integration**: ~$A456-712 AUD

## Contributing

This is a personal project documentation repository, but contributions, suggestions, and experience reports from similar installations are welcome. Particularly interested in:
- IBT-2 motor controller tuning advice for hydraulic systems
- Ecowit WS80 integration experiences with rtl_433 and SignalK
- Alternative rudder feedback sensor recommendations
- PID tuning strategies for different sea states
- USB GPS receiver recommendations for marine use
- Comparisons of solid-state vs relay-based autopilot performance
- Experiences upgrading from TQM AP8 or similar relay-based systems

Please open an issue for discussion before submitting pull requests.

## Resources

### Official Documentation
- [Pypilot Official Documentation](https://pypilot.org/doc/pypilot_user_manual/)
- [OpenPlotter Pypilot Documentation](https://openplotter.readthedocs.io/latest/pypilot/pypilot_app.html)
- [Lysmarine (BBN OS) Documentation](https://bareboat-necessities.github.io/my-bareboat/)
- [Tinypilot Information](https://pypilot.org)
- [Wireless Hotspot Setup Guide](docs/wireless_hotspot.md)

### Community Forums
- [OpenMarine Forum - Pypilot Section](https://forum.openmarine.net/forumdisplay.php?fid=17)
- [Pypilot GitHub Discussions](https://github.com/pypilot/pypilot/discussions)
- [IBT-2 Motor Controller Discussion](https://github.com/pypilot/pypilot/issues/37)

### Hardware Datasheets & Resources
- [IBT-2 Motor Controller Datasheet (BTS7960B)](https://www.infineon.com/dgdl/bts7960b.pdf)
- [BTS7960B Half-Bridge Driver Technical Details](https://www.hessmer.org/blog/2013/12/28/ibt-2-h-bridge-with-arduino/)
- [rtl_433 GitHub Repository](https://github.com/merbanan/rtl_433)
- [Ecowit WS80 Specifications](https://www.ecowitt.com/shop/goodsDetail/256)
- [RTL-SDR Blog - Weather Station Integration](https://www.rtl-sdr.com/building-a-diy-off-grid-weather-station-with-a-raspberry-pi-and-rtl-sdr-receiver/)

### Related Projects
- [DIY Marine Autopilot with IBT-2](https://forum.openmarine.net/showthread.php?tid=3385)
- [Arduino IBT-2 Motor Control Examples](https://www.hessmer.org/blog/2013/12/28/ibt-2-h-bridge-with-arduino/)
- [rtl_433 Weather Sensor Decoding](https://github.com/merbanan/rtl_433)
- [Pypilot GPS Configuration](https://forum.openmarine.net/showthread.php?tid=5167)

## License

This documentation is released under MIT License. Pypilot software is licensed under GPLv3.

## Acknowledgments

- **Sean d'Epagnier** - Creator and primary developer of pypilot (RIP - his legacy lives on)
- **OpenMarine community** - Ongoing pypilot support and development
- **Bareboat Necessities team** - Lysmarine OS development and maintenance
- **rtl_433 contributors** - Software-defined radio decoder for weather sensors
- The broader open-source marine navigation community

---

**Project Status**: Planning and hardware acquisition phase (January 2026)

**Maintainer**: botheredbybees  
**Vessel**: SY Arion (36ft)  
**Location**: Cygnet, Tasmania, Australia

**Last Updated**: January 19, 2026