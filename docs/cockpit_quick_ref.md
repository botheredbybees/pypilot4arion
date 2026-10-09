# Cockpit Quick Reference Guide

**Network**: `YachtArion` | **Pass**: [YourPassword]
**Pypilot (Steering Pi 3B)**: `http://192.168.20.100:8000` | **Signal K (Hub)**: `http://192.168.20.101:3000`

---

## 1. Power Up Sequence
1.  **Main Switch**: Turn **ON** (Red Key).
2.  **Instruments**: Switch **Instruments** breaker ON at panel.
3.  **Wait**: 60 seconds for Wi-Fi and GPS lock.
4.  **Verify**: Check OpenCPN for "Green Boat" icon (GPS active).

## 2. The Pilot Controls (web UI only)
There are **no physical buttons** on Arion. The pilot is controlled from the web UI on a phone or tablet on the YachtArion WiFi:
`http://192.168.20.100:8000` -> **Control** tab.

| Control | What it does |
|---|---|
| **Heading** / **Command** | Current heading, and the heading the pilot is trying to hold |
| **Mode** drop-down | Steering mode. Only modes with working sensors are listed: `compass` always; `gps` with a GPS fix; `wind` with wind data; `true wind` with wind + GPS; `nav` with a route feed |
| **AP** toggle | **Engages** (target = your *current* heading) or, tapped again, **disengages** to standby |
| `10` `1` / `1` `10` (engaged) | Change course by 1 or 10 degrees to port (left pair) or starboard (right pair). In wind modes the sign is reversed |
| `<<` `<` `>` `>>` (standby) | **Hold to drive the rudder manually**; it stops when you let go. `\|` centres the rudder |
| **Tack** (engaged) | Starts a tack; tap again to cancel |

## 3. Auto Steering (Compass Mode)
*   **Engage**: Point the boat on the desired heading and steady the helm. Select **compass** in the mode drop-down, then tap **AP**.
*   **Adjust**: Use the `1` buttons for fine changes (dodging debris) and the `10` buttons for course changes.
*   **Disengage**: Tap **AP** again (standby). **Take the helm immediately.**

## 4. Wind Steering (Wind Mode)
*   **Pre-Req**: Wind data must be reaching pypilot. If **wind** is missing from the mode drop-down, pypilot has no wind data: check the wind node (`arion-wx`) and Signal K.
*   **Engage**: Sail close-hauled or on a reach, select **wind**, then tap **AP**.
*   **Note**: The boat steers to hold the current wind angle. Watch for gybes if running deep downwind!

## 5. Route Following (nav / gps Mode)
1.  **OpenCPN**: Right-click a route -> "Activate Route".
2.  **Pypilot**: Select **nav** (or **gps**) in the mode drop-down, then tap **AP**. If neither is listed, pypilot is not receiving a route/GPS feed.
3.  **Monitor**: Ensure the boat tracks the line. Watch for XTE (Cross Track Error).
*   **Set up and verified 2026-10-08 (not yet tried underway):** OpenCPN sends APB to pypilot (`192.168.20.100:20220`), so **nav** appears in the mode list once a route is activated. Test it at the dock with the helm manned before relying on it. The OpenCPN connection changed on 2026-10-10 (now also reads pypilot's stream), so confirm **nav** still appears the next time a route is active. Details: `docs/data_flows.md` (Route following).

## 6. Trolling Motor (Propulsion)
1.  **Deploy**: Lower motor into water. Lock depth collar.
2.  **Power**: Switch **Propulsion** breaker ON (12V Bus).
3.  **Throttle**: Use remote/tiller to advance speed slowly.
    *   *Warning*: Monitor Battery Voltage. Stop if < 11.5V.

---

**Emergency Disengage**: Turn Hydraulic Bypass Valve **CCW**.
