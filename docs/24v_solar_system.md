# 24V Solar Charging & Power System for YachtArion

## System Overview

This document describes the 24V lead-acid battery system with MPPT solar charging for YachtArion, providing power for both propulsion (24V trolling motor) and house systems (12V via buck converter).

### System Components

- **Solar Array**: 2 × JA Solar JAP60S01-275/SC (275W each, 550W total)
- **Battery Bank**: 2 × 12V lead-acid batteries in series (24V nominal, 200Ah typical)
- **Charge Controller**: 60A MPPT auto-detect (12V/24V/36V/48V capable)
- **DC-DC Converter**: Golf-cart style 24V to 12V buck converter (18-58V input, 12V 20A output, 240W)
- **Propulsion**: 24V trolling motor (90 lb thrust, ~1152W at full power)
- **House Loads**: 12V lighting, electronics, communications via buck converter

### Voltage & Power Specifications

**Solar Panels (per unit at STC)**:
- Maximum Power: 275W
- Voltage at MPP (Vmp): 31.34V
- Current at MPP (Imp): 8.77A
- Open Circuit Voltage (Voc): 38.38V
- Short Circuit Current (Isc): 9.29A

**Array Configuration (Parallel)**:
- Total Array Voltage at MPP: ~31.3V
- Total Array Current at MPP: ~17.5A (2 × 8.77A)
- Total Array Power: ~550W

**Battery Bank Voltage Setpoints** (lead-acid, temperature compensated):
- Bulk/Absorption Charge: 28.8V (14.4V per 12V cell)
- Float Charge: 27.2V (13.6V per 12V cell)
- Low Voltage Disconnect (LVD): 22.2-23.0V (configurable)
- Temperature Compensation: -3mV/°C per 2V cell

**Trolling Motor** (example: 90 lb electric):
- Rated Voltage: 24V
- Rated Power: 1152W (full thrust)
- Typical Current: 48A @ 24V (full power)
- Run Time from 200Ah Bank @ 50% DoD: 2-3 hours (accounting for voltage sag and Peukert effect)

## Electrical System Architecture

### Block Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     YACHT ARION 24V SYSTEM                   │
└──────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  2× JA Solar 275W   │
                    │   Panels (Parallel) │
                    │  Vmp ≈ 31.3V, P≈550W│
                    └──────────┬──────────┘
                               │
                               │ MC4 connectors
                               │ 10 AWG tinned marine cable
                               │ 6mm² / PV Isolator breaker
                               ▼
                    ┌──────────────────────┐
                    │  60A MPPT Controller │
                    │   (12/24/36/48V)    │
                    │  AMPT/Victron/etc.  │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │  60A Battery Breaker │
                    │   Heavy cabling      │
                    │   ≥16mm² / 6AWG     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────────┐
        │  24V     │    │  24V     │    │ 12V Buck     │
        │ Battery  │    │ Trolling │    │ Converter    │
        │  Bank    │    │  Motor   │    │ (18-58V→12V) │
        │200Ah×24V │    │  Circuit │    │   240W       │
        └────┬─────┘    └──────────┘    └───────┬──────┘
             │                                   │
             │         12V DC Distribution       │
             └───────────────────┬───────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌──────────────┐        ┌──────────────────┐
            │  12V Fused   │        │   Autopilot &    │
            │  House Panel │        │  Navigation (Pis)│
            │  (Lights,    │        │  (Buck Conv #1)  │
            │   Radio,etc) │        │                  │
            └──────────────┘        └──────────────────┘
```

### Single-Line Wiring Diagram (Text)

```
PV Array (2×275W)
│
├─ MC4 Y-connector (parallel)
│
├─ PV+ (6mm² red) ─→ PV Isolator Breaker (20A)
│                      │
│                      ├─ MPPT Controller (PV+)
│
└─ PV- (6mm² black) ──→ MPPT Controller (PV-)


24V Battery Bank
│
├─ Batt1- (12V) ───→ Batt2- (12V)
│                      [Series connection]
└─ Batt2+ (12V) ───→ Bank+ (24V nominal)

From MPPT Batt+ output:
│
├─ 60A Battery Breaker (16mm² / 6AWG red)
│  │
│  ├─ 24V Trolling Motor Circuit
│  │  ├─ 60-70A Motor Breaker → Motor + terminal
│  │  └─ Heavy cable (≥10mm²) back to Bank-
│  │
│  ├─ 12V Buck Converter Input (25A fuse)
│  │  ├─ Input: 24V+ and GND
│  │  └─ Output: 12V + and 12V - to house panel
│  │
│  └─ Other 24V Loads (if any)
│     └─ Via individual fused branches

From MPPT Batt- output:
│
├─ Main Battery GND bus (16mm² / 6AWG black)
│  │
│  ├─ DC negative common point
│  ├─ Hull bonding (single point, ABYC E-11)
│  └─ All return paths


24V DC Negative Bus / Single-Point Ground
│
├─ Battery Bank negative
├─ Motor return
├─ Buck converter return
├─ MPPT controller ground
└─ Hull bonding point (one location only)
```

## Charge Controller Configuration

### MPPT Controller Selection

**Recommended Specifications**:
- **Voltage Capability**: 12V / 24V / 36V / 48V auto-detect (or fixed 24V)
- **Charge Current**: 60A minimum
- **PV Input**: ≥150V Voc rating
- **Temperature Sensor**: Built-in or remote probe compatible
- **Display/Remote**: Bluetooth or WiFi monitoring (optional but recommended)

**Example Models**:
- Amptron AT-SOLCHR-AM4860 (60A, 12/24/36/48V auto-detect)
- Victron SmartSolar 60/48 (60A, 48V system, requires de-rating for 24V)
- OutBack MPPT (60A models with datalogger capability)
- Generic Chinese 60A MPPT (≥150V Voc, 24V compatible)

### Configuration Parameters (24V Lead-Acid Bank)

**Charge Setpoints** (temperature-compensated):

| Parameter | Value | Notes |
|-----------|-------|-------|
| Bulk/Absorption Voltage | 28.8V | 14.4V per 12V cell; typical for lead-acid |
| Absorption Time | 1-2 hours | Configurable; default usually 1-2h |
| Float Voltage | 27.2V | 13.6V per 12V cell; long-term maintenance |
| Float Current Threshold | 2-5% of rated | Auto-transition when current drops |
| Equalization (AGM only) | Not recommended | Flooded lead-acid may support every 3-6 months |
| LVD (Load Disconnect) | 22.2V - 23.0V | Optional; protects battery from over-discharge |
| Temperature Compensation | -3mV/°C per 2V cell | Adjust setpoints for ambient temp |

**Typical Daily Cycle** (sunny day):
1. **Morning (dawn)**: Bulk charge at 28.8V; controller maximum current (~19A at MPP)
2. **Mid-day (peak sun)**: Array voltage rises slightly; charge current decreases as battery approaches bulk voltage
3. **Absorption**: Once bulk voltage reached, current tapers over 1-2 hours
4. **Float**: Battery transitions to 27.2V float for rest-of-day trickle charging
5. **Night**: No charging; loads discharge from battery

### MPPT Efficiency & Power Flow

**At Nominal Operating Point**:

- **Array Output**: Vmp ≈ 31.3V, Imp ≈ 17.5A, Pmp ≈ 548W
- **Battery Voltage (bulk)**: 28.8V
- **MPPT Duty Cycle** (buck regulator): ~92% (28.8V / 31.3V)
- **Expected Charge Current**: $I_{bat} = \frac{P_{pv}}{V_{bat}} \times \eta = \frac{548}{28.8} \times 0.95 \approx 18A$
- **Loss (5%)**: ~27W → heat dissipation in MPPT (cooling fan may activate if ambient >40°C)

**Efficiency Over Operating Range**:
- Peak efficiency (~90-95%): Array voltage 5-10% above battery voltage (buck mode)
- Reduced efficiency (<85%): Array voltage <<battery voltage (excessive duty cycle) or >>battery voltage (boost mode, not typical for this array)
- Best performance: Panels unshaded, MPPT in "sweet spot" of 30-35V PV input

## Battery Bank Design

### Battery Selection

**Lead-Acid Type Options**:
1. **Flooded (wet) lead-acid**: Lower cost, requires venting & maintenance, good for stationary marine use
2. **AGM (Absorbed Glass Mat)**: Sealed, lower maintenance, slightly higher cost, good vibration tolerance
3. **Gel**: Very low maintenance, highest cost, slower charge acceptance

**Recommended for YachtArion**: AGM or quality flooded lead-acid (Odyssey, Relion, or marine-grade equivalent)

**Capacity Examples**:
- **100Ah bank** (2×12V 100Ah in series → 24V 100Ah): ~2.4kWh total energy; ~1.2kWh usable @ 50% DoD
- **200Ah bank** (2×12V 200Ah in series → 24V 200Ah): ~4.8kWh total energy; ~2.4kWh usable @ 50% DoD

### Series Connection (Two 12V Batteries)

```
┌─ 12V Battery #1 ─┐
│  Batt1+ (red)    │
│  Batt1- (black)  │
└──────────────────┘
         │
         │ Interconnect cable (≥10mm² / 8AWG)
         │ Heavy-duty lug terminals, crimped & soldered
         │
┌─ 12V Battery #2 ─┐
│  Batt2+ (red)    │
│  Batt2- (black)  │
└──────────────────┘
         │
         │ Bank+ = Batt2+ (positive terminal of upper cell)
         │ Bank- = Batt1- (negative terminal of lower cell)
         │
    ┌────┴─────┐
    │  24V Bus  │
    └───────────┘
```

**Critical Points**:
- Never tap loads from mid-point (Batt1+ to Batt2-)—this causes imbalance and accelerated degradation
- Use heavy-gauge interconnect cable with crimp lugs (no exposed copper, risk of arc flash)
- Ensure terminal connections are clean and tight (minimum 0.2V contact resistance)
- Use marine-grade battery box with integrated straps & venting for flooded batteries
- Install temperature sensor on one battery for MPPT compensation

### Battery Monitoring

**Recommended Instruments**:
1. **Shunt & Monitor**: 500A shunt with integrating monitor (displays Ah drawn, SoC %, voltage, current)
   - Example: Victron SmartShunt 500A, EPEVER EM5, or equivalent
   - Measures actual bank voltage and discharge current
2. **Manual Hydrometer** (if flooded): Monthly check of specific gravity per cell
3. **Visual Inspection**: Weekly check for corrosion, leaks, or loose connections
4. **Temperature Probe**: Part of MPPT or dedicated thermometer

**Expected Performance**:
- **Charge time** (550W array): ~8-10 hours from 50% to 95% SoC on sunny day (accounting for voltage rise and absorption phase)
- **Cycle life** (50% DoD, flooded lead-acid): 800-1000 cycles typical (~2-3 years marine use)
- **Self-discharge**: ~1-2% per month (flooded), <1% (AGM) at float voltage

## 24V Propulsion System (Trolling Motor)

### Motor Circuit Design

**24V Trolling Motor Specifications** (example: 90 lb thrust):
- Rated Voltage: 24V DC
- Rated Power: 1152W (at full thrust)
- Rated Current: 48A @ 24V
- Peak Thrust: 90 lbf (~400N)
- Duty Cycle: Intermittent (not continuous full power)

### Motor Wiring & Protection

**Cable Sizing** (for 50A continuous, <3% voltage drop @ 10m run):

| Parameter | Value | Notes |
|-----------|-------|-------|
| Conductor Gauge | ≥10mm² (8 AWG) | Tinned marine cable for salt water |
| Positive Lead | 10mm² red | From battery + via breaker to motor + |
| Negative Lead | 10mm² black | From motor - back to battery - (common bus) |
| Fuse/Breaker | 60-70A thermal-magnetic | Rating: 1.25-1.5× max motor current |
| Breaker Type | Marine-grade DC breaker | Suitable for 24V DC; preferred over fuse for reliability |
| Cable Length | Minimize | Shorter run = less voltage drop |
| Connections | Tinned lug terminals | Crimped & soldered; no bare copper |
| Conduit | Marine-grade loom | Protect from chafe, UV, salt spray |

**Breaker Selection**:
- **Thermal-Magnetic DC Breaker** (e.g., Blue Sea Systems, AMAG Marine):
  - Instant trip at ~2-3× rated current (15-20A for 60A breaker)
  - Thermal trip at ~1.1× rated current (66A for 60A breaker) over ~30 sec
  - Rated for 24V DC inductive loads
  - Preferrable to fuses for motor circuits (fuse cannot re-trip)

**Example 60A Breaker Specification**:
- Frame: Toggle or push-button
- Voltage Rating: 24V DC minimum (or 48V DC for marine dual-voltage)
- Current Rating: 60A
- Breaking Capacity: ≥1000A
- Trip Type: Thermal-magnetic (bi-metal + solenoid)
- Operating Temperature: -20°C to +60°C

### Motor Operation & Run-Time Calculation

**Power Delivery at Various Thrust Levels**:

| Thrust (%) | Power (W) | Current (A) | Run-Time* (hours) |
|------------|-----------|------------|-------------------|
| 25% (light cruise) | 288 | 12 | ~16h |
| 50% (medium) | 576 | 24 | ~8h |
| 75% (high) | 864 | 36 | ~5.3h |
| 100% (full) | 1152 | 48 | ~4.1h |

*Run-time from 24V 200Ah bank @ 50% DoD, accounting for Peukert effect and voltage sag.

**Real-World Considerations**:
- At 48A draw, battery voltage sags from 24V → ~22-23V (heavy load)
- Peukert effect reduces usable Ah (faster discharge = lower capacity)
- Actual run-time is 60-70% of Ah/Current estimate
- **Practical Run-Time Estimate**: At full power, expect 2-3 hours continuous from full 200Ah bank

### Motor Control & Direction

**Reversible Trolling Motor Circuit**:
- Typically includes integral forward/reverse control (manual lever or foot pedal)
- Most 24V motors are 3-wire: 24V+, 24V-, and PWM speed control
- Speed control via PWM signal from hand throttle or foot pedal
- No additional relay/contactor needed (all logic inside motor controller)

**Optional External Motor Contactor** (if desired for remote monitoring):
- 24V DC contactor rated for motor inrush (e.g. 60A continuous, 200A inrush)
- Allows cut-off from navigation station or autopilot
- Recommended practice: Use hard-wired breaker for instant safety cutoff, add soft contactor for remote control

## 24V House System (Lights, Radio, Instruments)

### 12V Buck Converter Integration

The existing 24V-to-12V buck converter provides regulated 12V for house loads:

**Converter Specifications** (from earlier documentation):
- Input Voltage: 18-58V DC (operates from 24V battery directly)
- Output Voltage: 12V DC regulated ±5%
- Output Current: 20A maximum continuous
- Output Power: 240W nominal
- Efficiency: 90-95% at typical loads

**Connection to 24V Bank**:

```
24V Battery Bank
      │
      ├─ [25A Fuse] ─── Golf Cart Buck Converter Input (24V+, GND)
      │                         │
      │                    [Internal buck regulation]
      │                         │
      │                  Output: 12V ± 0.3V
      │
      └─ [Common Ground] ─────┬──── 12V Negative Bus
                              │
                         12V Fuse Panel
                              │
                    ┌─────────┼─────────┐
                    │         │         │
               [Lighting] [Radio] [Instruments]
                   (5A)      (10A)      (5A)
```

**House Circuit Breakers** (12V side):

| Circuit | Breaker Size | Devices |
|---------|--------------|---------|
| Lighting | 5A | Navigation lights, cabin lights, deck lights |
| Radio / Comms | 10A | VHF radio, SSB transceiver, AIS receiver |
| Instruments | 5A | Chart plotter, compass display, depth sounder |
| Autopilot Pi 4 | 3A | Lysmarine system (powers via buck converter) |
| Autopilot Pi Zero | 1A | Tinypilot (powers via separate buck converter #1) |
| **Total Max** | **24A** | (But 20A buck converter limit = practical max 20A) |

**12V Load Budget**:
- Normal cruising (all systems active): ~15A (180W)
- Peak draw (full lights + charging): ~20A (240W)
- Idle (autopilot + minimal instruments): ~3A (36W)

**Note**: Pi 4 and Pi Zero are powered from separate 5V buck converters (as per main README), not from this 24V-to-12V converter. The 24V→12V converter is dedicated to house loads only.

## Complete Equipment List (Bill of Materials)

### Solar Array & Mounting

| Item | Qty | Spec | Price (AUD) | Source |
|------|-----|------|------------|--------|
| JA Solar JAP60S01-275/SC | 2 | 275W polycrystalline, 31.34V Vmp | $200-250/ea | LocalSolar, SupplyInstalled |
| Solar panel mounting kit | 1 | Stainless steel rails + clamps | $150-250 | Marine supplier |
| MC4 connectors (pair) | 2 sets | IP67 rated, 30A | $20-30/set | Electrical supplier |
| Breaker gland / penetration | 2 | Deck gland for cable entry | $15-20/ea | Marine hardware |
| PV isolator switch | 1 | 20A DC, manual or automatic | $30-50 | Electrical supplier |

**Subtotal Solar & Mounting**: ~$700-950 AUD

### Charge Controller & Monitoring

| Item | Qty | Spec | Price (AUD) | Source |
|------|-----|------|------------|--------|
| MPPT Solar Charge Controller | 1 | 60A, 12/24/36/48V auto-detect | $300-600 | Amptron, Victron, PowMR |
| Temperature sensor (optional) | 1 | For MPPT compensation | $20-40 | MPPT vendor |
| Shunt + Battery Monitor | 1 | 500A shunt, integrating monitor | $200-400 | Victron, EPEVER |
| Bluetooth/WiFi adapter (opt) | 1 | Remote monitoring | $50-100 | MPPT vendor |

**Subtotal Charge Controller & Monitoring**: ~$570-1140 AUD

### Battery Bank

| Item | Qty | Spec | Price (AUD) | Source |
|------|-----|------|------------|--------|
| 12V lead-acid battery (AGM) | 2 | 200Ah each | $600-900/ea | SuperCheap Auto, Battery World |
| Battery interconnect cables | 1 | ≥10mm² / 8AWG tinned, lugs | $30-50 | Marine supplier |
| Battery box with straps | 1 | Stainless steel frame | $50-100 | Marine hardware |
| Terminal covers / insulators | 2 | Prevent accidental shorts | $10-20 | Auto/electrical |
| Hydrometer (if flooded) | 1 | For specific gravity checks | $10-15 | Auto parts |

**Subtotal Battery Bank**: ~$1300-1995 AUD

### DC Wiring & Distribution

| Item | Qty | Spec | Price (AUD) | Notes |
|------|-----|------|------------|-------|
| Tinned marine cable (red) | 30m | 16mm² / 6AWG | $150-200 | Battery to breaker, controller output |
| Tinned marine cable (black) | 30m | 16mm² / 6AWG | $150-200 | Ground/return runs |
| Tinned marine cable (red) | 20m | 10mm² / 8AWG | $80-120 | Motor circuit positive |
| Tinned marine cable (black) | 20m | 10mm² / 8AWG | $80-120 | Motor circuit return |
| Tinned marine cable (red) | 10m | 6mm² / 10AWG | $30-50 | PV array input |
| Tinned marine cable (black) | 10m | 6mm² / 10AWG | $30-50 | PV array ground |
| Crimp lugs (assorted) | 100-pack | Tinned, various sizes | $20-40 | Electrical supplier |
| Heatshrink tubing (marine) | 50m | Adhesive-lined, various diameters | $30-50 | Marine/electrical |
| Cable ties (stainless) | 100-pack | UV-rated, stainless steel | $15-25 | Marine hardware |
| Wire conduit (marine loom) | 30m | Corrugated, UV-resistant | $40-60 | Marine supplier |
| Negative bus bars (tinned) | 2 | For central grounding | $20-40 | Electrical supplier |
| Battery breaker (main) | 1 | 60A, 24V DC thermal-magnetic | $80-150 | Blue Sea, AMAG Marine |
| PV isolator (optional) | 1 | 20A manual DC breaker | $30-50 | Electrical supplier |
| Motor breaker | 1 | 60-70A, 24V DC thermal-magnetic | $80-150 | Blue Sea, AMAG Marine |
| 24V to 12V buck converter | 1 | 18-58V input, 12V 20A output | $50-100 | Lithium Power, Amazon |
| 12V fuse block | 1 | 6-8 position, 20A bus rating | $30-60 | Electrical supplier |
| Fuses & holders | 1 lot | 5A, 10A, 15A, 25A marine ATO | $20-40 | Auto/electrical |

**Subtotal DC Wiring & Distribution**: ~$1185-1910 AUD

### Motor Circuit & Propulsion

| Item | Qty | Spec | Price (AUD) | Source |
|------|-----|------|------------|--------|
| 24V trolling motor | 1 | 90 lb thrust, ~1152W | $300-600 | Striker, Minnkota |
| Motor breaker (60-70A) | 1 | Redundant breaker in motor circuit | $80-150 | Blue Sea, AMAG |
| Shaft coupler / propeller | 1 | Matched to motor | $50-150 | Motor vendor |

**Subtotal Motor & Propulsion**: ~$430-900 AUD

### Miscellaneous

| Item | Qty | Spec | Price (AUD) | Source |
|------|-----|------|------------|--------|
| Battery tester | 1 | Voltage + load tester | $30-80 | Auto parts |
| Multimeter | 1 | Digital, 600V DC / 20A | $20-50 | Bunnings, electrical |
| Torque wrench | 1 | For terminal bolt tightness | $20-60 | Hardware |
| Crimping tool | 1 | Hydraulic or ratchet | $40-150 | Electrical tools |
| Soldering kit | 1 | For cable terminations | $30-80 | Hardware |
| Fire extinguisher | 1 | ABC type, 1-2 kg, dry chem | $20-40 | Safety |
| Electrical bonding strap | 1 | For hull bonding point | $15-30 | Marine hardware |
| Penetrating oil / contact cleaner | - | WD-40, electrical contact cleaner | $15-30 | Auto/hardware |
| Battery acid neutralizer (opt) | - | For flooded lead-acid safety | $10-20 | Auto parts |

**Subtotal Miscellaneous**: ~$230-540 AUD

## **TOTAL SYSTEM COST ESTIMATE**: ~$4,400 - $7,435 AUD

(Excluding Pixel 2 phone, Raspberry Pis, and existing autopilot hardware)

## Installation Guide Summary

The full installation guide includes 8 phases:

1. **Planning & Site Survey** - Panel location, battery placement, controller location
2. **Solar Panel Installation** - Mounting, electrical connections, cable routing
3. **Battery Bank Assembly** - Series configuration, box installation, DC wiring
4. **Charge Controller Installation** - Physical mounting, electrical connections, configuration parameters
5. **24V Motor Circuit** - Motor mounting, cable routing, breaker installation, control integration
6. **12V House System** - Buck converter connection, fuse panel installation, circuit wiring
7. **Safety & Compliance** - DC negative bus grounding, fire suppression, AMSA/ABYC standards
8. **Testing & Commissioning** - Pre-power inspection, power-up sequence, load testing, monitoring

## Operating Procedures

- **Daily Operation**: Morning checks, midday monitoring, motor operation, evening configuration
- **Weekly Maintenance**: Visual inspection, charge controller check, motor inspection
- **Monthly Maintenance**: Battery specific gravity, terminal inspection, system testing
- **Seasonal Maintenance**: Panel cleaning, angle adjustment for winter/summer, capacity testing

## Troubleshooting Guide

Common issues addressed:
- Low charge current
- Battery not reaching full charge
- 12V buck converter output instability
- Motor breaker tripping
- High battery self-discharge

Each includes probable causes, troubleshooting steps, and resolution procedures.

## System Expansion & Future Upgrades

- Additional solar capacity
- Battery bank expansion
- Wind generation
- Lithium battery upgrade
- Shore charger integration

## Safety Summary

10 critical safety rules covering breaker operation, grounding, cabling, fire suppression, and hydrogen venting.

---

**Document Version**: 1.0  
**Last Updated**: January 19, 2026  
**System Designer**: botheredbybees  
**Vessel**: SY Arion (36ft)  
**Location**: Cygnet, Tasmania, Australia

For questions or updates, please open an issue at https://github.com/botheredbybees/pypilot4arion
