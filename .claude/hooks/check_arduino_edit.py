"""
PostToolUse hook: remind user to flash Arduino Nano after editing motor firmware.
Claude Code pipes tool input as JSON to stdin.
"""
import sys
import json
import re

data = json.load(sys.stdin)
file_path = data.get("tool_input", {}).get("file_path", "").replace("\\", "/")

if re.search(r"arduino/motor/.*\.(ino|h)$", file_path):
    print(json.dumps({
        "systemMessage": (
            "ACTION REQUIRED: Arduino file changed. "
            "Flash to Nano before testing: "
            "use Arduino IDE (Board: Nano, Processor: ATmega328P Old Bootloader) "
            "or run make upload on Pi 3B (192.168.20.100)."
        )
    }))
