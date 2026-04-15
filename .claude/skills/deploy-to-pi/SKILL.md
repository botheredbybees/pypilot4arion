---
name: deploy-to-pi
description: Deploy pypilot changes to the Pi 3B steering node and restart the autopilot service
disable-model-invocation: true
---

Remind the user to run the following steps to deploy changes to the steering node:

```
1. SSH to the Pi 3B:
   ssh pi@192.168.20.100

2. Pull latest changes:
   cd ~/pypilot4arion && git pull

3. Install updated Python package:
   sudo python3 setup.py install

4. Restart pypilot service:
   sudo systemctl restart pypilot

5. Watch logs to confirm clean startup:
   sudo journalctl -u pypilot -f
```

**If you changed arduino/motor/ firmware**, also flash the Arduino Nano:
```
   cd ~/pypilot4arion/arduino/motor
   make upload   # ensure DEVICE= is set to /dev/ttyUSB0 in Makefile
```

**Check pypilot is running correctly:**
- Web interface: http://192.168.20.100:8000
- Serial flags (look for SYNC, no INVALID or BAD_FUSES):
  python3 ~/pypilot4arion/arduino/motor/tests/nano_test.py
