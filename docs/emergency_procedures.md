# Emergency Procedures & Failure Modes

**STATUS: CRITICAL** - Print this document and keep it in the chart table.

## 1. Autopilot Failure (Loss of Steering)

**Symptoms**: Boat wanders off course, rudder unresponsive to "Auto" commands, or continuous beeping.

### Immediate Action: Manual Override
1.  **Disengage**: Press the **STANDBY** button on the cockpit control (if available) or Web UI.
2.  **Hydraulic Bypass**:
    *   Locate the **Bypass Valve** on the Octopus hydraulic pump.
    *   Turn the valve **Open** (Counter-Clockwise) to allow free flow of fluid.
3.  **Steer Manually**: Use the ship's wheel. The helm should feel lighter with the bypass open.

### Troubleshooting at Sea
1.  **Check Power**: Is the TinyPilot Pi Zero Green LED on?
    *   *No*: Check fuse in **Bus B (Regulated)** panel.
    *   *Yes*: Try a software reboot via `http://192.168.43.101` -> Configuration -> System -> Reboot.
2.  **Check Drive**:
    *   Listen for the pump motor whirring.
    *   If motor runs but rudder doesn't move: Check fluid level / Air in lines.
    *   If motor silent: Check **Bus C (High Current)** fuse for the IBT-2 controller.

## 2. Total Power Failure (Blackout)

**Symptoms**: No lights, instruments, or autopilot.

### Diagnosis
1.  **Check Voltmeter**: Read voltage at the **24V Bus A**.
    *   *Below 22V*: Battery bank is flat.
    *   *Normal (24V+)*: Main fuse/breaker has tripped.
2.  **Check Main Breaker**: Locate the 250A Main Fuse/Breaker near the Battery Bank.
    *   *Tripped?*: Reset ONCE. If it trips immediately, **STOP**. You have a dead short.
    *   *Intact?*: Check main isolation switch.

### Emergency Lighting
*   Use standalone battery torches.
*   The **Engine Start System (Bus C)** is isolated and should still function to start the engine, providing alternator power.

## 3. Engine Start Failure

If the 12V Start Battery is dead:

### Jump Start Procedure (Hybrid Bridge)
1.  **Confirm**: 24V House Bank has charge.
2.  **Engage**: Switch on the **12V Start-Boost DC-DC Converter** (Bridge).
3.  **Wait**: Allow 5-10 minutes for the Start Battery to surface charge.
4.  **Disconnect House Loads**: Turn off Fridge, Autopilot, Inverter to maximize available stability.
5.  **Crank**: Attempt to start engine.

## 4. Fire / Smoke

1.  **ISOLATE BATTERIES**: Turn OFF the **Main Battery Switches** (House & Start) immediately.
    *   *Location*: Under companionway steps / Nav station.
2.  **Extinguish**: Use ABC Fire Extinguisher. Do **NOT** use water on electrical fires.
3.  **Assess**: Do not restore power until the melted wire/component is identified and disconnected.
