"""
PreToolUse hook: warn when Claude edits upstream pypilot source files.
Claude Code pipes tool input as JSON to stdin.
"""
import sys
import json
import re

data = json.load(sys.stdin)
file_path = data.get("tool_input", {}).get("file_path", "").replace("\\", "/")

if re.search(r"pypilot/(autopilot|boatimu|sensors|server|client|nmea|signalk)\.py$", file_path):
    print(json.dumps({
        "systemMessage": (
            "WARNING: This is upstream pypilot code. "
            "Changes here will conflict on next upstream merge. "
            "Confirm this is intentional for Arion."
        )
    }))
