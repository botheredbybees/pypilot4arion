Write an updated openplotter_setup.md with this additional information

# docs/openplotter_setup.md

## OpenPlotter pypilot Setup for Arion (Tested 2026-01-27)

**Hardware**: Raspberry Pi 3B + 16GB SD card + Arduino motor controller + IMU

## 1. Flash OpenPlotter Starting Image

```
Raspberry Pi Imager → OpenPlotter Starting (4.x.x)
Settings (gear icon):
├── Hostname: tinypilot
├── Username: bbb  
├── WiFi: flow SSID/password
└── Enable SSH
```

**Boot Pi 3B** → SSH: `ssh bbb@192.168.1.183`

## 2. Install pypilot App

```
Desktop → OpenPlotter → Settings → Apps
├── Refresh app list
└── Install "pypilot" ✓
```

## 3. Enable Interfaces (Required)

```
OpenPlotter Settings → Apps:
☑️ GPIO     ← Arduino pins
☑️ Serial   ← USB Arduino  
☑️ I2C      ← IMU sensors
```
```
**Reboot**
sudo reboot
```

## 4. Start pypilot Services

```bash
# Check services created
systemctl list-units | grep pypilot

# Enable all services
sudo systemctl enable --now pypilot pypilot_web pypilot_boatimu

# Status
sudo systemctl status pypilot pypilot_web pypilot_boatimu --no-pager
```

## 5. Verify IMU (Connect Before boatimu)

**I2C pins (Power OFF first)**:
```
Pin 1 (3.3V) → IMU VCC
Pin 3 (SDA)  → IMU SDA  
Pin 5 (SCL)  → IMU SCL
Pin 6 (GND)  → IMU GND
```

**Test detection**:
```bash
sudo i2cdetect -y 1
# Should show 0x68 (MPU9250) or your IMU address
```

**Logs**:
```bash
journalctl -u pypilot_boatimu -f
# "boatimu: detected MPU9250" = success
```

## 6. Web Interface

```
http://192.168.1.183
# or http://tinypilot.local
```

## 7. Arduino Motor Controller Setup

```
1. Connect Arduino to USB port
2. OpenPlotter → Serial → USB devices → Arduino → alias "pypilot_arduino"

3. pypilot Web → Configuration → Serial
   ├── Add: /dev/ttyUSB0 (pypilot_arduino)
   └── Test connection
```

## 8. Hydraulic Pump Configuration (4-Solenoid H-Bridge)

```
pypilot Web → Configuration → Servo:
├── Driver: arduino  
├── servo.mode: solenoid
├── Pins:
│   ├── Sol1-Port: D2
│   ├── Sol2-Port: D3  
│   ├── Sol3-Star: D4
│   └── Sol4-Star: D5
├── servo.max_current: 20
└── Test rudder movement
```

## Troubleshooting

```
No pypilot service:
$ sudo apt install openplotter-pypilot
$ sudo openplotter-pypilotPostInstall

No IMU:
$ sudo systemctl stop pypilot_boatimu
$ sudo systemctl start pypilot pypilot_web  # Run without IMU

Web not loading:
$ sudo systemctl status pypilot_web
$ curl -I http://localhost:8080
```

## Expected Status (All Green)

```
● pypilot.service           active (running)
● pypilot_web.service       active (running)  
● pypilot_boatimu.service   active (running)
```

```
Web UI shows: IMU data + servo controls + calibration ready
```

***
**Tested: Raspberry Pi 3B, OpenPlotter Starting 4.x.x, 2026-01-27**  
**Next: Arduino solenoid H-bridge wiring + calibration** [1][2]

***

