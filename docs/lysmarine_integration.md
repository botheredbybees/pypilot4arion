# Lysmarine Integration Guide

> Partly superseded: this guide predates the current layout (TinyPilot Pi Zero, phone hotspot on 192.168.43.x). Current: Lysmarine is the **hub** (Pi 4, `lysmarine`, 192.168.20.101, on the EZR23 router); pypilot runs on the **steering node** (Pi 3B, `arionpypilot`, 192.168.20.100). Data flows (Signal K, gpsd, OpenCPN): see [data_flows.md](./data_flows.md).

## Overview

**Lysmarine** (also known as **BBN OS** or Bareboat Necessities) is the operating system running on the **Navigation Computer** (Raspberry Pi 4 8GB). It is a comprehensive marine Linux distribution based on Raspberry Pi OS, pre-loaded with open-source navigation tools.

On *Arion*, Lysmarine serves as the **Command Center**. Unlike the steering node `arionpypilot` (headless and focused solely on steering), Lysmarine provides:
1.  **Visual Navigation**: Electronic Chart Display & Information System (ECDIS) via **OpenCPN**.
2.  **Data Hub**: Multiplexing NMEA data, Signal K server, and sensor integration.
3.  **User Interface**: The primary way you interact with the autopilot for route planning and monitoring.

## Software Stack

### 1. OpenCPN
The primary chartplotter application.
*   **Role**: Displays charts, routes, AIS targets, and the pypilot control dashboard.
*   **Integration**: Takes GPS from the hub's local gpsd (`127.0.0.1:2947`). OpenCPN runs as the Lysmarine desktop user `user` (config `/home/user/.opencpn/opencpn.conf`), not `bbb`. If the Pypilot plugin is used, it must point at the steering node (192.168.20.100); that setup is unverified.

### 2. Signal K Server
The central nervous system for marine data.
*   **Role**: Ingests data from NMEA 0183 (GPS), NMEA 2000 (future), and I2C/GPIO sensors.
*   **Integration**: Reads pypilot data from the steering node (provider `Pypilot_Raw_Data`, TCP 192.168.20.100:20220) and broadcasts it to other devices (phones, tablets) on the `YachtArion` network.

## System Architecture

The Lysmarine Pi 4 sits on the **YachtArion** WiFi network alongside the steering node (Pi 3B) and the wind bridge (Pi Zero WX).

*   **Network Role**: WiFi Client
*   **Gateway**: EZR23 router (192.168.20.1)
*   **IP**: 192.168.20.101
*   **Local pypilot must stay disabled**: Lysmarine ships its own pypilot (0.56: `pypilot@pypilot.service`, `pypilot_web.service` on port 8080, `pypilot_detect.service`). It reads gpsd and publishes a competing `pypilot` position into Signal K. These were disabled on 2026-10-07; do not re-enable them. The real pypilot is on the steering node.

## Setup Instructions

### 1. Network Configuration
Lysmarine needs to connect to the `YachtArion` network to communicate with the steering node.

1.  Boot the Raspberry Pi 4.
2.  Click the Network icon in the top right system tray.
3.  Select **YachtArion**.
4.  Enter the password.
5.  *Verification*: Open a terminal and ping the steering node:
    ```bash
    ping 192.168.20.100
    ```

### 2. OpenCPN Pypilot Plugin Setup
To control the autopilot from the chartplotter:

1.  Open **OpenCPN**.
2.  Go to **Options -> Plugins**.
3.  Install/Enable the **Pypilot** plugin (if not already installed).
4.  Open the Pypilot plugin preferences.
5.  **Configuration**:
    *   **Host**: `192.168.20.100` (the steering node, Pi 3B)
    *   **Port**: `20220` (pypilot NMEA TCP port; whether the plugin expects this port is unverified)
6.  Click **Apply/OK**.
7.  A "Pypilot" floating window should appear in OpenCPN showing Heading, Rudder Angle, and large control buttons.

### 3. Signal K Configuration
Signal K already has the pypilot connection configured (see [data_flows.md](./data_flows.md)); do not add a duplicate.

1.  Open a browser to `localhost:3000` (Signal K Admin).
2.  Go to **Server -> Data Connections** and confirm `Pypilot_Raw_Data` (TCP `192.168.20.100:20220`) is enabled. `pypilot_nmea` is a disabled duplicate; leave it off.
3.  GPS comes from `local_gpsd` (source `local_gpsd.GN`).
4.  You should see `navigation.headingMagnetic` and `steering.rudderAngle` updates in the Data Browser.

## Usage Workflow

1.  **Power Up**: Turn on the 12V system (router and all Pis).
2.  **Verify**: Wait for the Pis to boot (~30-60 secs).
3.  **Navigation**: Launch OpenCPN on the Pi 4.
4.  **Engage**:
    *   Steer manually to course.
    *   Click **AUTO** on the OpenCPN Pypilot dashboard.
    *   The steering node takes over steering.
5.  **Route Following (NAV Mode)**:
    *   Activate a Route in OpenCPN.
    *   Click **NAV** on the Pypilot dashboard.
    *   The steering node will steer to follow the active route.

## Troubleshooting

*   **"Pypilot Disconnected" in OpenCPN**:
    *   Check if Pi 4 is connected to `YachtArion` WiFi.
    *   Ping `192.168.20.100` from Pi 4 terminal.
    *   Verify the steering node (Pi 3B) is powered and `pypilot` is running.
*   **Laggy Charts**: Ensure the Pi 4 has adequate cooling (Argon ONE case fan active).

---

**Related Documentation**:
*   [TinyPilot Setup Guide](archive/tinypilot_setup.md) - Legacy; describes the abandoned Pi Zero pilot.
*   [System Overview](../README.md) - Full network topology.
