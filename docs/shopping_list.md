# Project Shopping List

This document consolidates hardware requirements from the **Solar**, **Rewiring**, **TinyPilot**, and **Wind** integration plans.

> [!NOTE]
> Items marked **[Check Inventory]** may already be in your possession (based on uploaded photos). Please verify before purchasing.

## 1. Power System (12V)
*Reference: [12V Solar Design](12v_solar_system.md)*

### Critical
*   [ ] **High-Amp Fuse Holders (ANL or MRBF)**:
    *   1x 100A for Trolling Motor.
    *   1x 100A for Solar Bank Main.
    *   1x 80A for Anchor Winch (if existing breaker is dodgy).
*   [ ] **Battery Cable (Heavy Gauge)**:
    *   Red & Black 2 AWG (35mm²) for Battery Interconnects + Main Feed.
    *   Red & Black 6 AWG (16mm²) for DC-DC Charger runs.

## 2. Wiring & Distribution
*Reference: [House Rewiring Plan](rewiring_house_loads.md)*

### Critical
*   [ ] **Fuses**: Standard ATO/ATC Blade Fuses (Assorted Box: 5A, 10A, 15A, 20A, 30A).
*   [ ] **Heat Shrink Labels**: "Cabin Light", "Nav Light", "Fridge", etc.
*   [ ] **Marine Grade Wire** (Primary Tinned Copper):
    *   100ft Spool of **14 AWG (Red/Black)**: Lighting & Instruments.
    *   20ft Spool of **10 AWG (Red/Black)**: Fridge, Water Pump, Solar inputs.

### Check Inventory (Verify against photos)
*   [ ] **Bus Bars**: You have red/black bus blocks appropriately sized (based on photos). Ensure studs are clean.
*   [ ] **Fuse Blocks**: You have two blocks. Verify they are rated for 32V DC max (Standard).

## 3. Autopilot & Electronics (TinyPilot)
*Reference: [TinyPilot Setup](tinypilot_setup.md)*

### Critical
*   [ ] **12V -> 5V Buck Converter (USB Power)**: Dedicated PSU for Pi 3B & Pi 4.
    *   *Recommendation*: "12V to 5V 3A Micro USB Converter" (Waterproof module). One per Pi.
*   [ ] **Low Voltage Disconnect (LVD) relay module, 10A+**: Inline on the 12V feed to both buck converters.
    *   *Purpose*: Cuts Pi power cleanly if bus voltage sags below ~10.5V (engine cranking, flat battery). Prevents SD card corruption. Reconnects automatically once voltage recovers to ~12.5V.
    *   *Recommendation*: Any generic 12V LVD module (AliExpress) rated 10A+. Victron Battery Protect 65A is the marine-grade option.
    *   *Threshold settings*: Disconnect 10.5V / Reconnect 12.5V (avoids false trips during normal load).
*   [ ] **Electrolytic capacitor, 2200–4700µF 25V**: Mounted on 12V input of each buck converter.
    *   *Purpose*: Absorbs brief inductive voltage spikes and millisecond dips from hydraulic pump and anchor winch start/stop. Rides through transients the LVD relay is too slow to handle.
    *   *Recommendation*: 3300µF 25V electrolytic, low-ESR (Jaycar or element14).
*   [ ] **Connection Method (GPIO Required)**: Since USB is used for GPS.
    *   **Logic Level Shifter (TXS0108E)**: Bi-directional 3.3V <-> 5V shifter.
    *   *Purpose*: Safety connects Pi Zero GPIO (3.3V) to Arduino RX/TX (5V). Direct connection risks frying the Pi.
*   [ ] **End Stop Switches (2x)**: Waterproof limit switches for the rudder.
    *   *Purpose*: Stops the hydraulic pump hitting hard stops.

## 4. Wind Sensor Integration
*Reference: [Wind Sensor Integration](wind_sensor_integration.md)*

### Critical
*   [ ] **RTL-SDR Dongle**: "RTL-SDR Blog V3" or "Nooelec NESDR".
*   [ ] **USB Extension Cable**: 1-2m.
    *   *Purpose*: Move the dongle away from the noisy Raspberry Pi/Buck converters to improve radio reception.
*   [ ] **SMA Pigtail / Adapter**: If connecting to a proper masthead antenna later.

## 5. Tools & Consumables

### Critical
*   [ ] **Dielectric Grease**: To coat terminals after tightening (prevents green corrosion).
*   [ ] **Self-Amalgamating Tape**: For waterproofing outdoor connections (Mast base, Solar connectors).
*   [ ] **Butt Connectors (Heat Shrink)**: Blue (16-14 AWG) and Yellow (12-10 AWG).
    *   *Warning*: Do NOT use cheap PVC automotive crimps. Use the "Dual wall adhesive lined" ones.

### Nice to Have
*   **Ferrule Crimper Kit**: For inserting stranded wire into screw terminals (like on the solar charge controller or fuse block inputs). Clean and safe.
