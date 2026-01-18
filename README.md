# Pypilot for Arion

Open-source autopilot retrofit for 36ft yacht *Arion* using pypilot with hydraulic steering and legacy solenoid hardware.

## Project Overview

This project documents the installation and configuration of a pypilot-based autopilot system on *Arion*, a 36-foot sailboat with existing hydraulic steering. The installation reuses four solenoids from a non-functional TQM AP8 autopilot (configured as an H-bridge) controlling an Octopus Model 1012 hydraulic pump, integrated with a modern IBT-2 motor controller featuring dual BTS7960B chips.

The system uses a dual-Raspberry Pi architecture combining reliability and functionality:
- **Tinypilot** on Raspberry Pi Zero W for dedicated autopilot control
- **Lysmarine** on Raspberry Pi 4 (8GB) for navigation, chartplotting, and marine data integration

## Technology Stack

### Hardware

#### Autopilot System (Tinypilot)
- **Computer**: Raspberry Pi Zero W
- **Operating System**: Tinypilot (TinyCore Linux-based, runs from RAM)
- **IMU**: Pypilot IMU with compass, gyroscope, and accelerometer
- **Motor Controller**: IBT-2 with dual BTS7960B H-bridge chips (30A continuous, 43A peak per channel)
- **Hydraulic Pump**: Octopus Model 1012 (legacy, retrofitted)
- **Solenoids**: 4x solenoids from TQM AP8 (H-bridge configuration: port/starboard pairs)
- **Rudder Feedback**: Analog or digital rudder position sensor
- **Power**: 12V DC ship's power with appropriate fusing (20-30A recommended)

#### Navigation System (Lysmarine)
- **Computer**: Raspberry Pi 4 (8GB RAM)
- **Case**: Argon ONE V2 Aluminium Case with passive cooling
- **Storage**: 512GB SSD
- **Operating System**: Lysmarine (BBN OS - Bareboat Necessities OS)
- **Display**: Compatible marine display or standard HDMI monitor
- **GPS**: External GPS receiver (NMEA 0183/2000 via USB or serial)

#### Network
- **WiFi Access Point**: Mobile phone hotspot
- **Network Architecture**: Both Raspberry Pis connect as WiFi clients to phone hotspot
- **IP Addressing**: Static DHCP reservation recommended (e.g., Pi4: 192.168.43.100, Pi Zero: 192.168.43.101)

### Software

#### Core Autopilot
- **Pypilot**: Open-source marine autopilot software (https://pypilot.org)
- **Tinypilot**: Minimal, dedicated pypilot distribution running from RAM
- **Control Modes**: 
  - Compass (magnetic heading) - **fully standalone, no network required**
  - GPS (track following) - requires GPS data via network
  - Wind (wind angle) - requires wind sensor data
  - NAV (route following) - requires waypoint data from OpenCPN

#### Navigation & Integration
- **Lysmarine (BBN OS)**: Comprehensive marine computing platform
- **OpenCPN**: Electronic chart plotter and navigation software
- **SignalK**: Modern marine data server for sensor integration and data multiplexing
- **Pypilot OpenCPN Plugin**: Direct autopilot control and monitoring from OpenCPN

#### Data Protocols
- **NMEA 0183**: GPS, wind, and sensor data (TCP port 10110)
- **Pypilot TCP Protocol**: Autopilot control and status (TCP port 20220)
- **SignalK WebSocket**: Real-time marine data distribution (TCP port 3000)

## System Architecture

### Network Topology

```
Mobile Phone Hotspot (192.168.43.1)
         |
         |--- Raspberry Pi 4 (192.168.43.100)
         |    ├── Lysmarine OS
         |    ├── OpenCPN (chartplotter)
         |    ├── SignalK (data hub)
         |    ├── GPS receiver → NMEA data
         |    └── Pypilot plugin (client)
         |
         └--- Raspberry Pi Zero W (192.168.43.101)
              ├── Tinypilot OS
              ├── Pypilot server (TCP 20220)
              ├── IMU (I2C)
              ├── Rudder feedback sensor
              └── Motor controller (GPIO/serial)
                   |
                   └── IBT-2 H-Bridge
                        |
                        └── 4x Solenoids (H-bridge pairs)
                             |
                             └── Octopus 1012 Hydraulic Pump
                                  |
                                  └── Hydraulic Steering Ram
```

### Data Flow

**GPS/Wind to Autopilot:**
1. GPS receiver → Lysmarine Pi 4
2. SignalK processes and broadcasts NMEA data
3. Tinypilot Pi Zero receives GPS/wind via TCP
4. Pypilot uses data for GPS/Wind autopilot modes

**Autopilot Control:**
1. User commands via OpenCPN pypilot plugin or Tinypilot web interface
2. Commands sent to pypilot server (TCP 20220)
3. Pypilot PID controller calculates steering corrections
4. GPIO signals to IBT-2 motor controller
5. Motor controller drives solenoid pairs
6. Hydraulic pump adjusts steering

**Status Monitoring:**
1. Pypilot broadcasts heading, rudder angle, autopilot status
2. OpenCPN pypilot plugin displays real-time status
3. SignalK distributes data to other marine instruments

## Key Features

### Reliability
- **Standalone Operation**: Tinypilot operates independently in Compass mode without network, GPS, or Pi 4
- **RAM-based OS**: Tinypilot runs entirely from RAM after boot—safe power disconnection, no SD card corruption
- **Dual-System Redundancy**: Navigation computer failure doesn't affect autopilot operation
- **Minimal Power**: Pi Zero consumes ~200mA (2.4W) for extended offshore passages

### Safety
- **Network Independence**: Core steering function never depends on WiFi connectivity
- **Rudder Feedback**: Continuous position monitoring prevents rudder runaway
- **Current Limiting**: Motor controller monitors and limits hydraulic pump current
- **Manual Override**: Hydraulic steering allows instant manual override at helm
- **Fuse Protection**: Inline fuses protect against electrical faults

### Flexibility
- **Multiple Control Interfaces**:
  - OpenCPN pypilot plugin (graphical, route integration)
  - Tinypilot web interface (http://192.168.43.101)
  - Optional RF remote control
  - Optional GPIO physical buttons
  - Optional IR remote
- **Multiple Heading Modes**: Compass, GPS track, Wind angle, True wind, Route following
- **Tack/Jibe Commands**: Automated sailing maneuvers with configurable angles
- **Custom Python Scripts**: Full Python API for advanced automation

## Installation Overview

### Phase 1: Hardware Installation
1. Mount Raspberry Pi Zero W near compass location (away from magnetic interference)
2. Install pypilot IMU with proper orientation and calibration access
3. Mount IBT-2 motor controller near hydraulic pump
4. Wire solenoids in H-bridge configuration to IBT-2 outputs
5. Install rudder feedback sensor on rudder shaft or hydraulic ram
6. Run power wiring with appropriate fusing (20-30A)
7. Connect motor controller to Pi Zero GPIO pins

### Phase 2: Tinypilot Software Setup
1. Flash Tinypilot image to Pi Zero SD card
2. Configure WiFi client mode for phone hotspot
3. Connect to Tinypilot web interface for initial setup
4. Configure motor controller parameters (solenoid/bang-bang mode)
5. Calibrate IMU (compass, accelerometer, alignment)
6. Configure rudder feedback sensor range and calibration
7. Tune PID parameters for hydraulic system response

### Phase 3: Lysmarine Integration
1. Verify Lysmarine Pi 4 connects to phone hotspot
2. Install OpenCPN pypilot plugin
3. Configure plugin to connect to Tinypilot IP (192.168.43.101:20220)
4. Configure SignalK to broadcast GPS data to Tinypilot
5. Test GPS and Wind autopilot modes

### Phase 4: Testing and Tuning
1. Dockside testing: verify motor controller response
2. Motoring trials: test compass mode stability
3. Sailing trials: tune PID gains for sea conditions
4. Advanced mode testing: GPS track following, wind modes
5. Emergency procedures: verify manual override and fail-safe behavior

## Repository Contents

- `/docs/` - Detailed installation guides and wiring diagrams
- `/config/` - Sample pypilot configuration files
- `/scripts/` - Python utilities for custom solenoid control and testing
- `/hardware/` - Hardware specifications, component datasheets, and schematics
- `/calibration/` - Calibration procedures and reference data

## Configuration Notes

### Motor Controller Settings
```python
# Pypilot servo configuration for solenoid H-bridge
servo.mode = 'solenoid'  # or bang-bang control for on/off solenoids
servo.max_current = 15-20  # Amps, tune to hydraulic pump draw
servo.max_controller_temp = 60  # Celsius
servo.use_eeprom = true  # Save calibration to motor controller
```

### Network Configuration
```
# /etc/wpa_supplicant/wpa_supplicant.conf on Tinypilot
country=AU
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YachtArion"
    psk="your_hotspot_password"
    priority=10
}
```

## Failsafe Behavior

| Component Failure | Autopilot Status | Available Modes | Notes |
|------------------|------------------|-----------------|-------|
| Phone hotspot offline | **Continues normally** | Compass only | No GPS/Wind/NAV modes |
| Lysmarine Pi 4 offline | **Continues normally** | Compass only | No OpenCPN integration |
| Both network systems offline | **Continues normally** | Compass only | Use RF remote or GPIO buttons |
| Pi Zero power loss | **Stops immediately** | None | Manual steering required |
| Motor controller fault | **Stops immediately** | None | Check fuses and connections |

**Critical Safety Note**: Compass mode is fully standalone and requires only the Pi Zero, IMU, motor controller, and rudder feedback sensor. Network connectivity is optional for advanced features.

## Performance Characteristics

- **Heading Hold Accuracy**: ±2-5° (dependent on sea state and PID tuning)
- **Rudder Response Time**: ~1-3 seconds (hydraulic system dependent)
- **Power Consumption**: 
  - Pi Zero: ~2.4W (200mA @ 12V)
  - Pi 4: ~7.5W (625mA @ 12V) 
  - Hydraulic pump: 180-360W peak (15-30A @ 12V)
- **IMU Update Rate**: 10-20 Hz
- **Control Loop Frequency**: 10 Hz

## Contributing

This is a personal project documentation repository, but contributions, suggestions, and experience reports from similar installations are welcome. Please open an issue for discussion before submitting pull requests.

## Resources

### Official Documentation
- [Pypilot Official Documentation](https://pypilot.org/doc/pypilot_user_manual/)
- [OpenPlotter Pypilot Documentation](https://openplotter.readthedocs.io/latest/pypilot/pypilot_app.html)
- [Lysmarine (BBN OS) Documentation](https://bareboat-necessities.github.io/my-bareboat/)
- [Tinypilot Information](https://pypilot.org)

### Community Forums
- [OpenMarine Forum - Pypilot Section](https://forum.openmarine.net/forumdisplay.php?fid=17)
- [Pypilot GitHub Discussions](https://github.com/pypilot/pypilot/discussions)

### Hardware Datasheets
- [IBT-2 Motor Controller (BTS7960B)](https://pypilot.org/schematics/hbridge_datasheet.htm)
- Octopus 1012 Hydraulic Pump Specifications
- TQM AP8 Solenoid Specifications

## License

This documentation is released under MIT License. Pypilot software is licensed under GPLv3.

## Acknowledgments

- Sean d'Epagnier - Creator and primary developer of pypilot
- OpenMarine community - Ongoing support and development
- Bareboat Necessities team - Lysmarine OS development
- The broader open-source marine navigation community

---

**Project Status**: Planning and hardware acquisition phase (January 2026)

**Maintainer**: botheredbybees

**Vessel**: SY Arion (36ft)

**Location**: Cygnet, Tasmania, Australia
