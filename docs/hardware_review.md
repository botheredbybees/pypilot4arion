# Hardware Review & Mitigation Plan

## 1. Executive Summary

You have purchased "Budget/Generic" components to substitute for the "Marine Grade/Smart" components originally specified.
*   **Can it work?** Yes, effectively.
*   **Is it plug-and-play?** **NO.**
*   **Critical Safety Issues**: The **8AWG CCA Wire** and the **Generic DC-DC Converter** require specific handling to avoid fire risks and dead batteries.

## 2. Component Analysis

### A. The "8 Gauge CCA Wire"
> **Item**: 8 Gauge CCA (Copper Clad Aluminum)
> **Intended Use**: Battery Interconnects / High Current?

*   **⚠️ CRITICAL WARNING**:
    *   **Resistance**: CCA has ~60% higher resistance than Copper. "8 Gauge CCA" behaves like **10 Gauge Copper**.
    *   **Corrosion**: Aluminum corrodes instantly in salt air (turning to white powder), causing high resistance -> Heat -> **Fire**.
    *   **Suitability**: **UNSAFE for main battery interconnects** (Series jumpers) or the main 60A/100A runs.
*   **Mitigation**:
    *   **Do NOT use this for the Battery-to-Battery series jumper.** You must buy a real copper (welding cable) jumper for the 24V bank creation.
    *   *Acceptable Use*: You *can* use this for the "Solar Panel to Controller" run (if keep dry) or lower amperage loads (<20A), but you **MUST** use "Bi-Metal" crimps or seal the connections perfectly (glue-lined heat shrink) to prevent air getting to the aluminum core.

### B. The "12V Input / 24V Output" DC-DC Converter
> **Item**: Generic Boost Converter (12V->24V)
> **Intended Use**: Charging link (The Bridge)

*   **The Issue**: This is likely a "Dumb" booster, not a "Smart Charger".
    1.  **No "Charge Profile"**: It just pushes voltage. If you set it to 28.8V, it will push 28.8V forever, potentially boiling the batteries if left for days.
    2.  **No "Engine Detection"**: It will run as long as it has input power, draining your Start Battery flat even when the engine is off.
*   **Mitigation**:
    *   **Voltage Setting**: Set the output voltage to **27.6V** (Float Voltage). This will charge the 24V bank slower but is safe to leave connected indefinitely without boiling the batteries.
    *   **Ignition Control**: Use your **Smart Battery Isolator (VSR)** on the input. This solves the "Engine Detection" problem perfectly.

### C. The "Smart Battery Isolator" (VSR)
> **Item**: 12V 140A VSR (Voltage Sensitive Relay)
> **Verdict**: **The Perfect Fix**.

*   **The Solution**: You initially bought a 24V relay (wrong voltage) and we worried about ignition wiring.
*   **The VSR**: This device connects when voltage > 13.3V and disconnects < 12.8V.
*   **Action**: Put this **between** the Start Battery and the DC-DC Converter Input. It will automatically turn the charger ON when the engine starts and OFF when it stops. **Problem Solved.**

### D. The Solar Cable (12AWG) & Parallel Panels
> **Item**: 10m of 12AWG Solar Cable
> **Constraint**: Panels must be parallel (Tip Shop find).
> **Current**: ~18 Amps total.

*   **Analysis**:
    *   **Voltage Drop**: ~1.3V over 10m at full sun.
    *   **Impact**: Your 60V panels (if they are 60-72 cell) output ~30-36V. Losing 1.3V brings you to ~29V.
    *   **Verdict**: **Acceptable.** Since you only need to reach ~28.8V to charge a 24V bank, losing 1V is fine. It's efficient enough for a budget build.

## 4. Specific "Budget Build" Integration Strategy

### A. The "Daisy Chain" Idea (DC-DC -> Solar Controller)
> **Idea**: Feed the Generic DC-DC output into a 2nd Solar Controller to manage charging.

*   **Verdict**: **NOT RECOMMENDED**.
*   **Why**:
    *   **The Fight**: A solar controller assumes its input is a current source (panel). It rapidly switches the input (PWM) or sweeps voltage (MPPT).
    *   **The Risk**: Your Generic DC-DC Converter tries to force a stiff voltage. When the Solar Controller switches, the DC-DC may oscillate, overheat, or blow its capacitors.
*   **Better Solution ("The Float Hack")**:
    *   Set the Generic DC-DC Converter output voltage to **27.6V exactly** (Float Voltage).
    *   **Result**: It will charge the house bank to ~90% and then just sit there safely. It effectively acts as a "Float Maintainer" while the engine runs. No boiling batteries, no complex chaining, robust.

### B. The 7Ah LiFePO4 Batteries (Dinghy Use)
> **Correction**: User clarified these are for a 12V Dinghy Trolling Motor, not the main yacht.

*   **Revised Advice**:
    *   **BMS Trip Risk**: Even small dinghy motors draw 20-30 Amps. A single 7Ah battery usually has a "Max Continuous Discharge" of only 7-10 Amps. If you use just one, it will cut out immediately.
    *   **The Fix (Parallel Gang)**: You MUST wire all 4 in **Parallel** (Positive to Positive, Neg to Neg) to create a single **12V 28Ah** battery.
    *   *Result*: This gives you ~40A of available current (4x 10A limits), which should run the dinghy motor fine.
    *   **Mixing with Gel**: Do not hard-wire them to your Gel cell permanently (different resting voltages). Use the Lithium pack until flat, then physically swap the cables to the Gel pack ("Reserve Tank").

### C. The 20A 24V->12V Buck Converter
> **Item**: Golf Cart Style Reducer
> **Verdict**: **Excellent**.
*   Perfect for powering the **12V House Bus (Bus B)** (Lights, Fridge, Instruments) from the 24V Main Bank.
*   Connect Input to 24V Fuse block. Connect Output to your 12V Fuse Block.

## 5. How to Tune the Generic DC-DC Converter

You asked: *"How do I set the DC-DC output to 27.6V exactly?"*

The generic silver/heatsink converters usually have a small brass screw component called a **Potentiometer (Trimpot)** next to the terminals.

**The Procedure:**
1.  **Preparation**: You need a **Digital Multimeter** and a **Small Flathead Screwdriver** (precision/jewellers size).
2.  **Wiring**: Connect the **Input** side to your 12V Battery. Do **NOT** connect the Output to the 24V house bank yet. Leave the output wires "floating" (safe in mid-air).
3.  **Measure**: Set Multimeter to "DC Volts (200V range)". Put the Red probe on Output(+) and Black probe on Output(-).
4.  **Adjust**:
    *   Read the display (e.g., it might say 24.0V).
    *   Turn the small brass screw on the blue trimpot. One direction increases voltage, the other decreases. It may need many turns.
    *   Keep turning until the multimeter reads **27.6V**.
5.  **Finalize**: Once set, disconnect the Input, wire up the Output to your 24V Bank, and you are ready to go. The voltage is now "clamped" to that safe Float level.

## 6. Revised Wiring Plan (Budget Edition)

### The "Bridge" (VSR + Generic Converter)
1.  **Start Battery (+)** -> **Smart Battery Isolator (VSR) Input** (Red cable).
2.  **VSR Output** -> **DC-DC Input (+)**.
3.  **Ground** -> **DC-DC Input (-)** AND **VSR Black Wire (Ground)**.
4.  **DC-DC Output (+)** -> **24V House Bank (+)**.
5.  *Settings*: Adjust DC-DC trimpot to output **27.6V** (Check regularly with multimeter).

*How it works*: The VSR automatically detects when the Yanmar starts (Voltage > 13.3V) and turns ON power to the converter. When engine stops (Voltage < 12.8V), it cuts power. **Perfect automation.**

### Cabling Rules
*   **High Current (Batteries/Inverter/Motor)**: Use the **Second-hand Battery Cable** (Copper).
*   **Medium Current (Solar/Fridge)**: Use the **12AWG Solar Cable** or **8AWG CCA (Sealed)**.
*   **Low Current (Lights/Instruments)**: Use the **14AWG Wire**.
