# Cockpit Quick Reference Guide

**Network**: `YachtArion` | **Pass**: [YourPassword]
**TinyPilot**: `http://192.168.43.101`

---

## 1. Power Up Sequence
1.  **Main Switch**: Turn **ON** (Red Key).
2.  **Instruments**: Switch **Instruments** breaker ON at panel.
3.  **Wait**: 60 seconds for Wi-Fi and GPS lock.
4.  **Verify**: Check OpenCPN for "Green Boat" icon (GPS active).

## 2. Auto Steering (Compass Mode)
*   **Engage**: Point boat on desired heading. Steady the helm. Press **AUTO**.
*   **Adjust**:
    *   **+1 / -1**: Fine adjustment (Dodge debris).
    *   **+10 / -10**: Course change (Tacking).
*   **Disengage**: Press **STANDBY**. **Take helm immediately.**

## 3. Wind Steering (Wind Mode)
*   **Pre-Req**: Ensure wind data is valid in OpenCPN.
*   **Engage**: Sail close-hauled or on reach. Press **WIND**.
*   **Note**: Boat will steer to maintain Apparent Wind Angle (AWA). Watch for gybes if running deep downwind!

## 4. Route Following (GPS Mode)
1.  **OpenCPN**: Right-click a route -> "Activate Route".
2.  **Pypilot**: Press **NAV** / **GPS**.
3.  **Monitor**: Ensure boat tracks the line. Watch for XTE (Cross Track Error).

## 5. Trolling Motor (Propulsion)
1.  **Deploy**: Lover motor into water. Lock depth collar.
2.  **Power**: Switch **Propulsion** breaker ON (24V Bus).
3.  **Throttle**: Use remote/tiller to advance speed slowly.
    *   *Warning*: Monitor Battery Voltage. Stop if < 23.0V.

---

**Emergency Disengage**: Turn Hydraulic Bypass Valve **CCW**.
