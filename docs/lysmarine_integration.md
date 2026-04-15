# Lysmarine Integration Guide

## Overview

**Lysmarine** (also known as **BBN OS** or Bareboat Necessities) is the operating system running on the **Navigation Computer** (Raspberry Pi 4 8GB). It is a comprehensive marine Linux distribution based on Raspberry Pi OS, pre-loaded with open-source navigation tools.

On *Arion*, Lysmarine serves as the **Command Center**. Unlike the TinyPilot (which headless and focused solely on steering), Lysmarine provides:
1.  **Visual Navigation**: Electronic Chart Display & Information System (ECDIS) via **OpenCPN**.
2.  **Data Hub**: Multiplexing NMEA data, Signal K server, and sensor integration.
3.  **User Interface**: The primary way you interact with the autopilot for route planning and monitoring.

## Software Stack

### 1. OpenCPN
The primary chartplotter application.
*   **Role**: Displays charts, routes, AIS targets, and the pypilot control dashboard.
*   **Integration**: Connects to the TinyPilot via the **Pypilot Plugin** to send headings/routes and receive status.

### 2. Signal K Server
The central nervous system for marine data.
*   **Role**: Ingests data from NMEA 0183 (GPS), NMEA 2000 (future), and I2C/GPIO sensors.
*   **Integration**: Can receive autopilot data from TinyPilot and broadcast it to other devices (phones, tablets) on the `YachtArion` network.

## System Architecture

The Lysmarine Pi 4 sits on the **YachtArion** WiFi network alongside the TinyPilot Pi Zero.

*   **Network Role**: WiFi Client
*   **Gateway**: Pixel 2 Phone (192.168.43.1)
*   **Target IP**: 192.168.43.100 (Recommended Static IP)

## Setup Instructions

### 1. Network Configuration
Lysmarine needs to connect to the `YachtArion` hotspot to communicate with the TinyPilot.

1.  Boot the Raspberry Pi 4.
2.  Click the Network icon in the top right system tray.
3.  Select **YachtArion**.
4.  Enter the password.
5.  *Verification*: Open a terminal and ping the TinyPilot:
    ```bash
    ping 192.168.43.101
    ```

### 2. OpenCPN Pypilot Plugin Setup
To control the autopilot from the chartplotter:

1.  Open **OpenCPN**.
2.  Go to **Options -> Plugins**.
3.  Install/Enable the **Pypilot** plugin (if not already installed).
4.  Open the Pypilot plugin preferences.
5.  **Configuration**:
    *   **Host**: `192.168.43.101` (The IP of the TinyPilot Pi Zero)
    *   **Port**: `20220` (Default pypilot control port)
6.  Click **Apply/OK**.
7.  A "Pypilot" floating window should appear in OpenCPN showing Heading, Rudder Angle, and large control buttons.

### 3. Signal K Configuration (Optional)
If you want to view autopilot data in Signal K (e.g., for WilhelmSK or a web dashboard):

1.  Open a browser to `localhost:3000` (Signal K Admin).
2.  Go to **Server -> Data Connections**.
3.  Add a new connection:
    *   **Type**: Pypilot
    *   **Host**: `192.168.43.101`
    *   **Port**: `20220`
4.  Restart Signal K Server.
5.  You should now see `navigation.headingMagnetic` and `steering.rudderAngle` updates in the Data Browser.

## Usage Workflow

1.  **Power Up**: Turn on the Pixel 2 Hotspot, then the 12V system (powering both Pis).
2.  **Verify**: Wait for both Pis to boot (~30-60 secs).
3.  **Navigation**: Launch OpenCPN on the Pi 4.
4.  **Engage**:
    *   Steer manually to course.
    *   Click **AUTO** on the OpenCPN Pypilot dashboard.
    *   TinyPilot takes over steering.
5.  **Route Following (NAV Mode)**:
    *   Activate a Route in OpenCPN.
    *   Click **NAV** on the Pypilot dashboard.
    *   TinyPilot will steer to follow the active route.

## Troubleshooting

*   **"Pypilot Disconnected" in OpenCPN**:
    *   Check if Pi 4 is connected to `YachtArion` WiFi.
    *   Ping `192.168.43.101` from Pi 4 terminal.
    *   Verify TinyPilot is powered (Green LED on Pi Zero).
*   **Laggy Charts**: Ensure the Pi 4 has adequate cooling (Argon ONE case fan active).

---

**Related Documentation**:
*   [TinyPilot Setup Guide](tinypilot_setup.md) - The autopilot core this system controls.
*   [System Overview](../README.md) - Full network topology.
