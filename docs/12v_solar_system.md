# 12V Solar, Wind & Charging System for Yacht Arion

## System Overview

Fully 12V house/start system with isolated start battery, smart VSR isolator, Alpha Pro alternator regulator, PL20 for Rutland 913 windgen, and new MPPT (TBD) for 550W 36V panels. Uses your ordered MC4 kits, 4mm²/12AWG extensions, 8G CCA, ferrule crimper, 100A breakers, and 24-slot fuse holders.

## Components Inventory & Assignments

| Item | Source | Use |
| ----- | -------- | ----- |
| MC4 Y-Branch (8pcs kit) AU$21.53 | New | Parallel 2x panels: 2x MC4F→Y‑F + 2x MC4M→Y‑M → single MC4 pair to MPPT. |
| 4mm²/12AWG 6m red/black MC4 extensions (2 sets) AU$26.62 | New | Roof/deck run panels → MPPT (fuse each positive leg @20A). |
| 8G CCA wire 7.7m red+black | New | MPPT output → house bus (16mm² equiv., fuse 60A); VSR house side. |
| Ferrule crimper HCS8 kit +400pcs AU$12.90 | New | All bus terminations (AWG8–14 ferrules to blades/spades for fuse blocks). |
| 3x 100A auto breakers | New | Solar input (40A), wind input (30A), house main (100A). |
| 2x 12-blade fuse holders (24 slots total) | Existing | House Bus A (12 slots: lights, nav, pumps); High-current Bus B (12 slots: inverter, toilet, etc.). |
| Red bus (4-post) + black bus (strips) | Existing | House positive/negative studs. |
| PL20 + ammeter panel | Existing | Rutland 913 regulation/diversion to start bus. |
| Smart VSR 140A | Existing | Links start/house positives. |
| Batteries: N70 house + N702 start | Existing | House (blue box), start (red box). |

## Wiring Standards

- All positives fused/brechered near source (AMSA/ABYC E-11).
- 4mm² PV cable UV-rated; 8G CCA tinned or sleeved.
- Common negative bus bonded to engine.
- Labels on every run (ferrules + heatshrink).

## Mermaid System Diagram

```mermaid
graph TD
    subgraph "Sources"
        Panels["2x 275W 36V Panels<br/>MC4 Y-Branch + 4mm² 6m Ext."]
        Wind["Rutland 913<br/>w/ Regulator<br/>4mm² cable"]
        Alt["Yanmar Alt<br/>Alpha Pro Reg"]
        Gen["Generator<br/>(PL20 Aux)"]
    end

    subgraph "Batteries & Link"
        StartBat["Start Bat<br/>N702 Red<br/>100A Breaker"]
        HouseBat["House Bat<br/>N70 Blue<br/>100A Breaker"]
        VSR["Smart VSR<br/>140A<br/>8G CCA"]
    end

    subgraph "Buses"
        StartBus["Start Bus<br/>Red Bus Post<br/>PL20 Load Out"]
        HouseBusA["House Bus A<br/>12-Slot Fuseholder<br/>Lights/Nav/Pumps"]
        HouseBusB["House Bus B<br/>Heavy Studs<br/>100A Breakers<br/>Winch/Inverter/Toilet/Troll Motor"]
        NegBus["Common Neg Bus<br/>Black Strips<br/>Engine Bond"]
    end

    subgraph "Loads"
        Starter["Starter Motor"]
        Nav["Nav/VHF/GPS<br/>20A Circ"]
        HF["HF Radio<br/>40A"]
        Lights["Lights<br/>15A"]
        Pumps["Bilge/Pumps<br/>15A"]
        Fridge["Fridge"]
        Winch["Windlass<br/>100A"]
        Inverter["1500W Inv<br/>50A"]
        Toilet["Elec Toilet<br/>15A"]
        Trolling["Troll Motor<br/>30A"]
    end

    Panels -->|"20A Fuse ea.<br/>40A Breaker"| MPPT["New 40A MPPT<br/>12V 100V PV"]
    MPPT -->|"8G CCA 60A Fuse"| HouseBat
    Wind -->|"30A Breaker"| PL20["PL20 PWM<br/>20A"]
    PL20 --> StartBat
    Alt --> StartBat
    Gen -.-> PL20
    StartBat <-->|"VSR Link"| HouseBat

    StartBat --> StartBus
    HouseBat -->|"Main 100A"| HouseBusA
    HouseBat -->|"100A Breakers"| HouseBusB

    StartBus --> Starter
    StartBus -.-> HF
    HouseBusA --> Nav
    HouseBusA --> Lights
    HouseBusA --> Pumps
    HouseBusA --> Fridge
    HouseBusB --> Winch
    HouseBusB --> Inverter
    HouseBusB --> Toilet
    HouseBusB --> Trolling

    StartBus --> NegBus
    HouseBusA --> NegBus
    HouseBusB --> NegBus
