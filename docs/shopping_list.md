# Project Shopping List

This document consolidates hardware requirements from the **Solar**, **Rewiring**, **TinyPilot**, and **Wind** integration plans.

> [!NOTE]
> Items marked **[Check Inventory]** may already be in your possession (based on uploaded photos). Please verify before purchasing.

## 1. Power System (24V Hybrid)
*Reference: [24V Solar Design](24v_solar_system.md)*
*> ⚠️ **User Purchased Budget Hardware**: See [Hardware Safety Review](hardware_review.md) for critical mitigations for Temu/Generic components.*

### Critical
*   [ ] **12V->24V DC-DC Charger (The Bridge)**: Victron Orion-Tr Smart 12/24-18 Isolated (or Non-Isolated).
    *   *Purpose*: Charges 24V House bank from 12V Engine Alternator.
*   [ ] **24V->12V Buck Converter**: 30A-40A isolated converter (Step Down).
    *   *Note*: You mentioned you have an "old" one. Ensure it provides clean 13.8V output for sensitive electronics.
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
*   [ ] **24V -> 5V Buck Converter (USB Power)**: Dedicated PSU for Pi Zero & Pi 4.
    *   *Recommendation*: "12V/24V to 5V 3A Micro USB Converter" (Waterproof module).
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
