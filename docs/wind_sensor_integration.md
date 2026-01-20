# Wind Sensor Integration Guide

## Overview

This guide documents the integration of the **Ecowit WS80** ultrasonic anemometer into the *Arion* navigation system. Unlike traditional wired marine wind sensors, the WS80 is wireless (433MHz), solar-powered, and ultra-low maintenance (no moving parts).

We use a Software Defined Radio (RTL-SDR) on the Lysmarine Pi 4 to receive the sensor's data, decode it, and inject it into the Signal K server. Pypilot then consumes this data to enable **Wind Mode** steering.

## Hardware Stack

1.  **Sensor**: Ecowit WS80 6-in-1 Ultrasonic Sensor (Solar powered, 4.8s update rate).
2.  **Receiver**: Generic RTL-SDR V3/V4 USB Dongle with 433MHz antenna.
3.  **Computer**: Raspberry Pi 4 (Lysmarine).

## Software Stack

1.  **rtl_433**: Command-line tool to decode 433MHz signals.
2.  **Signal K**: The central data hub that converts the `rtl_433` JSON output into standard marine Signal K delta messages.
3.  **Pypilot**: Consumes Signal K wind data for steering.

## Installation & Configuration

### 1. Hardware Setup
1.  Mount the **WS80** at the masthead or a high, unobstructed location. Align the "North" marker correctly towards the bow (you can offset this in software later, but physical alignment is best).
2.  Plug the **RTL-SDR USB dongle** into the Lysmarine Pi 4.
3.  Attach the 433MHz antenna to the dongle.

### 2. Install rtl_433
On the Lysmarine Pi 4, open a terminal:

```bash
sudo apt-get update
sudo apt-get install rtl_433
```

Test reception:
```bash
# Listen for Ecowit protocol usually on 433.92MHz
rtl_433 -f 433.92M -R 156
```
*   Wait up to 16 seconds. You should see a JSON output with `wind_avg_km_h`, `wind_dir`, etc.
*   **Note the ID**: Write down the `id` field from the output (e.g., `12345`). You'll use this to filter out neighbor's sensors.

### 3. Connect to Signal K
There are two common ways to pipe data into Signal K: via **MQTT** or via the **Signal K plugin**. The Plugin method is often easier for beginners.

#### Method A: Signal K RTL_433 Plugin (Recommended)
1.  Open Signal K Admin (`http://localhost:3000`).
2.  Go to **Appstore -> Available**.
3.  Search for and install `signalk-rtl433`.
4.  Restart Server.
5.  Go to **Server -> Plugin Config -> RTL_433**.
6.  **Configuration**:
    *   **Frequency**: `433920000`
    *   **Protocols**: `156` (Ecowit)
    *   **Device ID**: Enter your sensor's ID (to ignore stray signals).
7.  Save and Enabled.

#### Method B: Command Line Pipe (Advanced)
If you prefer a robust background service:
Create a service that runs:
```bash
rtl_433 -f 433.92M -R 156 -F json | curl -X POST -H "Content-Type: application/json" -d @- http://localhost:3000/signalk/v1/api/vessels/self
```
*(Note: Method A involves less maintenance)*

### 4. Verify Data in Signal K
Go to the **Data Browser** in Signal K Admin. Look for:
*   `environment.wind.speedApparent`
*   `environment.wind.angleApparent`

If these values are updating every ~4.8 seconds, integration is successful.

## Pypilot Configuration

Now that Signal K has the wind data, Pypilot needs to see it.

1.  Ensure Pypilot is connected to Signal K (this usually happens automatically via mDNS/Discovery on the same network).
2.  In **OpenCPN**, enable the Pypilot dashboard.
3.  You should now see the "Wind" button become active (no longer greyed out).
4.  **Wind Mode**:
    *   Click **WIND**.
    *   Pypilot will now steer to maintain a constant Apparent Wind Angle (AWA).

## Troubleshooting

*   **No Signal**:
    *   Check antenna connection.
    *   Verify you are using the correct frequency (433MHz vs 915MHz - depends on region/model). US/Aus models are often 915MHz, EU is 433MHz. Check your WS80 sticker!
    *   If 915MHz, change `rtl_433` command to `-f 915M`.
*   **Wrong Direction**:
    *   If the wind angle is consistently off (e.g., shows 180° when head-to-wind), adjust the Offset in Signal K (Server -> Data -> Derived Data -> Offset not usually available directly, use a "Calibration" plugin in Signal K).

---
**Related Documentation**:
*   [Lysmarine Integration](lysmarine_integration.md) - The host system for RTL-SDR.
*   [System Overview](../README.md)
