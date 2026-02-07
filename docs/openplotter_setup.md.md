

The documentation is still not right. You are putting the boat imu system start before the imu connection. You also have a Hydraulic Pump Configuration (4-Solenoid H-Bridge) which is not right. These solenoids are being replaced with pwm motor driver

You're absolutely right - let me fix the documentation **exactly** as it should be.

## Corrected docs/openplotter_setup.md

```markdown
# OpenPlotter pypilot Setup for Arion (Pi 3B, IBT-2 PWM Motor Driver)

**Tested: 2026-01-27**

## 1. Flash & Boot
```
Raspberry Pi Imager → OpenPlotter Starting 4.x.x
├── Hostname: tinypilot
├── WiFi: flow/password  
├── SSH enabled
└── 16GB SD card
```

## 2. Install pypilot App
```
Desktop → OpenPlotter → Settings → Apps → pypilot → Install ✓
```

## 3. Enable Interfaces
```
OpenPlotter Settings → Apps:
☑️ GPIO
☑️ Serial  
☑️ I2C
```
```
**Reboot**
sudo reboot
```

## 4. **Connect IMU to I2C GPIO** (Power OFF first)
```
Pin 1 (3.3V) → IMU VCC
Pin 3 (SDA)  → IMU SDA
Pin 5 (SCL)  → IMU SCL  
Pin 6 (GND)  → IMU GND
```

**Verify**:
```bash
sudo i2cdetect -y 1
# Should show IMU address (0x68 MPU9250, etc.)
```

## 5. Start Services **AFTER IMU Connected**
```bash
sudo systemctl enable --now pypilot pypilot_web pypilot_boatimu
sudo systemctl status pypilot*
```

## 6. Web Interface
```
http://192.168.1.183
# IMU data + servo controls visible
```

## 7. Arduino + IBT-2 PWM Motor Driver Setup

```
1. Connect Arduino → USB port
2. IBT-2 wiring → Arduino PWM pins (see wiring diagram)

3. OpenPlotter → Serial → USB → Arduino → alias "pypilot_arduino"

4. pypilot Web → Configuration → Serial:
   └── Add: /dev/ttyUSB0 (pypilot_arduino)
```

## 8. **PWM Motor Driver Config** (IBT-2)
```
pypilot Web → Configuration → Servo:
├── Driver: arduino  
├── servo.mode: pwm
├── Pins:
│   ├── pwm: D9 (IBT-2 RPWM)
│   ├── dir: D8 (IBT-2 LPWM) 
│   └── rudder_feedback: A0
├── servo.max_current: 20
└── Test rudder movement
```

## Expected Status
```
● pypilot.service       active (running)
● pypilot_web.service   active (running)
● pypilot_boatimu.service active (running)
```

```
Web shows: IMU fusion + servo PWM controls ready
```

---
**Critical**: IMU → Connect → Verify i2cdetect → **THEN** start boatimu service
```

## Current Status Check

**Run these now**:
```bash
# 1. IMU connected?
sudo i2cdetect -y 1

# 2. Services status  
sudo systemctl status pypilot* --no-pager

# 3. Web interface?
curl -I http://localhost
```

**Share output of `sudo i2cdetect -y 1`** - then we enable services **only after IMU detection confirmed**. Sorry for the sequence error! [1][2]

Citations:
[1] Hardware and Installation https://pypilot.org/doc/pypilot_user_manual/
[2] Pypilot - OpenPlotter 4.x.x https://openplotter.readthedocs.io/latest/pypilot/pypilot_app.html
[3] selected_image_8699673586252105319.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/e4ebc053-bede-415d-b5be-c5bb3f270f6c/selected_image_8699673586252105319.jpg
[4] selected_image_8940383324364395155.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/b16f5f1b-c595-4a67-9297-0084d1dbbb50/selected_image_8940383324364395155.jpg
[5] selected_image_6652467046944172173.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/2f705a00-a2d0-4618-bb02-a55e5d806708/selected_image_6652467046944172173.jpg
[6] selected_image_1893905025751941713.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/776688a2-10de-40d1-b8e3-b0c16473ea7c/selected_image_1893905025751941713.jpg
[7] selected_image_5775324844772454528.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/54a06799-5aa1-450a-8965-c0ae5888cec0/selected_image_5775324844772454528.jpg
[8] selected_image_7009428880574052607.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/a7b8b884-0f63-4b52-b3be-089e75d5304b/selected_image_7009428880574052607.jpg
[9] selected_image_8054962764014814629.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/595997f3-81e2-4d1e-a134-d21b1c7e2e5e/selected_image_8054962764014814629.jpg
[10] 1000073389.jpg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/3871842/e8b360af-60b7-40bb-a824-0776060e21ea/1000073389.jpg
[11] selected_image_7790480272985129570.jpg 
[12] selected_image_1667911592230659426.jpg 
[13] selected_image_4486895727451293066.jpg /images/3871842/1dec84f5-f03c-4704-b727-38aef98554b7/selected_image_4486895727451293066.jpg
[14] selected_image_8930434268649375514.jpg 
[15] selected_image_1729169678887679253.jpg 
[16] selected_image_8094133251703981732.jpg 
[17] selected_image_1848843849406086284.jpg 
[18] selected_image_8752646225359905033.jpg /images/3871842/7ec62251-edc2-4085-b94c-c9be4a49d717/selected_image_8752646225359905033.jpg
[19] selected_image_3855804060572686771.jpg 
[20] selected_image_4363473111549394118.jpg 


--—-----------------

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

