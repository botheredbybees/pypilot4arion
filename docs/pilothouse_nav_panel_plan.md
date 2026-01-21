# pilothouse_nav_panel_plan.md

## Panel Overview
New **12V pilothouse navigation panel** (12mm marine plywood, **700mm W x 500mm H x 25mm D frame**) mounts flush/angled on console bulkhead, replacing Navman 5600. Houses iTechworld MPPT (solar monitoring), RPi4 Lysmarine (15" OpenCPN nav screen), TinyPilot Pi0, IBT-2 ctrl, Pixel2 hotspot. Local 12V bus fed from house (16mm²), 5V bucks for Pis/phone. Coordinates: **Top-left corner (0,0)** at upper-left mounting hole; X right, Y down. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/0c96d063-151f-4586-bb71-8744763bca3d/PXL_20260121_003049784.jpg)

## Pilothouse Panel Components (Upper Panel)
All positions from **top-left (0mm,0mm)**; clearances 20mm edges.

| Component | Description | Location (X,Y from top-left) | Mount/Dims | Connections | Power |
|-----------|-------------|------------------------------|------------|-------------|-------|
| **15" HDMI Nav Screen** | Main chartplotter (OpenCPN on RPi4 Lysmarine; replaces Navman 5600). Full HD, marine glare-proof.  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/0c96d063-151f-4586-bb71-8744763bca3d/PXL_20260121_003049784.jpg) | (50mm, 20mm); spans 600x250mm | VESA 75mm holes; 375x230mm vis.  [beetronics](https://www.beetronics.com/c-marine/15-inch-1/9-36volt) | HDMI from RPi4; 12V DC jack | Bus A 10A blade (screen) |
| **TinyPilot Pi Zero LCD** | Autopilot status/dashboard (pypilot web; heading/rudder/PID).  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/3871842/99145bed-8e8b-44de-877c-749c1ff69482/tinypilot_setup.md) | (650mm, 20mm); 80x60mm | Snap-fit case; 79x38x15mm  [adafruit](https://www.adafruit.com/product/3446) | WiFi to hotspot; UART IMU | 5V buck #1 USB (500mA) |
| **iTechworld 40A MPPT** | Solar regulator LCD/app monitor (PV/batt amps/kWh). Batt out to bus.  [itechworld.com](https://itechworld.com.au/products/itechworld-40a-12-24v-mppt-solar-charge-controller) | (20mm, 150mm); 215x145x75mm | 4x screw holes | PV MC4 top; batt+ bot (40A MIDI) | None (self-powered) |
| **RPi4 Lysmarine** | Nav computer (OpenCPN, SignalK, wind RTL-SDR). Behind screen.  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/3871842/0dc8821f-8747-4650-a189-453c42afa719/lysmarine_integration.md) | (50mm, 280mm); 86x57mm board | Argon ONE case ~100x70x30mm  [deepseadev](https://www.deepseadev.com/en/blog/raspberry-pi-4-specs/) | HDMI to screen; Ethernet opt. | 5V buck #2 USB-C (3A) |
| **IBT-2 Motor Ctrl** | H-bridge PWM drive for hydraulic pump (43A BTS7960).  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/3871842/99145bed-8e8b-44de-877c-749c1ff69482/tinypilot_setup.md) | (300mm, 320mm); 50x50x43mm  [majju](https://www.majju.pk/product/bts7960-ibt2-bts7960-43a-high-power-motor-driver-module/) | 4-screw PCB | UART/PWM from TinyPi; 12V/helm pump | Bus B 20A direct |
| **Pixel2 Hotspot** | YachtArion WiFi AP (192.168.43.1; Pi network). USB mount.  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/3871842/fdcc6bee-6c7c-4636-a02f-df5ece50456c/wireless_hotspot.md) | (500mm, 380mm); phone dims ~150x70x10mm | Velcro/USB cradle | USB-C charge; SIM opt. | 5V buck #2 USB (2A) |
| **12V Bus A Fuseholder** | 12-slot blade for nav/Pi (20A main).  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/0abe54af-a778-4174-99f7-a951f3698c83/PXL_20260121_003604448.jpg) | (20mm, 380mm); 120x80mm | Screw mount | Feed from house 16mm² | House Bus A |
| **5V Buck Converters** | #1 TinyPi (3A); #2 RPi4/Pixel (3A). | (550mm, 150mm); 60x40x25mm ea. | Screw/velcro | 12V Bus A in; USB out | Bus A 15A blade |
| **USB/DC Jacks** | Spare 5V/12V for future. | (620mm, 420mm); 4x ports | Panel cutouts | Bus/local | - |

**Total power**: ~30W (Bus A 40A circuit safe); glands bottom for cables.


## Wiring Loom Below Panel (Full Engine Room Board Replacement)
**Lower loom** (12mm ply, **600mm W x 400mm H**) mounts vertically beside batteries/hydraulic filler (retain ~200x150mm space right). Replaces mess; centralized 12V DC distro. Positions **top-left (0mm,0mm)** upper-left bolt hole; X right, Y down. Measurements from photos (~450x350mm old board).[file:104-110]

| Component | Description | Location (X,Y from top-left) | Mount/Dims | Connections | Power/Fuse |
|-----------|-------------|------------------------------|------------|-------------|------------|
|  **House Main 100A Breaker**| Primary house isolator (resets post-trip). | (20mm, 20mm)   | Panel/din screw           | Batt+/VSR → loom buses | Master on/off starpoweradvancesolartechnology​ |
| **Windlass 100A Breaker** | Anchor winch momentary.          | (20mm, 120mm)  | Near Bus B        | Bus B stud | Overcurrent theboatwarehouse​                  |
| **Wind/Bilge 100A Breaker**  | Rutland/PL20 + pumps group.                | (20mm, 220mm)  | Near PL20                 | Wind reg → PL20 batt+  | Backup charging whitworths​                    |
| **Red Pos Bus (4-post)** | HouseB heavy studs (50-100A MIDI/ANL).  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/678e9b27-e0b3-4cbc-850a-54efa7c3d215/PXL_20260121_003540878.jpg) | (150mm, 20mm); 100x50mm | Screw/insul. block | MPPT batt+, VSR house, heavy feeds | Studs torque 5Nm |
| **Black Neg Bus (strips)** | Common ground returns/engine bond.  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/f054cb4b-1ad6-4883-b11d-82ee3ce44d25/PXL_20260121_003608419.jpg) | (300mm, 20mm); 150x40mm multi-term | Screw block | All negs, engine block 25mm² | - |
| **Bus A 12-blade Fuseholder #1** | Low-current (lights/nav/pumps 10-25A).  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/0abe54af-a778-4174-99f7-a951f3698c83/PXL_20260121_003604448.jpg) | (20mm, 100mm); 120x80mm | 4-screw | 16mm² from main brk; branches 4-6mm² | 30A main blade |
| **Bus B 12-blade #2** | High-current spares/expansion.  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/b3cde1b6-7d3b-4553-bae6-e1a5343c3c71/PXL_20260121_003158513.jpg) | (170mm, 100mm); 120x80mm | 4-screw | Main brk; troll/toilet 6-10mm² | 60A main |
| **Smart VSR 140A Isolator** | Batt link (start↔house; LED status).  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/4d72658e-46c9-484f-a07d-4a11a147daa3/PXL_20260119_235127785.jpg) | (450mm, 20mm); 120x80mm | Bulkhead screw | Start+ 16mm² ea. end (100A fuses) | Self-powered |
| **40A MIDI Fuse Holder** | Solar MPPT batt+ protect (blue fuse).  [caravanrvcamping.com](https://www.caravanrvcamping.com.au/product/blue-sea-60a-midi-ami-fuse) | (20mm, 200mm); 60x40mm holder | Din/screw | iTech MPPT batt+ → 8G red | 40A MIDI insert |
| **Alpha Pro Regulator** | Yanmar alternator smart reg (start batt). Retain. | (200mm, 200mm); ~150x100mm | Existing bracket | Alt B+/sense; start batt | Engine 12V |
| **Bilge Pump Solenoid #1** | Port/auto bilge (float direct). | (400mm, 200mm); relay 50x50mm  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/feeddbf3-1641-431d-a4f5-e0c9a150c82f/PXL_20260121_003217375.jpg) | Din rail | Bus B 15A; pump 4mm² | 15A blade |
| **Bilge Pump Solenoid #2** | Stbd/shower (manual override). | (470mm, 200mm); relay 50x50mm | Din rail | Bus B 15A; pump | 15A blade |
| **60A MIDI Heavy Fuse** | VSR/inverter spares (yellow). | (20mm, 280mm); 4x holders 100x40mm | Block | Spares rack | 40/50/60A inserts |
| **Shore Power RCD** | AC inlet retain (C20 breakers).  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/e59dea78-ab2b-4db4-8bbe-071e302711fc/PXL_20260121_003334533.jpg) | (450mm, 100mm); 200x150mm | Existing | Shore cord; AC panel | AC 16A |
| **Hydraulic Filler Gauge** | Reservoir level retain. | (500mm, 20mm); ~100x100mm | Existing pipe | Visual only | None |

**Cable glands**: Bottom row (10x PG9 for 8G/16mm²); total ~40 terminations.

## Installation Sequence
1. **Ply cut**: 600x400mm; drill per table (label holes).
2. **Mount static**: Buses, breakers, PL20/Alpha (epoxy/screw).
3. **Wire**: Torque lugs; test shorts w/ multimeter.
4. **Upper panel feed**: 16mm² from Bus A → pilothouse conduit.
5. **Test**: 12V on, check no smoke; app monitor MPPT/VSR.

## Technical Notes
MIDI fuse sizing: \( I_{\text{fuse}} = 1.25 \times I_{\text{max}} \); 40A for 32A solar peak. [outbackmarine.com](https://www.outbackmarine.com.au/victron-midi-fuse-60a-58v-for-48v-products-1-pc~48556)
Loom heat: Buses rated 200A; <50°C rise at 100A continuous.

## Next Maintenance Steps
- [ ] 600x400mm ply + glands (~AU$50).
- [ ] MIDI fuses 40/50/60A pack.
- [ ] Dry-wire/test before boat swap.