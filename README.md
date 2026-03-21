
=Pypilot for Arion=
Open-source autopilot and integrated marine data network for the 36ft yacht Arion. This project utilizes a distributed "Tri-Pi" architecture to provide high-reliability steering, ultrasonic wind sensing, and professional-grade data logging.
Project Overview
The system replaces a legacy TQM AP8 autopilot with a modern solid-state solution and integrates an ultrasonic wind station. It is split across three dedicated nodes to ensure that navigation or sensor failures do not impact core steering reliability.
 * Autopilot (Pi 3B): Dedicated pypilot server for hydraulic steering.
 * Navigation & Hub (Pi 4): Central "brain" for charts, Signal K, and InfluxDB/Grafana logging.
 * Wind Bridge (Pi Zero WX): Remote solar-powered node for the WS80 ultrasonic sensor.
Technology Stack
Hardware
1. Autopilot System (The "Steering Node")
 * Computer: Raspberry Pi 3B (OpenPlotter 4.x).
 * Power: Permanent 12V DC via dedicated Buck Converter (required for 5V stability and to prevent CPU throttling).
 * IMU: ICM-20948 9-axis sensor at I2C address 0x68.
 * Motor Controller: Arduino Nano running motor.ino (v38400 × 4 baud).
 * H-Bridge: IBT-2 (Dual BTS7960B) driving an Octopus Model 1012 Hydraulic Pump.
 * GPS: Dedicated USB GPS (NMEA 0183) for standalone "GPS Track" mode.
2. Navigation & Hub (The "Analysis Node")
 * Computer: Raspberry Pi 4 (8GB RAM).
 * Storage: 512GB SSD (crucial for high-frequency InfluxDB writes).
 * Case: Argon ONE V2 Aluminium Case (passive cooling).
 * OS: Lysmarine (BBN OS).
 * Display: Kiosk-mode Articboard (AvNav) dashboard for cockpit instruments.
3. Wind Bridge (The "Sensor Node")
 * Computer: Raspberry Pi Zero WX.
 * Sensor: Ecowit WS80 Ultrasonic 6-in-1 (Wind, Temp, Humidity, Solar, UV).
 * Integration: 433MHz SDR receiver decoding via rtl_433 and pushing data to the Hub via MQTT.
Network Architecture
Both the Steering Node and the Wind Bridge operate as clients to the Pi 4 Hub.
 * SSID: YachtArion (EZR23 4G Router).
 * Pi 4 (Hub): 192.168.20.101 (Signal K, InfluxDB, Grafana).
 * Pi 3B (Pilot): 192.168.20.100 (Pypilot).
 * Pi Zero (Wind): Managed via MQTT bridge.
Software & Data Integration
Signal K & Derived Data
The Pi 4 acts as the master Signal K server, performing complex vector mathematics to provide:
 * Apparent Wind: Received via MQTT from the Pi Zero.
 * Heading: Received via Pypilot TCP (Port 20220) from the Pi 3B.
 * Ground Wind: Calculated using GPS SOG/COG.
 * True Wind: Calculated using Heading + SOG + Apparent Wind.
Data Logging (The "Research Vessel" Stack)
Reflecting professional standards (RSV Nuyina / RV Investigator), Arion utilizes a dedicated logging stack:
 * Database: InfluxDB 1.8.
 * Retention Policy: one_year (52-week) default policy to protect SSD longevity while maintaining seasonal trends.
 * Visualization: Grafana (Port 3080).
 * Key Metrics: * Wind triangles (Apparent vs. True).
   * System Health (Voltage, CPU Temp, Throttling status).
   * WS80 Battery Health (sensors.ws80.raw_voltage).
Updated Installation & Configuration Notes
1. Power Stability (The "Throttling" Fix)
Testing revealed that the RPi 3B requires a highly stable 5V supply to prevent the IMU from outputting false values. A dedicated Buck Converter is mandatory; standard micro-USB phone chargers are insufficient for the current spikes required by the IBT-2/Arduino serial communication.
2. Derived Data Plugin Setup
To ensure True Wind and Ground Wind appear on the dashboard:
 * Install signalk-derived-data via the Appstore.
 * Enable Ground Wind (requires SOG + Heading).
 * Enable Magnetic to True conversion (requires GPS for Variation calculation).
 * If STW (Speed Through Water) is unavailable, map SOG to STW to enable traditional True Wind calculations.
3. InfluxDB Retention Setup
To prevent the 512GB SSD from filling with high-frequency telemetry, the following retention policy is applied via the Influx CLI:
CREATE RETENTION POLICY "one_year" ON "signalk" DURATION 52w REPLICATION 1 DEFAULT

4. Kiosk Dashboard (Articboard)
The cockpit display runs Articboard/AvNav in a locked kiosk mode.
 * Access Editor: Via laptop at http://192.168.20.101:8080.
 * Primary Instruments: Heading (Magnetic), SOG (Knots), AWA (Apparent Wind Angle), and TWD (True Wind Direction).
Project Status
 * Hardware: 3-node Pi network established. Power delivery upgrades in progress.
 * Data: MQTT Wind-to-SignalK bridge functional.
 * Logging: InfluxDB/Grafana stack active with 1-year retention.
 * Next Phase: Calibration of WS80 ultrasonic offset and PID tuning for hydraulic pump response.
Last Updated: March 19, 2026
Location: Cygnet, Tasmania, Australia
Maintainer: Peter Shanks (botheredbybees)
