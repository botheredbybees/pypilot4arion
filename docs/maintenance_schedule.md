# Electrical & Autopilot Maintenance Schedule

Regular maintenance prevents "sudden" failures at sea.

## Monthly Checks
*   ** Battery Water**: (If Lead-Acid) Check electrolyte levels in 24V House and 12V Start banks. Top up with distilled water only.
*   **Voltages**: Log resting voltage of 24V and 12V banks to track health.
*   **Bilge Switches**: Lift the float switch manually to verify the pump activates.
*   **Visual Inspection**: Glance at the **Bus Bars** and **Buck Converters**. Look for:
    *   Discoloration (Heat signs).
    *   Water ingress or salt crystals.

## 6-Month Checks (Pre-Season)
*   **Terminals**: Check tightness of all high-current connections (Bus A, Bus C, Windlass, Battery terminals). **Vibration loosens nuts.**
*   **Hydraulics**:
    *   Check fluid level in the helm reservoir.
    *   Inspect cylinder ram for pitting/leaks.
    *   Turn wheel hard-over to hard-over. Listen for air bubbles (gurgling). Bleed if necessary.
*   **Compass Calibration**:
    *   Do a 360° turn in calm water.
    *   Check Pypilot web UI scope. If the circle is distorted into an oval, re-calibrate.
*   **Corrosion Check ("Green Death")**:
    *   Pull a random sample of fuses. Check blades for corrosion.
    *   Inspect crimps on exposed deck wires (Windlass, Mast base).

## Annual Checks
*   **SD Card Backup**:
    *   Remove SD cards from TinyPilot (Pi Zero) and Lysmarine (Pi 4).
    *   Create full image backups.
    *   Replace cards if older than 2 years as preventative maintenance.
*   **Wind Sensor**:
    *   Inspect Ecowit WS80 at masthead.
    *   Clean solar panel surface.
    *   Check for spider webs/insect nests.
*   **Software Updates**:
    *   Check for Pypilot updates (only update if current version has bugs - "If it ain't broke, don't fix it").
    *   Update OpenCPN charts.

## 5-Year Replacement
*   **Bilge Pump**: Replace primary float switch.
*   **SD Cards**: Replace physical cards.
*   **Batteries**: Capacity test. Plan for replacement if capacity < 70%.
