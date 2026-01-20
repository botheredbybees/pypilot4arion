
# Testing and Tuning Guide for Pypilot with Arduino Motor Controller

Complete testing procedures and PID tuning guide for pypilot autopilot with Arduino motor.ino firmware, IBT-2 H-bridge, and Octopus Model 1012 hydraulic pump.

## Overview

This guide covers systematic testing from bench validation through sea trials, followed by PID tuning procedures for optimal autopilot performance. Testing progresses through increasing levels of complexity and risk, ensuring safety at each stage.

## Safety First

⚠️ **Critical Safety Rules:**

1. **Always maintain manual helm readiness** - never test in confined waters without immediate manual override capability
2. **Start conservatively** - begin with low PID gains and max_current limits
3. **Test in calm conditions first** - save rough weather testing for after basic functionality is confirmed
4. **Have a safety observer** - one person monitoring autopilot, another ready at helm
5. **Plan emergency procedures** - know how to disengage instantly (both software and physical power disconnect)
6. **Wear PFDs during testing** - unexpected rudder movements can cause loss of balance
7. **Check traffic** - test in open water away from other vessels, moorings, and hazards

## Testing Phases

### Phase 1: Bench Testing (No Water)

**Goal**: Verify all electronic components function correctly before installing on boat.

#### 1.1 Arduino Serial Communication Test

**Equipment needed:**

- Arduino Nano with motor.ino flashed
- USB cable
- Computer with screen/minicom installed

**Procedure:**

```bash
# Connect Arduino to computer
screen /dev/ttyUSB0 153600  # Adjust baud for your DIV_CLOCK setting

# Expected output: Binary telemetry packets every ~100ms
# Should see periodic data (not human-readable, but regular patterns)
# Check for:
# - Consistent packet timing
# - No long pauses or gaps
# - Clean data stream (not garbage characters)

# Press Ctrl+A then K to exit screen
```

**Success criteria:**

- ✓ Regular telemetry packets received
- ✓ No communication errors in dmesg
- ✓ Arduino LED (D13) flashes periodically

**Troubleshooting:**

- No data: Check baud rate matches motor.ino DIV_CLOCK setting
- Garbage data: Wrong baud rate, check USB cable quality
- CH340 not detected: Install/update CH340 drivers (see installation guide)

#### 1.2 Arduino Flag Status Check

**Equipment needed:**

- Bench power supply (12V, 2A minimum)
- Multimeter

**Procedure:**

1. Connect Arduino to 12V bench supply via voltage divider on A0:
   - 560Ω resistor from 12V+ to A0
   - 10kΩ resistor from A0 to GND
2. Connect Arduino to Pi Zero via USB
3. On Pi Zero, run pypilot in verbose mode:

   ```bash
   pypilot --verbose
   # or
   pypilot_client 192.168.43.101 | grep flags
   ```

4. Check flag output for:

   - `SYNC` flag set (communication established)
   - No `BAD_FUSES` flag (if set, ATmega328P needs fuse programming)
   - No `BADVOLTAGE_FAULT` (voltage reading within 9-20V range)
   - No `INVALID` flag (CRC8 validation passing)

**Success criteria:**

- ✓ SYNC flag consistently set
- ✓ Voltage reading correct (within 0.5V of actual supply)
- ✓ No persistent fault flags

#### 1.3 IBT-2 Bench Test (Motor Disconnected)

**Equipment needed:**

- IBT-2 motor controller
- 12V bench supply (30A capable) or car battery
- Arduino with motor.ino
- Multimeter or oscilloscope

**Procedure:**

1. Wire Arduino to IBT-2 as per installation guide (D9, D10, D2, D3, GND, 5V)
2. Connect 12V supply to IBT-2 B+/B- (motor outputs OPEN, not connected yet)
3. Ground Arduino D6 pin (H-bridge mode)
4. Power Arduino from bench supply or USB
5. On Pi Zero, manually command motor via pypilot web interface:

   ```text
   Navigate to: http://192.168.43.101
   Engage autopilot
   Use servo.command slider: 
   - Move to 1500 (starboard)
   - Move to 500 (port)
   - Return to 1000 (stop)
   ```

6. Monitor with multimeter or scope:

   - At command 1500: D9 (RPWM) should show PWM, D10 (LPWM) = 0V
   - At command 500: D10 (LPWM) should show PWM, D9 (RPWM) = 0V
   - At command 1000: Both D9 and D10 should be 0V (or brake mode)

**Success criteria:**

- ✓ PWM signals appear on correct pins for forward/reverse commands
- ✓ No PWM on both channels simultaneously (would indicate H-bridge shoot-through risk)
- ✓ IBT-2 doesn't overheat (should be cool to touch at no-load)

**Troubleshooting:**

- No PWM output: Check D6 is grounded (H-bridge mode), verify Arduino D9/D10 wiring
- Wrong direction: Expected behavior at this stage, will reverse in motor testing
- Both outputs active: CRITICAL - do not connect motor, check motor.ino code

#### 1.4 Current Sense Calibration

**Equipment needed:**

- IBT-2 with motor connected
- Clamp ammeter or inline ammeter (20A range)
- Hydraulic pump (Octopus 1012)

**Procedure:**

1. Connect ammeter in series with pump motor
2. Connect motor to IBT-2 outputs (Motor+, Motor-)
3. Command motor via pypilot to 25% duty cycle (command ~1250)
4. Measure actual current with ammeter
5. Check Arduino telemetry for current reading:

   ```bash
   pypilot_client 192.168.43.101 | grep servo.current
   ```

6. Compare telemetry reading to ammeter:
   - Telemetry is in units of amperes (decimal)
   - Should match ammeter within ±10%
7. Repeat at 50% and 75% duty cycles

**Success criteria:**

- ✓ Current readings within ±10% of ammeter at all duty cycles
- ✓ Current sense responds to load changes
- ✓ No overcurrent faults during normal operation

**Calibration adjustment** (if needed):

- Edit motor.ino `TakeAmps()` function for your shunt configuration
- Common adjustments:
  - If reads high: Reduce multiplier in calculation
  - If reads low: Increase multiplier
  - Document calibration factor for future reference

#### 1.5 Pump Direction Verification

**Equipment needed:**

- Hydraulic pump connected to steering ram
- Ability to observe rudder movement

**Procedure:**

1. With pump connected to hydraulic ram on boat (or test stand)
2. Command small starboard turn via pypilot (command ~1200)
3. Observe rudder direction:
   - Should move to starboard (right when viewed from stern)
4. Command small port turn (command ~800)
5. Observe rudder direction:
   - Should move to port (left when viewed from stern)

**Success criteria:**

- ✓ Starboard command → rudder moves starboard
- ✓ Port command → rudder moves port
- ✓ Stop command → pump stops immediately
- ✓ Smooth startup (no jerking or hammering)

**Correction** (if directions reversed):

- Swap Motor+ and Motor- connections at IBT-2 output terminals
- Alternatively, swap D9/D10 wiring at Arduino (less preferred)

### Phase 2: Dockside Testing (Boat in Water, Engine Off)

**Goal**: Verify autopilot functionality and safety systems with boat secured.

#### 2.1 IMU Calibration and Compass Check

**Procedure:**

1. Access Tinypilot web interface: <http://192.168.43.101>
2. Navigate to Calibration section
3. Perform compass calibration:
   - Follow on-screen instructions to rotate boat through 360°
   - May require motoring in circles or swinging at mooring
4. Verify compass accuracy:
   - Compare pypilot heading to handheld compass
   - Should agree within ±5° after calibration
5. Perform accelerometer calibration:
   - Level boat at dock (if possible)
   - Follow calibration routine for pitch/roll sensors
6. Check heel compensation:
   - Have crew lean on one side to induce heel
   - Verify compass heading remains stable (not affected by heel)

**Success criteria:**

- ✓ Compass calibration completes without errors
- ✓ Heading matches handheld compass within ±5°
- ✓ Heading stable during induced heel
- ✓ No excessive compass noise or jitter (< 1° variance)

#### 2.2 Rudder Feedback Calibration (If Sensor Installed)

**Procedure:**

1. Turn rudder hard to port (manually or via engine)
2. Note pypilot rudder angle reading (should be minimum value)
3. Turn rudder hard to starboard
4. Note pypilot rudder angle reading (should be maximum value)
5. Set pypilot rudder limits:

   ```python
   # Via pypilot_client or web interface
   servo.rudder_min = [value at port limit]  # e.g., 5000
   servo.rudder_max = [value at starboard limit]  # e.g., 60000
   ```

6. Verify midpoint corresponds to rudder centered

**Success criteria:**

- ✓ Rudder angle tracks actual rudder position linearly
- ✓ Full rudder range mapped to 0-100% in pypilot
- ✓ Centered rudder reads approximately 50%

#### 2.3 Manual Control Test

**Procedure:**

1. Engage autopilot in manual mode (no heading hold)
2. Use web interface sliders to command rudder:
   - Small port command (~900)
   - Hold for 2 seconds, observe rudder movement
   - Return to neutral (1000)
   - Small starboard command (~1100)
   - Hold for 2 seconds, observe rudder movement
3. Test response time:
   - Time from command to visible rudder movement (should be < 1 second)
4. Test manual override:
   - While autopilot commanding rudder, manually turn wheel
   - Verify you can overpower autopilot easily
5. Test disengage:
   - Command autopilot to turn rudder
   - Click "Disengage" button
   - Verify rudder stops immediately (within 0.5 seconds)

**Success criteria:**

- ✓ Rudder responds to all commands correctly
- ✓ Response time < 1 second
- ✓ Manual override possible with moderate force
- ✓ Disengage stops rudder immediately
- ✓ No unusual noises or vibrations from pump

#### 2.4 Safety System Tests

**Test emergency stop:**

1. Engage autopilot and command rudder movement
2. Press emergency stop (if physical button installed)
3. Verify rudder stops immediately and pypilot shows fault

**Test over-current protection:**

1. Reduce `servo.max_current` to artificially low value (e.g., 500 = 5A)
2. Command rudder movement
3. Verify autopilot disengages with OVERCURRENT_FAULT
4. Reset `servo.max_current` to proper value (1500 = 15A)

**Test low voltage protection:**

1. Temporarily reduce voltage via voltage divider or adjust threshold
2. Verify autopilot disengages with BADVOLTAGE_FAULT below 9V
3. Restore normal voltage monitoring

**Test rudder limit switches (if installed):**

1. Turn rudder to physical port limit
2. Verify D7 fault switch triggers and autopilot prevents further port movement
3. Verify starboard commands still work
4. Repeat for starboard limit switch (D8)

**Success criteria:**

- ✓ All safety systems trigger appropriately
- ✓ Autopilot disengages and sets fault flags
- ✓ Faults clear when condition resolved
- ✓ Manual override always available regardless of fault state

#### 2.5 Power Consumption Baseline

**Equipment needed:**

- Clamp ammeter on 12V supply to pypilot system

**Procedure:**

1. Measure current with autopilot disengaged (standby):
   - Record Pi Zero + Arduino + GPS current draw
   - Typical: ~300-400mA (3.6-4.8W at 12V)
2. Measure current with autopilot engaged, rudder stationary:
   - Should be similar to standby (pump not running)
3. Measure current with rudder actively moving:
   - Record peak and average current
   - Compare to Octopus 1012 specifications (19A max)
4. Calculate duty cycle for typical course holding:
   - Time rudder is active vs. stationary over 5 minutes
   - Estimate average power consumption for passage planning

**Success criteria:**

- ✓ Standby power < 5W
- ✓ Active steering power matches pump specifications
- ✓ No unexpected high current draw (indicates mechanical binding)

### Phase 3: Motoring Trials (Calm Conditions)

**Goal**: Test autopilot in controlled motoring conditions, tune basic PID parameters.

#### 3.1 Compass Mode - Straight Line Test

**Conditions:** Calm water, no significant wind/current, motoring at 4-5 knots

**Procedure:**

1. Motor on steady heading for 2 minutes manually to establish baseline
2. Note compass heading, engage autopilot in Compass mode
3. Observe autopilot behavior for 10 minutes:
   - **Heading error**: How far from target heading does boat wander?
   - **Rudder activity**: How often does autopilot correct?
   - **Corrections**: Are they smooth or jerky?
   - **Oscillation**: Does boat weave side-to-side (hunting)?
4. Record data:
   - Maximum heading error (degrees)
   - Average rudder activity (% time pump running)
   - Frequency of corrections (per minute)
5. Try different speed settings (3 knots, 5 knots, 7 knots)
6. Record which speed produces smoothest autopilot behavior

**Success criteria:**

- ✓ Holds heading within ±10° (initial test, will improve with tuning)
- ✓ No continuous oscillation (hunting)
- ✓ Rudder corrections smooth, not hammering
- ✓ Manual override still easy

**Data to record:**

```text
Test: Motoring Compass Mode
Date/Time: ___________
Conditions: Wind ___ kts from ___, Sea state ___
Speed: ___ knots
Target heading: ___°

Initial PID values:
- P (servo.P): ___
- I (servo.I): ___  
- D (servo.D): ___

Results:
- Max heading error: ±___ degrees
- Avg heading error: ±___ degrees
- Rudder activity: ___% time
- Corrections per minute: ___
- Oscillation: Yes / No
- Notes: _________________
```

#### 3.2 GPS Track Mode - Waypoint Test

**Conditions:** Same as above, open water with room to maneuver

**Procedure:**

1. Set a waypoint 0.5nm ahead on current heading
2. Engage GPS track mode targeting that waypoint
3. Observe for 5 minutes:
   - Does boat track directly toward waypoint?
   - How much does track wander side-to-side?
   - Does autopilot anticipate and correct before getting off track?
4. Add a second waypoint requiring 30° course change
5. Observe turn behavior:
   - Does autopilot execute smooth turn?
   - Any overshoot or undershoot?
   - Time to settle on new course?

**Success criteria:**

- ✓ Tracks directly toward waypoint (minimal S-curves)
- ✓ Cross-track error < 50m (will improve with tuning)
- ✓ Smooth course changes without overshoot
- ✓ Settles on new heading within 30 seconds

#### 3.3 Initial PID Tuning (Motoring)

See [PID Tuning Guide](#pid-tuning-guide) section below for detailed tuning procedures.

**Quick tuning for motoring:**

1. **Start with conservative values:**

   ```python
   servo.P = 0.005  # Proportional gain
   servo.I = 0.0    # Integral (disable initially)
   servo.D = 0.1    # Derivative gain
   ```

2. **Increase P gradually:**
   - If boat wanders too much: Increase P by 0.001
   - If boat oscillates (hunting): Decrease P by 0.001
   - Target: Heading held within ±5° without oscillation

3. **Add I if needed:**
   - If boat has persistent offset (always 2° left of heading): Add small I (0.00001)
   - If oscillation appears: Reduce I or P

4. **Tune D for smoothness:**
   - If corrections are jerky: Increase D to 0.2
   - If too sluggish: Decrease D to 0.05

5. **Record final values** for future reference

### Phase 4: Sailing Trials (Light Wind)

**Goal**: Test autopilot under sail, tune for heel compensation and varying speeds.

#### 4.1 Sailing Compass Mode - Upwind

**Conditions:** 8-12 knots wind, close-hauled, heel 10-20°

**Procedure:**

1. Trim sails for optimal upwind performance manually
2. Establish steady heading for 2 minutes
3. Engage autopilot in Compass mode
4. Observe for 15 minutes:
   - **Heading stability**: More challenging under sail due to varying forces
   - **Heel compensation**: Does heading wander as boat heels more/less?
   - **Speed variations**: Does autopilot adapt to speed changes from gusts/lulls?
5. Tack through wind:
   - Use pypilot tack command (typically +/- 90-100°)
   - Observe autopilot behavior during and after tack
   - Does it settle on new heading smoothly?

**Success criteria:**

- ✓ Holds heading within ±5° while close-hauled
- ✓ Heading stable despite heel angle changes
- ✓ Successful tacks without manual intervention
- ✓ Settles on new heading within 45 seconds after tack

**Notes:**

- Sailing requires more aggressive PID tuning than motoring
- May need separate PID profiles for upwind vs. downwind

#### 4.2 Sailing Compass Mode - Downwind

**Conditions:** 8-12 knots wind, broad reach or run, minimal heel

**Procedure:**

1. Establish broad reach or run manually
2. Engage autopilot
3. Observe for 15 minutes:
   - Generally easier than upwind (less weather helm)
   - Watch for accidental jibes in following seas
4. Test jibe command:
   - Command jibe via pypilot (typically +/- 140-160°)
   - Observe turn and settling

**Success criteria:**

- ✓ Holds heading within ±3° on reach/run
- ✓ No accidental jibes
- ✓ Smooth controlled jibes when commanded

#### 4.3 Wind Mode Test (Future, After Wind Sensor Installation)

**Conditions:** Steady breeze, sailing close-hauled

**Procedure:**

1. Verify wind sensor data appearing in pypilot
2. Engage Wind mode, set apparent wind angle (e.g., 45°)
3. Observe:
   - Does boat maintain constant angle to wind as direction shifts?
   - Does it adapt smoothly to wind shifts?
4. Test across range of wind angles (close-hauled to broad reach)

**Success criteria:**

- ✓ Maintains constant apparent wind angle within ±5°
- ✓ Adapts to wind shifts within 5 seconds
- ✓ Stable in varying wind strengths

### Phase 5: Extended Passage Testing

**Goal**: Validate reliability and performance over multi-hour passages.

#### 5.1 Coastal Passage (4-6 Hours)

**Conditions:** Day sail, good visibility, moderate conditions

**Procedure:**

1. Engage autopilot at start of passage
2. Monitor continuously for first hour, then check every 15 minutes
3. Record:
   - Any manual interventions required (and why)
   - Heading errors at check points
   - Power consumption (battery state of charge before/after)
   - Any fault conditions or warnings
   - Performance in varying conditions (wind shifts, sea state changes)
4. Test mode changes:
   - Switch between Compass and GPS track modes
   - Verify smooth transitions

**Success criteria:**

- ✓ Operates unattended for > 4 hours
- ✓ No unexpected faults or disengagements
- ✓ Course keeping within ±5° average
- ✓ Power consumption acceptable for long passages
- ✓ Mode changes work reliably

#### 5.2 Overnight Passage (8-12 Hours)

**Conditions:** Extended sail, watch-keeping crew, moderate to fresh conditions

**Procedure:**

1. Begin passage with autopilot engaged
2. Maintain watch schedule with regular autopilot checks
3. Document:
   - Night vision compatibility (LED brightness, screen glare)
   - Ease of mode changes in darkness
   - Response to changing conditions overnight
   - Reliability over extended period
4. Monitor battery charge throughout passage

**Success criteria:**

- ✓ Operates reliably through night passage
- ✓ Watch keepers comfortable with autopilot behavior
- ✓ No surprise disengagements
- ✓ Battery budget sustainable for longer passages

### Phase 6: Heavy Weather Testing

**Goal**: Validate autopilot performance and safety in challenging conditions.

⚠️ **Only proceed with heavy weather testing after all previous phases completed successfully**

#### 6.1 Moderate Sea State (2-3m Waves)

**Procedure:**

1. Start in moderate conditions (15-20 knots wind, 2m seas)
2. Engage autopilot in Compass mode
3. Observe:
   - Does autopilot maintain course in waves?
   - Excessive rudder activity (thrashing)?
   - Ability to handle broaching forces?
4. If performance degraded:
   - Adjust PID gains (typically increase D for damping)
   - Reduce `servo.max_slew_speed` to prevent overcorrection
   - Consider reducing sail area if weather helm excessive

**Success criteria:**

- ✓ Maintains course within ±10° in moderate seas
- ✓ Rudder activity appropriate (not constant thrashing)
- ✓ No loss of control or broaching
- ✓ Manual override still easy if needed

#### 6.2 Current and Load Monitoring

**Procedure:**

1. Monitor motor current during heavy weather operation
2. Check for:
   - Peak currents approaching `servo.max_current` limit
   - Over-temperature warnings
   - Excessive duty cycle (pump running constantly)
3. Adjust if needed:
   - Increase `servo.max_current` if limiting performance (but stay below pump rating)
   - Add cooling for IBT-2 if overheating
   - Reduce sail if excessive weather helm

**Success criteria:**

- ✓ Current stays below pump rating (19A max for Octopus 1012)
- ✓ No over-temperature faults
- ✓ Pump not running continuously (should have idle periods)

---

## PID Tuning Guide

### Understanding PID Control

Pypilot uses a PID (Proportional-Integral-Derivative) controller to maintain heading:

- **P (Proportional)**: Responds to current heading error
  - Higher P = more aggressive corrections
  - Too high = oscillation (hunting)
  - Too low = slow response, large heading errors

- **I (Integral)**: Responds to accumulated error over time
  - Eliminates persistent offset (e.g., weather helm)
  - Too high = slow oscillations, overshoot
  - Can often be kept at zero or very small

- **D (Derivative)**: Responds to rate of change of error
  - Dampens oscillations, smooths corrections
  - Higher D = smoother, but may reduce responsiveness
  - Too high = sluggish response, "dead" feeling

### Ziegler-Nichols Tuning Method (Modified for Marine Use)

### Step 1: Find Critical Gain (Ku)

1. Set I = 0, D = 0
2. Set P to small value (0.001)
3. Increase P gradually until boat begins sustained oscillation (hunting)
4. Record P value where oscillation starts = Ku (critical gain)
5. Measure oscillation period in seconds = Tu (critical period)

### Step 2: Calculate Initial PID Values

For "some overshoot" (good for autopilot):

```python
P = 0.33 × Ku
I = 0.5 × P / Tu  
D = 0.33 × P × Tu
```

For "no overshoot" (conservative):

```python
P = 0.2 × Ku
I = 0.4 × P / Tu
D = 0.067 × P × Tu  
```

### Step 3: Fine-Tune by Observation

1. Test calculated values in real conditions
2. Adjust based on behavior:

   **If heading wanders too much:**
   - Increase P by 20%

   **If boat oscillates (hunts):**
   - Decrease P by 20%
   - Or increase D by 50%

   **If persistent offset (always left/right of heading):**
   - Increase I by small amount (double it, starting from 0.00001)

   **If corrections too jerky:**
   - Increase D by 50%

   **If too sluggish:**
   - Decrease D by 30%
   - Or increase P by 20%

### Typical PID Values (Starting Points)

```python
# Light displacement sailboat (< 5 tons)
servo.P = 0.008
servo.I = 0.00002
servo.D = 0.15

# Medium displacement sailboat (5-15 tons)  
servo.P = 0.005
servo.I = 0.00001
servo.D = 0.1

# Heavy displacement (> 15 tons)
servo.P = 0.003
servo.I = 0.000005
servo.D = 0.08

# Motoring (all sizes) - generally more aggressive
servo.P = 0.01
servo.I = 0.00005
servo.D = 0.2
```

### Condition-Specific Tuning

**Upwind sailing:**

- Higher P for responsiveness to wind shifts
- Higher D to dampen oscillation from waves
- Small I to counter weather helm

**Downwind sailing:**

- Lower P (less weather helm, easier steering)
- Moderate D for smoothness
- Very small or zero I

**Heavy weather:**

- Lower P to prevent overcorrection in waves
- Much higher D for damping (may double or triple)
- Reduce `servo.max_slew_speed` to prevent thrashing

**Light air:**

- May need higher P for responsiveness at low speeds
- Lower D (less momentum to dampen)

### Advanced Tuning Parameters

```python
# Slew rate limits (degrees/second of rudder movement)
servo.max_slew_speed = 15  # Maximum rate during speed changes
servo.max_slew_slow = 5    # Maximum rate when slowing down

# Lower values = smoother but slower response
# Higher values = faster but potentially jerky

# Current limits
servo.max_current = 1500  # 15A - conservative for Octopus 1012
# Increase if current limiting in heavy weather
# Never exceed pump rating (19A for Octopus 1012)

# Temperature limits  
servo.max_controller_temp = 6000  # 60°C
servo.max_motor_temp = 7000       # 70°C
# Lower if components run hot
```

### Saving and Loading PID Profiles

Create multiple profiles for different conditions:

```python
# In pypilot_client or via web interface:

# Save current settings
pypilot_client_save motoring_profile

# Load profile  
pypilot_client_load heavy_weather_profile

# Or edit ~/.pypilot/autopilot.conf manually
# Create sections like:
# [motoring]
# P = 0.01
# I = 0.00005
# D = 0.2

# [upwind_sailing]
# P = 0.008
# I = 0.00002  
# D = 0.15
```

## Troubleshooting Common Issues

### Issue: Boat Oscillates (Hunts) Side-to-Side

**Symptoms:** Constant S-curve weaving, heading passes through target repeatedly

**Causes:**

- P gain too high
- D gain too low
- Speed too low (autopilot over-controls at low speeds)

**Solutions:**

1. Reduce P by 20-30%
2. Increase D by 50-100%
3. If at low speed (< 2 knots), increase speed or hand-steer

### Issue: Large Heading Errors (Boat Wanders)

**Symptoms:** Heading consistently 5-10° off target, slow to correct

**Causes:**

- P gain too low
- I gain too low (if persistent offset in one direction)
- Excessive rudder deadband

**Solutions:**

1. Increase P by 20-30%
2. If offset always same direction, add small I (start at 0.00001)
3. Check for mechanical binding in steering system

### Issue: Jerky, Hammering Corrections

**Symptoms:** Pump starts/stops rapidly, jarring corrections

**Causes:**

- D gain too low
- Slew rate too high
- Sensor noise causing rapid command changes

**Solutions:**

1. Increase D by 50-100%
2. Reduce `servo.max_slew_speed` by 30%
3. Check IMU mounting for vibration
4. Verify compass calibration

### Issue: Autopilot Disengages Unexpectedly

**Symptoms:** Autopilot stops, fault flag set

**Causes:**

- Over-current fault (binding, low battery, high load)
- Over-temperature fault (poor ventilation, high ambient temp)
- Bad voltage fault (low battery, poor connections)
- Communication timeout (Pi Zero crashed or Arduino disconnected)

**Solutions:**

**For OVERCURRENT_FAULT:**

1. Check `servo.current` reading - if near `servo.max_current`, increase limit
2. Verify battery voltage under load (should be > 12V)
3. Check for mechanical binding in steering system
4. Ensure hydraulic fluid level adequate

**For OVERTEMP_FAULT:**

1. Improve ventilation around Arduino and IBT-2
2. Reduce duty cycle (less aggressive PID gains, lower slew rate)
3. Lower `servo.max_controller_temp` threshold for earlier warning

**For BADVOLTAGE_FAULT:**

1. Check battery state of charge
2. Test voltage at Arduino under load (should be > 11V)
3. Verify wiring connections (no voltage drop due to resistance)
4. Consider larger wire gauge or dedicated circuit for autopilot

**For communication timeout:**

1. Check USB connection between Pi Zero and Arduino
2. Verify Arduino still running (D13 LED should flash)
3. Check Pi Zero hasn't locked up (ping 192.168.43.101)
4. Check USB cable quality (data+power, not power-only)

### Issue: Autopilot Works but Power Consumption Too High

**Symptoms:** Battery drains faster than expected during autopilot use

**Causes:**

- Excessive rudder activity (PID gains too aggressive)
- Mechanical friction in steering system
- Current sense calibration incorrect (reading low, allowing excessive current)

**Solutions:**

1. Reduce PID gains (less rudder activity)
2. Increase D gain (smoother corrections use less power)
3. Lubricate steering components, check hydraulic system
4. Recalibrate current sense with accurate ammeter
5. Verify pump not stalling or binding

### Issue: GPS Mode Doesn't Work

**Symptoms:** GPS mode available but boat doesn't track waypoints

**Causes:**

- No GPS fix (not enough satellites)
- GPS data not reaching pypilot
- Cross-track error tolerance too tight

**Solutions:**

1. Verify GPS has fix:

   ```bash
   pypilot_client 192.168.43.101 | grep gps.fix
   # Should show: gps.fix = True
   ```

2. Check GPS receiver connection (USB, power LED)
3. Give GPS time to acquire fix (may take 1-5 minutes cold start)
4. Verify GPS data in pypilot logs:

   ```bash
   tail -f ~/.pypilot/pypilot.log | grep NMEA
   ```

5. Check waypoint is set correctly in OpenCPN or pypilot interface

## Data Logging and Performance Analysis

### Enable Detailed Logging

```bash
# On Tinypilot Pi Zero, edit /etc/pypilot.conf or start pypilot with:
pypilot --log_dir=/home/tc/logs --verbose

# Logs will be written to specified directory
# Useful for post-passage analysis
```

### Key Metrics to Log

- **Heading error** (actual vs. target heading)
- **Rudder position** (if sensor installed)
- **Motor current** (average and peak)
- **Corrections per minute** (measure of autopilot activity)
- **GPS track deviation** (cross-track error in GPS mode)
- **Power consumption** (battery state over time)
- **Fault events** (any disengagements or warnings)

### Analyzing Logs

```python
# Example Python script to analyze pypilot logs:
import json

with open('pypilot.log') as f:
    for line in f:
        if 'ap.heading_error' in line:
            data = json.loads(line)
            heading_error = data['ap.heading_error']
            # Calculate RMS error, max error, etc.
```

## Performance Benchmarks

After tuning, your system should achieve:

| Metric | Target (Motoring) | Target (Sailing) |
| -------- | ------------------ | ------------------ |
| Heading hold accuracy | ±2° RMS | ±3° RMS |
| Maximum heading error | < 5° | < 8° |
| Corrections per minute | 5-15 | 10-25 |
| Rudder duty cycle | < 30% | < 50% |
| Response time to 10° error | < 3 seconds | < 5 seconds |
| Settling time after course change | < 30 seconds | < 60 seconds |
| Power consumption (standby) | < 5W | < 5W |
| Power consumption (active avg) | 30-60W | 40-80W |

## Pre-Passage Checklist

Before each passage using autopilot:

- [ ] Verify pypilot web interface accessible
- [ ] Check IMU calibration status (should be "Calibrated")
- [ ] Confirm GPS fix acquired (if using GPS mode)
- [ ] Test manual rudder movement (verify hydraulic system responsive)
- [ ] Engage autopilot briefly, test disengage function
- [ ] Check current PID profile loaded for conditions
- [ ] Verify battery state of charge adequate for passage duration
- [ ] Check `servo.current` and `servo.voltage` readings normal
- [ ] Review weather forecast, adjust PID if heavy weather expected
- [ ] Ensure crew familiar with autopilot disengage procedures

## Post-Passage Maintenance

After each extended passage:

- [ ] Review pypilot logs for any fault events
- [ ] Check motor current trends (any increases suggest mechanical wear)
- [ ] Inspect IBT-2 for overheating signs (discoloration, smell)
- [ ] Check Arduino connections (USB, sensor wiring)
- [ ] Verify hydraulic fluid level
- [ ] Test manual override still easy
- [ ] Check battery voltage recovery after passage
- [ ] Update PID tuning notes if adjustments made

---

**Document Version**: 1.0  
**Last Updated**: January 20, 2026  
**Part of**: [pypilot4arion](https://github.com/botheredbybees/pypilot4arion) project  
**Related Docs**: [Installation Guide](README.md), [Arduino Setup](docs/flashing_motor_ino_to_arduino.md)

---

For questions or to report issues with testing procedures, please open an issue on the [pypilot4arion GitHub repository](https://github.com/botheredbybees/pypilot4arion/issues).
