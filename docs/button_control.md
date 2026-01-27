
# Button Control for Pypilot

This guide covers adding physical controls to your pypilot autopilot system on the TinyPilot Raspberry Pi.

## Control Options

1. **IR Remote Control** - Easiest, no GPIO wiring required
2. **Physical Pushbuttons** - Marine-grade buttons wired to GPIO
3. **Rotary Encoder** - For precise course adjustments

## Option 1: IR Remote Control (Recommended First)

Pypilot has built-in IR remote support. Use any IR remote (TV remote, dedicated remote).

### Hardware Required

- IR receiver module (TSOP38238, VS1838B, or similar 38kHz receiver)
- 3 wires (or use existing jumper wires)

### Wiring IR Receiver

| IR Receiver Pin | Pi Zero GPIO | Pin Number | Notes |
| :--- | :--- | :--- | :--- |
| VCC | 3.3V Power | Pin 1 or 17 | 3.3V only, not 5V |
| GND | Ground | Pin 6, 9, 14, etc. | Any ground pin |
| OUT (Data) | GPIO 18 | Pin 12 | Default LIRC GPIO |

**Alternative GPIO**: You can use GPIO 17, 22, 23, or 27, but GPIO 18 is default for LIRC.

### Software Installation

```bash
# Install LIRC (Linux Infrared Remote Control)
sudo apt install -y lirc

# Install Python LIRC bindings (optional)
sudo pip3 install python-lirc
```

### Configure LIRC

Enable LIRC device tree overlay:

```bash
sudo nano /boot/firmware/config.txt
# or on older systems: sudo nano /boot/config.txt
```

Add at the end:
```
# Enable IR receiver on GPIO 18
dtoverlay=gpio-ir,gpio_pin=18
```

Edit LIRC options:

```bash
sudo nano /etc/lirc/lirc_options.conf
```

Ensure these settings:
```
driver = default
device = /dev/lirc0
```

Reboot:
```bash
sudo reboot
```

### Test IR Receiver

```bash
# Test raw IR signals
mode2 -d /dev/lirc0

# Point your remote at the receiver and press buttons
# You should see pulse/space timings
# Press CTRL+C to stop
```

### Configure for Pypilot

Pypilot will automatically use IR remote when detected. Default button mappings work with most remotes. See pypilot documentation for custom button configuration.

## Option 2: Physical Pushbuttons via GPIO

For cockpit-mounted waterproof buttons using modern **gpiozero** library.

**Important**: `wiringpi` is deprecated and no longer available in Raspberry Pi OS repositories. Use `gpiozero` instead - it's actively maintained and much easier to use.

### Hardware Required

- 5x momentary pushbuttons (marine-grade, waterproof recommended)
- Wire (marine-grade tinned copper, 18-22 AWG)
- Optional: Project box, panel-mount buttons

### Recommended Buttons

- **Marinco/AFI**: Momentary pushbuttons, waterproof IP66+
- **Blue Sea Systems**: Push-button switches
- **Generic**: Stainless steel momentary switches (16mm diameter common)

### Wiring Physical Buttons

**Simple Connection** (no external resistors needed - gpiozero uses internal pull-ups):

```
Button Terminal 1 → GPIO Pin
Button Terminal 2 → GND Pin

All buttons can share a common GND
```

**Suggested GPIO Pin Assignments**:

| Function | GPIO | Physical Pin | Button Wire | GND Pin |
| :--- | :--- | :--- | :--- | :--- |
| Auto/Standby Toggle | GPIO 17 | Pin 11 | Red | Pin 9 |
| Port (Turn Left) | GPIO 22 | Pin 15 | Green | Pin 9 |
| Starboard (Turn Right) | GPIO 23 | Pin 16 | Blue | Pin 9 |
| Course +1° | GPIO 24 | Pin 18 | Yellow | Pin 20 |
| Course -1° | GPIO 25 | Pin 22 | White | Pin 20 |

### Software Installation

```bash
# Install gpiozero (modern GPIO library - replaces wiringpi)
sudo apt install -y python3-gpiozero

# Install pypilot client library (if not already installed)
pip3 install pypilot
```

### Create Button Control Script

Create `/home/bbb/pypilot_buttons.py`:

```python
#!/usr/bin/env python3
"""
Pypilot Physical Button Controller
Connects GPIO buttons to pypilot autopilot functions
"""

from gpiozero import Button
from signal import pause
import socket
import json

# Pypilot connection settings
PYPILOT_HOST = 'localhost'
PYPILOT_PORT = 20220

# GPIO pin assignments (BCM numbering)
PIN_AUTO = 17       # Auto/Standby toggle
PIN_PORT = 22       # Turn port (left)
PIN_STARBOARD = 23  # Turn starboard (right)
PIN_PLUS_1 = 24     # Course +1 degree
PIN_MINUS_1 = 25    # Course -1 degree

# Debounce time (seconds)
DEBOUNCE = 0.1

class PypilotButtonController:
    def __init__(self):
        # Initialize buttons with internal pull-up resistors
        self.btn_auto = Button(PIN_AUTO, bounce_time=DEBOUNCE)
        self.btn_port = Button(PIN_PORT, bounce_time=DEBOUNCE)
        self.btn_starboard = Button(PIN_STARBOARD, bounce_time=DEBOUNCE)
        self.btn_plus_1 = Button(PIN_PLUS_1, bounce_time=DEBOUNCE)
        self.btn_minus_1 = Button(PIN_MINUS_1, bounce_time=DEBOUNCE)
        
        # Assign button handlers
        self.btn_auto.when_pressed = self.toggle_auto
        self.btn_port.when_pressed = self.turn_port
        self.btn_starboard.when_pressed = self.turn_starboard
        self.btn_plus_1.when_pressed = self.course_plus_1
        self.btn_minus_1.when_pressed = self.course_minus_1
        
        print("Pypilot button controller initialized")
        print(f"  Auto/Standby: GPIO {PIN_AUTO}")
        print(f"  Port:         GPIO {PIN_PORT}")
        print(f"  Starboard:    GPIO {PIN_STARBOARD}")
        print(f"  Course +1:    GPIO {PIN_PLUS_1}")
        print(f"  Course -1:    GPIO {PIN_MINUS_1}")
    
    def send_command(self, key, value):
        """Send command to pypilot via TCP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((PYPILOT_HOST, PYPILOT_PORT))
            
            message = json.dumps({key: value}) + '\n'
            sock.send(message.encode())
            sock.close()
            
            print(f"Sent: {key} = {value}")
            return True
            
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def get_value(self, key):
        """Get value from pypilot"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((PYPILOT_HOST, PYPILOT_PORT))
            
            # Request value
            request = json.dumps({'method': 'get', 'key': key}) + '\n'
            sock.send(request.encode())
            
            # Read response
            response = sock.recv(1024).decode()
            sock.close()
            
            data = json.loads(response)
            return data.get(key)
            
        except Exception as e:
            print(f"Error getting value: {e}")
            return None
    
    def toggle_auto(self):
        """Toggle autopilot engaged/standby"""
        print("Button: Auto/Standby toggle")
        enabled = self.get_value('ap.enabled')
        self.send_command('ap.enabled', not enabled if enabled is not None else True)
    
    def turn_port(self):
        """Quick turn to port"""
        print("Button: Port tack")
        self.send_command('servo.command', -1)
    
    def turn_starboard(self):
        """Quick turn to starboard"""
        print("Button: Starboard tack")
        self.send_command('servo.command', 1)
    
    def course_plus_1(self):
        """Increase course heading by 1 degree"""
        print("Button: Course +1°")
        heading = self.get_value('ap.heading_command')
        if heading is not None:
            new_heading = (heading + 1) % 360
            self.send_command('ap.heading_command', new_heading)
    
    def course_minus_1(self):
        """Decrease course heading by 1 degree"""
        print("Button: Course -1°")
        heading = self.get_value('ap.heading_command')
        if heading is not None:
            new_heading = (heading - 1) % 360
            self.send_command('ap.heading_command', new_heading)
    
    def run(self):
        """Main loop"""
        print("Button controller running. Press CTRL+C to exit.")
        try:
            pause()  # Wait for button events
        except KeyboardInterrupt:
            print("\nShutting down button controller")

if __name__ == '__main__':
    controller = PypilotButtonController()
    controller.run()
```

Make executable:
```bash
chmod +x ~/pypilot_buttons.py
```

### Test Button Script

```bash
# Run manually to test
python3 ~/pypilot_buttons.py

# Press buttons and watch for output
# CTRL+C to exit
```

### Create Systemd Service

```bash
sudo nano /etc/systemd/system/pypilot_buttons.service
```

Content:
```ini
[Unit]
Description=Pypilot Button Controller
After=pypilot.service network.target
Requires=pypilot.service

[Service]
Type=simple
User=bbb
WorkingDirectory=/home/bbb
ExecStart=/usr/bin/python3 /home/bbb/pypilot_buttons.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pypilot_buttons.service
sudo systemctl start pypilot_buttons.service

# Check status
sudo systemctl status pypilot_buttons.service

# View logs
sudo journalctl -u pypilot_buttons.service -f
```

## Option 3: Rotary Encoder

For precise course adjustments using a rotary knob.

### Hardware

- Rotary encoder with push button (e.g., KY-040)
- 3.3V compatible

### Wiring

| Encoder Pin | Pi GPIO | Pin Number |
| :--- | :--- | :--- |
| VCC | 3.3V | Pin 1 |
| GND | Ground | Pin 6 |
| CLK | GPIO 5 | Pin 29 |
| DT | GPIO 6 | Pin 31 |
| SW (button) | GPIO 13 | Pin 33 |

### Script Addition

Add to button controller script:

```python
from gpiozero import RotaryEncoder

# In __init__:
self.encoder = RotaryEncoder(5, 6, bounce_time=0.002)
self.encoder_btn = Button(13, bounce_time=0.1)

self.encoder.when_rotated_clockwise = self.course_plus_1
self.encoder.when_rotated_counter_clockwise = self.course_minus_1
self.encoder_btn.when_pressed = self.toggle_auto
```

## Mounting Considerations

### Waterproofing

- Use marine-grade IP66 or IP67 rated switches
- Seal all penetrations with marine sealant
- Mount in protected location (under dodger, in cockpit locker lid)

### Button Layout

**Suggested cockpit layout**:

```
     [  -1°  ]
[ PORT ]  [ AUTO ]  [ STBD ]
     [  +1°  ]
```

Or vertical strip:
```
[ AUTO ]
[  +1° ]
[ PORT ] [ STBD ]
[  -1° ]
```

### Cable Routing

- Use marine-grade tinned copper wire
- Route cables away from high-current wires (motor, pump)
- Use cable glands for watertight entry to enclosure
- Label all wires at both ends
- Allow service loop inside enclosure

## Testing

### Test Individual Buttons

```python
# Quick test script
from gpiozero import Button

btn = Button(17)
btn.when_pressed = lambda: print("Auto button pressed!")

from signal import pause
pause()
```

### Test with Multimeter

1. Set multimeter to continuity mode
2. Connect one probe to GPIO pin
3. Connect other probe to GND
4. Press button - should beep/show continuity

## Troubleshooting

### Buttons Not Responding

```bash
# Check GPIO status
python3 -c "from gpiozero import Button; b = Button(17); print('Button state:', b.value)"

# Check button service logs
sudo journalctl -u pypilot_buttons.service -n 50
```

### Multiple Button Presses Detected

Increase debounce time in script:
```python
btn = Button(17, bounce_time=0.2)  # Increase to 200ms
```

### Buttons Triggering Randomly

- Check wiring for shorts
- Ensure proper ground connections
- Add capacitor (0.1µF) across button terminals if electrical noise present
- Keep button wires away from motor/pump power cables

### Cannot Connect to Pypilot

```bash
# Verify pypilot is running
sudo systemctl status pypilot.service

# Test pypilot port
telnet localhost 20220
```

## Advanced: Button LED Indicators

Add LEDs to show autopilot status:

### Wiring LED

```
GPIO Pin → 220Ω Resistor → LED Anode (+)
LED Cathode (-) → GND
```

### Code Addition

```python
from gpiozero import LED

# In __init__:
self.led_auto = LED(26)  # GPIO 26 for Auto engaged LED

def update_status_leds(self):
    """Update LED states based on pypilot status"""
    enabled = self.get_value('ap.enabled')
    if enabled:
        self.led_auto.on()
    else:
        self.led_auto.off()
```

## Why gpiozero Instead of wiringpi

- **wiringpi is deprecated**: Author stopped maintaining it in 2019, removed from Raspberry Pi OS
- **gpiozero is modern**: Actively maintained, Python 3 native, cleaner API
- **Built-in debouncing**: No external libraries needed
- **Simpler code**: Fewer lines, easier to understand
- **Better documentation**: Comprehensive examples and tutorials
- **Works with all Pi models**: Including Pi Zero, Pi 4, Pi 5

## References

- [gpiozero Documentation](https://gpiozero.readthedocs.io/)
- [LIRC Project](https://www.lirc.org/)
- [Pypilot GitHub](https://github.com/pypilot/pypilot)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)

## Related Documentation

- [TinyPilot Setup](./tinypilot_setup.md) - Main pypilot installation
- [Hardware Review](./hardware_review.md) - Complete hardware overview
- [Testing and Tuning](./testing_and_tuning.md) - Autopilot configuration


