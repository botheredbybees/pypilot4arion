# Pre-Flight Checklist — SY Arion

Use this document before every departure. Work through each section in order. For abort/emergency steps see [`emergency_procedures.md`](emergency_procedures.md).

> [!NOTE]
> Print this document and keep a copy at the nav station.

---

## 1. Physical Pre-Power Checks

Complete these before touching any switch or breaker.

- [ ] **House battery isolator** — switch ON
- [ ] **Start battery isolator** — switch ON
- [ ] **Bilge** — no standing water; float switch moves freely
- [ ] **No smell** of burning or fuel in bilge, nav station, or lazarette
- [ ] **Hydraulic bypass valve** — CLOSED (turn clockwise; tiller handle aligned fore-aft). *Open valve = rudder freewheels, autopilot cannot steer.*
- [ ] **Arduino Nano USB cable** — seated firmly in Pi 3B USB port
- [ ] **D6 jumper wire** on Arduino Nano — grounded (H-bridge mode). *Missing jumper = RC servo PWM output only; pump will not run.*
- [ ] **All breakers OFF** before energising main switch (clean start)

---

## 2. Power-Up Sequence

| Step | Action | Wait | Verify |
|:----:|--------|------|--------|
| 1 | Turn **Main Battery Switch** ON | — | Voltmeter at panel reads **≥ 12.4 V** |
| 2 | Power ON **EZR23 Router** | 60 s | `YachtArion` SSID visible on phone/tablet |
| 3 | Switch **Instruments** breaker ON | 90 s | Pi 3B green LED steady; Pi 4 green LED steady |
| 4 | Open browser → **Pypilot web** | — | `http://192.168.20.100:8000` loads and shows heading |
| 5 | Open browser → **Signal K** | — | `http://192.168.20.101:3000` loads |
| 6 | Wait for **GPS fix** | 2–5 min | Pypilot heading stable; OpenCPN shows green boat icon |
| 7 | Confirm **wind data** flowing | — | Signal K Data Browser: `environment.wind.speedApparent` updating |
| 8 | Check **MPPT controller** (daylight only) | — | iTechworld display shows PV input > 0 W |

*IP reference: Pi 3B Steering/Pypilot = `192.168.20.100` · Pi 4 Hub/Signal K = `192.168.20.101`*

---

## 3. Go / No-Go Gate

Do not depart under autopilot until all applicable boxes are checked.

- [ ] Pypilot web accessible — IMU status shows **"Calibrated"**
- [ ] Battery voltage **≥ 12.4 V** resting (check before engine start)
- [ ] `servo.current` reading **< 5 A** at rest in Pypilot scope
- [ ] **Hydraulic test** — turn wheel manually; rudder responds immediately and smoothly
- [ ] **Engage / disengage test** — engage autopilot in STANDBY mode briefly, confirm STANDBY disengages cleanly
- [ ] **GPS fix acquired** *(required for GPS or NAV mode)*
- [ ] **Wind data flowing** *(required for Wind mode)*

> For full autopilot tuning verification (PID profile, rudder calibration, slew rate) see [`testing_and_tuning.md`](testing_and_tuning.md) — Pre-Passage Checklist.

---

## 4. Shutdown Sequence

1. Press **STANDBY** — confirm autopilot disengaged
2. Close OpenCPN and any browser sessions
3. Switch **Instruments** breaker OFF
4. Power OFF **EZR23 Router**
5. Turn **Main Battery Switch** OFF
   - *Exception: leave ON if solar charging is active and boat is unattended at dock.*

---

## 5. Troubleshooting Quick-Reference

| Symptom | First check | Reference |
|---------|-------------|-----------|
| `YachtArion` SSID not visible after 60 s | Router powered? Check router LED state | [`network_map.md`](network_map.md) |
| Pypilot web won't load | Pi 3B LED on? Try `ping 192.168.20.100` from phone | [`network_map.md`](network_map.md) |
| Signal K / OpenCPN won't load | Pi 4 LED on? Try `ping 192.168.20.101` | [`network_map.md`](network_map.md) |
| IMU shows "Uncalibrated" | First boot after moving Pi? Perform 360° calibration turn in calm water | [`testing_and_tuning.md`](testing_and_tuning.md) |
| No GPS fix after 5 min | USB GPS dongle seated in Pi 3B? Green LED on dongle? | [`testing_and_tuning.md`](testing_and_tuning.md) |
| Rudder does not move | Bypass valve fully closed? Arduino Nano LED on? D6 jumper present? | [`flashing_motor_ino_to_arduino.md`](flashing_motor_ino_to_arduino.md) |
| `servo.current` high at rest (> 5 A) | Bypass valve partially open? Pump running against closed valve? | [`emergency_procedures.md`](emergency_procedures.md) |
| Total power loss | Check voltmeter (≥ 11 V?), then 250 A main fuse near battery bank | [`emergency_procedures.md`](emergency_procedures.md) |

---

**Related documentation:**
- [`cockpit_quick_ref.md`](cockpit_quick_ref.md) — AUTO / WIND / NAV mode quick reference
- [`emergency_procedures.md`](emergency_procedures.md) — Autopilot failure, power failure, fire
- [`network_map.md`](network_map.md) — Full network topology and static IP assignments
- [`battery_system.md`](battery_system.md) — Dual battery system (house + start), VSR, solar/wind charging
- [`testing_and_tuning.md`](testing_and_tuning.md) — Pre-passage autopilot verification and PID tuning
