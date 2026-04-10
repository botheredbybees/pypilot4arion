Technical Briefing: Open-Source Marine Navigation and Control Systems

Executive Summary

The transition toward open-source marine computing—represented by platforms such as OpenPlotter, BBN Marine OS, and SignalK—aims to replace proprietary, isolated hardware with a connected "Internet of Things" (IoT) ecosystem. These systems leverage low-cost hardware like Raspberry Pi and Arduino to perform complex tasks including chartplotting, weather routing, and autopilot control via Pypilot. However, successful implementation requires addressing significant hardware integration challenges. Key among these are the electrical sensitivities of sensors (e.g., the 1.8V logic of ICM-20948 IMUs), the thermal and design flaws of high-current motor drivers (BTS7960), and the complexities of managing bi-directional data flow across serial and network ports to avoid data loops.

The Marine Computing Ecosystem

Open-source marine operating systems, specifically OpenPlotter and BBN (Bareboat Necessities) Marine OS, provide a centralized hub for navigation and vessel monitoring.

Core Components and Capabilities

* Navigation and Chartplotting: Integration of OpenCPN, AvNav, and Freeboard-SK for mapping, weather GRIB viewing (XyGrib), and AIS tracking.
* Data Protocols: Support for NMEA 0183, NMEA 2000 (via CAN bus), Seatalk, and SignalK.
* Environmental Sensing: Interfaces for I2C and 1-Wire sensors to track temperature, pressure, humidity, and tank levels.
* Software Defined Radio (SDR): Capabilities for receiving AIS, weather fax, NAVTEX, and satellite weather (NOAA-APT).
* Energy Efficiency: Optimized for ARM-based processors (Raspberry Pi 4/5) to minimize power consumption on board.

SignalK: The Modern Data Standard

SignalK serves as the next-generation solution for marine data exchange, designed to overcome the limitations of NMEA standards.

* Technical Advantages: Unlike NMEA 0183 (limited baud rates) or NMEA 2000 (proprietary/certified), SignalK is an open, JSON-based protocol that allows sharing data between vessels and land-based resources.
* Security: Incorporates modern encryption (HTTPS/WSS) and authorization techniques similar to online banking.
* Extensibility: Features a "Plugin Store" and Node-RED integration for custom logic, such as automated alarms or geofencing.

Pypilot: Open-Source Autopilot Implementation

Pypilot is the central autopilot system within the OpenMarine ecosystem, but its reliability is heavily dependent on precise hardware configuration and calibration.

Hardware Integration and IMU Criticality

The Inertial Measurement Unit (IMU) provides heading and attitude data. The sources highlight frequent failure points:

* Voltage Mismatch: High-performance sensors like the ICM-20948 operate at 1.8V. Connecting them directly to a Raspberry Pi's 3.3V GPIO can cause intermittent detection, permanent damage, or compass "lock-up." Use of level-shifting circuitry is mandatory.
* Detection Errors: Common logs such as I2C read error or Failed to read compass fuse ROM often indicate hardware failure or improper library versions (RTIMULib2).
* Calibration Requirements: Stable heading requires specific accelerometer and compass calibration sequences. Calibration data is typically stored in ~/.pypilot/pypilot.conf.

Data Flow and Port Management

* Bidirectional NMEA: Pypilot communicates via port 20220. OpenCPN can send and receive data on this port for autopilot routing.
* Port Probing and Blacklisting: By default, Pypilot probes all serial ports for motor controllers. This can hijack NMEA 2000 converters (like the Actisense NGT1) or GPS devices.
  * Solution: Users must manually add devices to ~/.pypilot/blacklist_serial_ports to prevent Pypilot from claiming them.
* SignalK Zeroconf: Pypilot can automatically connect to SignalK via mDNS, provided the "mdns" setting is enabled in the SignalK server and the access request is approved.

Motor Control Hardware: BTS7960 (IBT-2) Analysis

The BTS7960 is a common high-current H-bridge driver used to move rudder actuators. While cost-effective, it possesses several design vulnerabilities.

Technical Specifications and Connectivity

Pin	Name	Description
1	RPWM	Forward PWM input (Active HIGH)
2	LPWM	Reverse PWM input (Active HIGH)
3	R_EN	Forward enable (Set HIGH)
4	L_EN	Reverse enable (Set HIGH)
7	VCC	5V Logic power
8	GND	Ground

Hardware Flaws and Risks

* Thermal Design: The BTS7960 chip (TO263 package) dissipates heat primarily through the PCB copper, not the metal back. The large heatsink provided is often poorly implemented.
* Short Circuit Risk: The heatsink is often screwed directly onto vias that are electrically connected to the motor outputs. The only insulation is the paint on the heatsink, creating a severe risk of shorting motor outputs together.
* Ground Loops: Creating redundant ground connections between the Arduino/Raspberry Pi and the high-current battery ground can lead to destructive ground loops.

Performance Optimization

* Switching Frequency: Standard Arduino PWM (488 Hz) is insufficient for DC motors; 20 kHz is recommended to avoid audible noise.
* Switching Losses: At 20 kHz, switching losses can be 10 times higher than resistance losses. Reducing the slew rate resistor (programming the SR pin) can reduce these losses by approximately 40% but may increase RF noise.
* Current Sensing: The IS pins provide a current alarm/output. This output is only active when the "Top FET" of the H-bridge is on, requiring precise timing for accurate readings during PWM cycles.

RF Sensing and SDR Reliability

Using SDR (rtl_433) on low-power hardware like the Raspberry Pi Zero for environmental monitoring presents unique challenges.

* Noise Floor Management: An ideal noise floor is around -20 dB to -30 dB. Signals near 0 dB cause clipping and impede decoding.
* Hardware Shielding: Dongles should not be plugged directly into the Raspberry Pi due to unshielded noise; USB extensions are recommended.
* Tuning: Using the -Y autolevel option in rtl_433 helps manage varying signal-to-noise ratios (SNR). High-quality dongles with a Temperature Compensated Crystal Oscillator (TCXO) and metal cases are preferred for frequency stability.

Key Technical Quotes

"The presence of the 74HC244 [on the BTS7960] is a mystery... Its not acting as a level shifter if you are using a 3.3V micro." — adam_david_66

"Whichever program reads directly from the gps must be running then and if it stops all the others will lose it." — seandepagnier

"The ICM-20948 runs on 1.8V which is increasingly common for device manufacturers but isn't hardly common for makers... it can be a bit particular about how it needs to be worked with." — Jean-Marc Douroux

"The only thing stopping this [BTS7960] from shorting the motor outputs together is the paint on the heatsink." — adam_david_66

Building a DIY marine autopilot system requires a multi-layered approach that integrates **specialised processing units**, a robust **motor control** interface, and a **unified data network** to handle navigation and sensor fusion. The sources recommend a distributed architecture to ensure that failures in non-critical navigation software do not compromise core steering reliability.

### **The "Tri-Pi" System Architecture**
A proven high-level architecture separates responsibilities across three dedicated Raspberry Pi nodes:
*   **Steering Node (Pi 3B):** Dedicated to the **PyPilot server**, the **ICM-20948 IMU**, and a local USB GPS. It connects directly to the Arduino motor controller.
*   **Navigation/Hub Node (Pi 4):** Acts as the master **Signal K** server. It handles resource-intensive tasks like **OpenCPN** chart plotting, data logging (InfluxDB), and visual dashboards (Grafana).
*   **Wind Bridge (Pi Zero WX):** A low-power, solar-friendly remote node that uses **rtl_433** and an RTL-SDR dongle to decode signals from wireless sensors like the **Ecowitt WS80**.

### **Core Autopilot Implementation: PyPilot & Arduino**
The steering core consists of the PyPilot server communicating with a dedicated motor controller node:
*   **Motor Firmware:** An **Arduino Nano** runs the `motor.ino` sketch, which provides safety monitoring and interfaces with the hardware.
*   **Power Driver:** The **IBT-2 (BTS7960B)** H-bridge is the recommended driver for reversible DC pumps, such as the Octopus Model 1012. 
*   **Critical Wiring:** For H-bridge mode, **pin D6 on the Arduino must be grounded**; if left floating, the firmware defaults to RC servo mode and will not drive the IBT-2 correctly.
*   **Safety:** The Arduino enforces current and temperature limits and will disengage the pilot upon detecting a fault. An inline **30A fuse** near the battery is essential for the IBT-2 main supply.

### **Wind Integration: WS80 and rtl_433**
To enable **Wind Mode** steering, the system must ingest data from the Ecowitt WS80 ultrasonic anemometer:
1.  **Decoding:** The **rtl_433** utility on the Pi Zero or Pi 4 decodes the 433MHz RF packets into JSON format.
2.  **Signal K Injection:** Data is piped into Signal K via an **MQTT bridge** or the `signalk-rtl433` plugin.
3.  **Mapping:** Raw values are mapped to standard marine paths like `environment.wind.speedApparent`.
4.  **Steering:** Once Signal K shares this data, the "Wind" button in the PyPilot interface becomes active, allowing the boat to maintain a constant **Apparent Wind Angle (AWA)**.

### **Data Management: Signal K & OpenCPN**
**Signal K** serves as the central "toolbox" that fuses data from heterogeneous sources (NMEA 0183, NMEA 2000, and generic sensors) into a single web-friendly model.
*   **PyPilot Connectivity:** PyPilot connects to Signal K via websockets. For data flow to be bidirectional, you must approve the **Access Request** in the Signal K security menu.
*   **Navigation Interface:** **OpenCPN** is used as the primary graphical interface. Through the **PyPilot plugin**, users can select waypoints on a chart ("Navigate to Here"), which automatically engages **GPS mode** on the autopilot.
*   **Port Management:** PyPilot uses port **20220** for NMEA data, while Signal K typically uses port **10110** for NMEA 0183 streams.

### **Reliability and Common Issues**
*   **Power Stability:** Using low-quality cigarette-plug USB adapters for the Pi 3B or Pi 4 often leads to **IMU noise**, heading jumps, or CPU throttling. High-quality **buck converters** are strongly preferred for stability.
*   **RF Interference:** RTL-SDR dongles should be plugged into **USB 2.0 ports** (black) rather than USB 3.0 ports (blue), as the latter generate significant RF interference that can drown out 433MHz signals.
*   **IMU Calibration:** The **ICM-20948** is extremely sensitive. It must be mounted in a plastic enclosure away from magnetic metal or high-current wires. Calibration requires rotating the IMU along all axes until the readings fit an optimal sphere in the PyPilot calibration utility.
*   **USB Disconnects:** Stalling data streams can be caused by **USB autosuspend** settings in the Linux kernel; this should be disabled to ensure continuous SDR operation.

Building the Brain of Your Boat: 5 Surprising Lessons from the DIY Autopilot Trenches

1. Introduction: The "Open Sea" of Open Source Hardware

The dream is seductive: a high-performance marine computer for a fraction of the cost of proprietary systems. By combining a Raspberry Pi with OpenPlotter, Signal K, and the Pypilot autopilot system, you gain the power to integrate everything from celestial navigation to real-time engine monitoring.

However, the reality of the DIY "bilge" is often less about serene sailing and more about troubleshooting at 2:00 AM while the boat rolls in a harbor. You might follow every manual perfectly and still be greeted by "Device or resource busy" errors or a compass heading that simply refuses to move. This "Open Sea" of open-source hardware is vast, and while the official documentation is a starting point, the real wisdom is buried in the trial-and-error logs of the global community.

This guide distills five critical technical takeaways from the front lines of marine systems architecture to help you navigate the common pitfalls of the Signal K/Pypilot ecosystem.


--------------------------------------------------------------------------------


2. Takeaway 1: The GPS "Monopoly" (Why Your Data Disappears)

In the world of Linux-based marine electronics, serial ports are jealous. If you connect a USB GPS and identify it at /dev/ttyOP_gps, you may find that as soon as you start Pypilot, your chartplotter (OpenCPN) or Signal K dashboard loses the signal.

This happens because only one process can read from a serial device at a time. If Pypilot probes the system and grabs the port to look for a motor controller or GPS data, Signal K will throw a "Device or resource busy" error.

"It's true that only one program can read from one device such as gps. It's possible that this can be gpsd, opencpn, pypilot, or even signalk server, and all of these can relay the data to all of the others. Whichever program reads directly from the gps must be running then and if it stops all the others will lose it." — seandepagnier, Pypilot Lead Developer

The "Bilge-Level" Pro-Tip: To stop Pypilot from "pinching" ports it shouldn't touch, you must manually manage its probing behavior. You can explicitly tell Pypilot to ignore your GPS port by adding the full path (e.g., /dev/ttyOP_gps) to the file ~/.pypilot/blacklist_serial_ports. Alternatively, you can create ~/.pypilot/serial_ports and list only the ports you want it to use. If neither file exists, Pypilot will probe every available port on startup, likely breaking your data flow.

3 Ways to Bring GPS to Your System:

1. The gpsd Middle-Man: Configure the gpsd service to read the hardware device directly. Both Pypilot and OpenCPN then connect to the gpsd stream.
2. Signal K Distribution (Recommended): Let Signal K act as the primary reader. Pypilot (version 0.2+) can receive data via Signal K. Note: You must grant Pypilot read/write permissions in the Signal K security menu for this loop to close.
3. Pypilot Forwarding: Assign the USB device to Pypilot. If granted proper permissions, it can forward the GPS data to Signal K via websockets.


--------------------------------------------------------------------------------


3. Takeaway 2: The IBT-2 Motor Driver’s "Heatsink Death Trap"

The IBT-2 (BTS7960) is a popular, low-cost H-bridge motor driver used to move heavy autopilot rudders. It features a massive aluminum heatsink that suggests high-current reliability, but the physical design contains a critical flaw that has led to many "magic smoke" incidents.

The power ICs (BTS7960) use the TO263 package, which relies on the metal tab on the back to dissipate heat into the PCB. The manufacturer then places the aluminum heatsink against the bottom of the PCB. Here is the danger: the via holes used to transfer heat through the board are electrically connected to those tabs—which are the motor outputs.

WARNING: The only thing stopping a total system meltdown is a micron of paint on the heatsink. Screwing that aluminum block directly against the PCB vias is a terrible idea because those vias carry motor current. Furthermore, the mounting screws often lack sufficient clearance on the top-side copper layer; the screw heads can easily bite through the solder mask and short the copper pour.

For most DIY tiller pilots, it is safer to leave the heatsink off entirely. The top-side copper areas of the PCB are the primary heat conductors, and the bottom-side heatsink is more for show than performance.


--------------------------------------------------------------------------------


4. Takeaway 3: The 1.8V Logic Lie (Protecting Your IMU)

The ICM-20948 is the "gold standard" Inertial Measurement Unit (IMU) for Pypilot, but it is frequently misused. While many modules are marketed as "3.3V compatible," there is a vital distinction you need to understand: VDD vs. VDDIO. VDD is the "Power" for the chip, while VDDIO is the voltage level for "Talking" (the I2C signal).

The ICM-20948 chip is designed for 1.8V logic. The Raspberry Pi’s GPIO operates at 3.3V. If you use a "bare" module that lacks its own 1.8V regulator and level-shifting circuitry, you are overvolting the sensor's I2C bus. Don't let the "3.6V max VDD" on the spec sheet fool you; the communication pins are often much more fragile.

Symptoms of a fried or improperly powered IMU:

* The "Half-Dead" Sensor: The Accelerometer appears to work (it reacts to tilt), but the Compass is locked in place or returns to a phantom heading regardless of boat rotation.
* Specific Error Codes: Look in your logs for I2C read error from 12, 16 or the dreaded Failed to read compass fuse ROM.

To avoid burning your fingers and your wallet, always use a high-quality module (like the GY-ICM20948V2 or Adafruit version) that includes dedicated level shifters for 3.3V/5V compatibility.


--------------------------------------------------------------------------------


5. Takeaway 4: The Invisible Wall of Signal K ZeroConf

One of the most common frustrations for new builders is the "Invisible Wall": you have Signal K running and Pypilot active, but they simply won't talk. Even though they are on the same machine, the data doesn't flow.

Since version 0.2, Pypilot attempts to connect to Signal K automatically via a ZeroConf/mDNS mechanism. However, the connection will remain blocked by Signal K's security layer until you open the gate.

Unblocking the Data Flow Checklist:

1. Enable mDNS: In Signal K server settings, ensure 'mDNS' is switched ON. This is often disabled by default and is required for Pypilot to find the server.
2. Restart the Server: Many Signal K settings—especially mDNS—require a full server restart to take effect.
3. Approve the Access Request: Navigate to the Signal K Security menu. You will likely see a pending Access Request from Pypilot.
4. Verify the Token: You must manually approve this request. Crucially, ensure the generated Signal K Token is granted read/write permissions. Without "Write" access, Pypilot cannot send steering commands or processed sensor data back to the network.


--------------------------------------------------------------------------------


6. Takeaway 5: Taming the RF Ghost (RTL-SDR on Low-Power Pi’s)

Using an RTL-SDR dongle to track AIS or 433MHz weather sensors is a great way to expand your boat's "senses." However, running these on a Raspberry Pi Zero requires careful tuning to avoid signal clipping and CPU exhaustion.

"Auto Gain" is the enemy of performance on cheap SDR dongles. It frequently drives the signal to 0 dB, making decoding impossible.

Pro-Tips for SDR Stability:

* Manual Gain: Set a manual gain (typically between 35 and 38 dB). Your goal is to have signals land between -1 dB and -9 dB for optimal decoding.
* Use Autolevel: Add the -Y autolevel flag in your rtl_433 command to lower the minimum signal level (RSSI) required for a clear read.
* The USB Extension Rule: Never plug an SDR dongle directly into the Pi. The Raspberry Pi emits a cloud of unshielded RF noise that will drown out weak signals. Use a USB extension cable to move the dongle at least a foot away from the processor.
* Performance Goals: In a clear band, aim for a noise floor of -20 dB to -30 dB. Reliable sensor updates generally require an SNR (Signal-to-Noise Ratio) above 9 dB.


--------------------------------------------------------------------------------


7. Conclusion: The Future is Interconnected

We are leaving the era of isolated NMEA 0183/2000 hardware silos. In the new "Internet of Things" approach championed by Signal K and BBN Marine OS, the network is the computer. This shift allows your boat to stop being an "island" and start acting as a central cockpit front-end—integrating celestial navigation, weather routing, and advanced sensor fusion into a single, extensible platform.

By mastering these "trenches" of DIY electronics, you aren't just building an autopilot; you're building a resilient system that can grow with every new sensor you add to the network.

Is your boat still an island, or is it ready to join the global peer-to-peer marine network?


Standard MS-RPi-2026: Technical Standard for Marine-Grade Raspberry Pi Deployments

1. Scope and Strategic Context

Compliance with MS-RPi-2026 is mandatory for all hull-integrated compute deployments. As the maritime industry transitions from proprietary "black box" electronics to transparent, open-source stacks—including BBN OS, OpenPlotter, and Pypilot—the burden of engineering integrity shifts from the manufacturer to the systems architect. Consumer-grade hardware, specifically the Raspberry Pi, is not inherently marine-grade; it requires a rigorous application of electrical safety and software orchestration to prevent catastrophic failure at sea. Adhering to these protocols transforms a hobbyist board into a professional-grade marine computer capable of surviving the extreme overvoltages, brownouts, and electromagnetic interference (EMI) characteristic of offshore environments. This standard establishes the baseline for physical power architecture and system hardened-state configurations.

2. Power Delivery Architecture and Electrical Safety

System availability is a life-safety requirement. Failure to adhere to regulated power delivery protocols constitutes a critical system risk. Power instability remains the primary failure point in marine computing, leading to SD card corruption and the loss of navigation services during high-vibration or heavy-weather events.

Power Method	Stated Requirements	Protection Level	Recommended Use Case
USB-C Port	5.1V / 3.0A	Integrated Fuse/TVS Diode	Primary Port; requires official RPi supply. Note: Consumer cables introduce high resistance-induced voltage drop.
GPIO Header	Regulated 5.1V	None (Bypasses internal protection)	HAT-integrated; Mandates external filtering and high-precision regulation. High-risk/High-reward.
PoE / PoE+	802.3at Standard	Galvanically Isolated	Network-intensive; requires official PoE+ HAT to support peripheral current spikes.

Critical Voltage Thresholds and Monitoring

* Operating Nominal: All deployments shall maintain 5.1V to provide adequate headroom for peripheral load spikes.
* Red LED Diagnostic (Pi 4/5):
  * Continuous Red: Regulated power detected above 4.64V.
  * Blinking Red (<4.64V): Critical undervoltage. Immediate brownout risk.
  * LED Off: System shutdown. The Power Management IC (PMIC) has ceased operation to prevent hardware destruction.
* Mandatory "Don'ts" for Electrical Integrity:
  * Prohibition of Conductivity: Never mount boards on metal or conductive surfaces without a verified non-conductive isolation interface.
  * Pin Safety: Shorting 3.3V lines to ground or other pins is a fatal error that will result in immediate CPU destruction.
  * Header Isolation: Verify all header pins are clear of conductive debris or uninsulated probe contact during live maintenance.

3. High-Current Subsystems: Motor Driver Integration (BTS7960/IBT-2)

Autopilot drive units require total isolation from the logic-level Raspberry Pi to prevent EMI-induced sensor stall and thermal runaway. Architects shall prioritize isolation of high-current paths from I2C and GPIO signaling.

Mandatory Hardware Correctives (Citing Infineon AN-2021-02)

1. Thermal Management Realities: Disregard the standard aluminum heatsink provided with IBT-2 modules; it is largely cosmetic. As specified in Infineon Application Note AN-2021-02, the BTS7960 (TO263 package) dissipates heat primarily through the PCB copper pour. High-current installations shall prioritize airflow across the PCB surface rather than the heatsink.
2. Logic Inversion for Thermal Stability: At a 20kHz switching frequency, switching losses are approximately 10x higher than resistance-based (Rds-on) losses. Software logic inversion is mandatory: the H-bridge side not receiving the PWM signal shall be held at 100% duty cycle (Always High). This ensures the diagnostic IS pin remains active continuously for stable current sensing and reduces total thermal flux.
3. Electrical Short Circuit Prevention: The IBT-2 heatsink is separated from electrically live vias only by a thin layer of paint. To prevent motor output shorts, verify screw head clearance and apply a non-conductive thermal interface (e.g., Kapton tape or thermal pads) if a heatsink must be used.
4. Ground Loop Prohibition: Disregard hobbyist wiring diagrams (e.g., HandsOn Technology) that suggest shared signal/power grounds at the module. Architects shall forbid any connection between the Pi/Arduino Ground and the Battery Negative that facilitates a ground loop. Signal and power grounds must only meet at a single, verified reference point.

4. System Security and Service Orchestration

In a maritime "Internet of Things" environment, unauthorized navigation data access constitutes a direct threat to vessel safety.

* Credential Hardening: Default credentials (Username: 'user' / Password: 'changeme') shall be replaced immediately upon OS initialization.
* SignalK Security Protocol:
  * mDNS (ZeroConf): Shall be enabled to facilitate legitimate service discovery.
  * Authorization: All data consumers require a manual Access Request. Tokens shall be audited and approved via the SignalK Security menu; unverified tokens are a critical vulnerability.
* Service Orchestration via systemd:
  * All critical services (SignalK, Pypilot) shall be managed via systemd to ensure automatic "respawning" after a process crash.
  * Dependency Mapping: systemd configurations shall be mapped to ensure signalk.service is fully initialized and binding to websockets before pypilot.service attempts to connect. This prevents boot-time race conditions.

5. Sensor Reliability and Environmental Hardening

Environmental stressors such as RF noise and voltage mismatch will induce "phantom" sensor failures if not mitigated at the physical layer.

* IMU Voltage Conflict (ICM-20948): The ICM-20948 is a 1.8V silicon device. Over-driving its I2C bus with the Raspberry Pi's 3.3V logic without MOSFET-based level-shifting circuitry is a fatal design error. This mismatch causes latch-up and gradual thermal degradation, leading to sensor failure during high-stress sea states. Only IMUs with integrated 1.8V regulators and level-shifters are compliant.
* RF Interference Mitigation: SDR and GPS dongles are sensitive to the RPi's processor noise.
  * Protocol: Mandate USB extension cables for all RF dongles.
  * Filtering: Apply ferrite chokes to all USB extensions to lower the noise floor.
  * Target SNR: Architects shall verify a noise floor between -20dB and -30dB SNR for reliable data reception.
* Serial Port Management: To prevent port "pinching" (e.g., Pypilot seizing an NMEA2000 gateway intended for SignalK), architects shall use udev rules to create persistent aliases (e.g., /dev/ttyOP_gps). Command-line exclusion via ~/.pypilot/blacklist_serial_ports and explicit definition in ~/.pypilot/serial_ports is mandatory to ensure configuration persistence across reboots.

6. Standard Compliance Checklist

Systems are only deemed "Marine-Ready" upon completion of this audit:

* [ ] Power Integrity: Official 5.1V/3A supply or PoE+ HAT confirmed; Red LED verified continuous under load.
* [ ] Thermal/Isolation: IBT-2 heatsink verified non-conductive to PCB vias; airflow verified across PCB copper pour.
* [ ] Grounding Audit: Verified single-point ground; no high-current return paths present on signal wires.
* [ ] Logic Inversion: Software side B held at 100% duty cycle; continuous IS-pin current diagnostics verified.
* [ ] Service Logic: systemctl indicates SignalK and Pypilot services are active with dependency mapping.
* [ ] Security Audit: Password changed from 'changeme'; SignalK mDNS active; only authorized tokens approved.
* [ ] Voltage Matching: ICM-20948 level-shifting verified; no 3.3V logic directly on 1.8V pins.
* [ ] RF Health: USB extensions and ferrite chokes installed; AIS/GPS SNR verified < -20dB.
* [ ] Calibration Convergence: IMU accelerometer and compass alignment completed. Visual check: Red cone has "Snapped to Globe" in the calibration GUI, indicating Kalman filter convergence.


Based on the sources, level-shifting is primarily discussed in the context of connecting **1.8V sensors** (like the ICM-20948 IMU) to the **3.3V logic** of a Raspberry Pi. Connecting these directly is considered "out of spec" and can result in unreliable communication, detection errors, or permanent hardware damage.

The sources recommend the following level-shifting solutions:

### **1. Integrated Breakout Boards (Recommended)**
The most straightforward and highly recommended solution for most users is to use a sensor breakout board that includes **onboard 1.8V regulation and level-shifting circuitry**. These boards allow the sensor to communicate safely with 3.3V devices (like the Raspberry Pi) or 5V devices (like an Arduino Uno).

Specific recommended modules include:
*   **Adafruit TDK ICM-20948 Breakout:** This board is explicitly cited for including the necessary 1.8V regulator and shifting circuitry.
*   **Pimoroni ICM20948 9DoF Breakout:** This module is 3.3V and 5V compatible and features a pinout specifically designed to pop directly onto the first five pins of a Raspberry Pi's GPIO header.
*   **GY-ICM20948V2 Module:** Recommended as a module that adapts the I2C bus to the Pi's 3.3V voltage.

### **2. Discrete Component Solutions (For Bare Chips)**
If you are using a "bare" sensor chip without a dedicated breakout board, you must implement your own translation.
*   **MOSFETs and Resistors:** Experts suggest that level translation can be achieved simply using a few **MOSFETs and resistors** to bridge the 1.8V and 3.3V logic levels.

### **3. Considerations for Other Hardware**
While the 1.8V to 3.3V shift is critical for modern IMUs, other components mentioned in the sources handle voltage differences differently:
*   **Motor Drivers (BTS7960):** Some motor driver modules include a **74HC244 octal buffer/driver**. While its presence is described as a "mystery" in some contexts, the BTS7960 datasheet indicates its inputs are TTL/CMOS compatible and can work directly from either a 3.3V or 5V microcontroller.
*   **PyPilot / MacArthur HATs:** When using specialized HATs, it is important to verify if they provide level shifting or if they require a pre-shifted sensor module. Some users have reported detection issues when using certain HATs with bare IMU chips.

**Summary Recommendation:** To ensure long-term reliability and avoid "frying" your hardware, the sources strongly suggest using **pre-built breakout boards from reputable vendors (like Adafruit or Pimoroni)** that handle the 1.8V level shifting internally.

