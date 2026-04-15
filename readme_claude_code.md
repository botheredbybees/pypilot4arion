# Claude Code Setup for pypilot4arion

This document describes the Claude Code automations configured for this repository and how to use them.

---

## What Was Added

| Type | Name | File |
|------|------|------|
| Hook | Upstream file warning | `.claude/settings.json` |
| Hook | Arduino flash reminder | `.claude/settings.json` |
| Skill | `deploy-to-pi` | `.claude/skills/deploy-to-pi/SKILL.md` |
| Agent | `marine-safety-reviewer` | `.claude/agents/marine-safety-reviewer.md` |
| MCP server | `context7` | `.mcp.json` |
| MCP server | `fetch` | `.mcp.json` |

---

## Hooks (`.claude/settings.json` + `.claude/hooks/`)

Hooks run automatically when Claude uses certain tools. No manual invocation needed.

The hook logic lives in Python scripts under `.claude/hooks/` and is called with the full Python path (`C:\Python311\python.exe`). This avoids the bash syntax that fails in Windows CMD. Claude Code pipes tool input as JSON to each script's stdin; the script prints a JSON `systemMessage` if the condition matches, or exits silently.

### 1. Upstream file warning (PreToolUse)

**Script:** `.claude/hooks/check_upstream_edit.py`

**Trigger:** Claude attempts to edit any of these files:
- `pypilot/autopilot.py`
- `pypilot/boatimu.py`
- `pypilot/sensors.py`
- `pypilot/server.py`
- `pypilot/client.py`
- `pypilot/nmea.py`
- `pypilot/signalk.py`

**What it does:** Injects a warning message into the conversation:
```
WARNING: This is upstream pypilot code. Changes here will conflict on
next upstream merge. Confirm this is intentional for Arion.
```

**Why:** These files are inherited from the upstream pypilot project. Editing them risks painful merge conflicts if you pull upstream changes. Arion-specific behaviour should go in `servo.py`, `motor.ino`, or new files.

---

### 2. Arduino flash reminder (PostToolUse)

**Script:** `.claude/hooks/check_arduino_edit.py`

**Trigger:** Claude writes or edits any file matching `arduino/motor/**/*.ino` or `arduino/motor/**/*.h`.

**What it does:** Injects an action-required message:
```
ACTION REQUIRED: Arduino file changed. Flash to Nano before testing.
Use Arduino IDE (Board: Nano, Processor: ATmega328P Old Bootloader)
or run make upload on Pi 3B (192.168.20.100).
```

**Why:** Changes to `motor.ino` or `config.h` are not live until flashed. The hook prevents the easy mistake of testing against stale firmware.

---

## Skill: `deploy-to-pi`

**Type:** User-invocable (does not run automatically — Claude will not invoke this on your behalf)

**Invocation:** Type `/deploy-to-pi` in the Claude Code prompt.

**What it does:** Prints the full deploy procedure for pushing changes to the steering node Pi 3B at `192.168.20.100`:

```
1. SSH to the Pi 3B:    ssh pi@192.168.20.100
2. Pull latest:         cd ~/pypilot4arion && git pull
3. Install package:     sudo python3 setup.py install
4. Restart service:     sudo systemctl restart pypilot
5. Watch logs:          sudo journalctl -u pypilot -f
```

If Arduino firmware was also changed, it adds:
```
cd ~/pypilot4arion/arduino/motor
make upload    # DEVICE=/dev/ttyUSB0 must be set in Makefile
```

And verification steps:
- Web interface: `http://192.168.20.100:8000`
- Serial flags: `python3 ~/pypilot4arion/arduino/motor/tests/nano_test.py`
  (look for SYNC; no INVALID or BAD_FUSES)

**Note:** This skill is intentionally non-interactive (`disable-model-invocation: true`). It outputs instructions for you to run — it does not SSH to the Pi itself.

---

## Agent: `marine-safety-reviewer`

**Type:** Claude-invocable subagent. Claude will use this automatically when you ask it to review safety-critical autopilot code.

You can also invoke it explicitly:

```
Review the changes to servo.py for safety issues.
```

**What it focuses on (exclusively):**

1. **Fault handling paths** — current, temperature, voltage faults. Are `OVERCURRENT_FAULT`, `OVERTEMP_FAULT`, `BADVOLTAGE_FAULT`, `INVALID` still reachable?
2. **Watchdog and timeout logic** — Arduino watchdog stroking; the 4-second serial timeout in `servo.py`; would the servo stay engaged after comms loss?
3. **Unintended rudder movement** — motor commands when `ap.enabled` is False; slew rate limits (`max_slew_speed`, `max_slew_slow`); I-gain integral (`heading_error_int`) bounded by `minmax()`?
4. **Safety limits** — `max_current` (default 1500 = 15A), `max_controller_temp`, `max_motor_temp`; IBT-2 H-bridge enable/disable logic.

**It will NOT flag:** style issues, variable naming, performance, or anything that cannot plausibly cause unintended physical movement or failure to disengage.

**Files it applies to:** `pypilot/servo.py`, `pypilot/autopilot.py`, `arduino/motor/motor.ino`, `arduino/motor/config.h`

**For each issue found it will state:**
- What the failure mode is
- Under what conditions it triggers
- The specific line or logic path at risk

---

## MCP Servers (`.mcp.json`)

MCP (Model Context Protocol) servers extend Claude with access to external tools and live data. Two are configured for this project.

### Why `.mcp.json` (not `settings.json`)

`.mcp.json` in the project root is the correct mechanism for project-scoped MCP servers — checked into the repo so any machine opening this project gets the same servers automatically. The `mcpServers` key is not valid in `settings.json`.

To add further MCP servers via the CLI, run from git-bash (`C:\Users\peter_sha\AppData\Local\Programs\Git\git-bash.exe`):
```bash
claude mcp add <name> -- npx -y <package>
```
Note: `claude mcp add` must be run from git-bash on Windows, not PowerShell or CMD.

**Prerequisite:** Node.js must be installed (servers run via `cmd /c npx`). Verify with:
```
node --version
```

### 1. context7

Provides live, version-specific documentation for any library Claude is working with. When Claude needs to look up how a pypilot API works, or check the Python `asyncio` docs, it can fetch the actual current docs rather than relying on training-data knowledge.

**Configuration (Windows — uses `cmd /c` to resolve `npx`):**
```json
{
  "command": "cmd",
  "args": ["/c", "npx", "-y", "@upstash/context7-mcp@latest"]
}
```

**How to use:** Just ask Claude questions about libraries and it will use context7 automatically. You can also be explicit:
```
Using context7, show me the current asyncio.Protocol docs.
```

### 2. fetch

Lets Claude fetch arbitrary URLs — useful for reading datasheets, checking the pypilot upstream GitHub, or pulling documentation from a URL you provide.

**Configuration (Windows):**
```json
{
  "command": "cmd",
  "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-fetch"]
}
```

**How to use:**
```
Fetch https://github.com/pypilot/pypilot and summarise recent changes to servo.py.
```

---

## Verifying Everything Works

After opening this project in Claude Code, check:

**Hooks active:**
- Edit `pypilot/autopilot.py` — you should see the upstream warning before the edit proceeds.
- (The Arduino hook fires after edits to `.ino` / `.h` files in `arduino/motor/`.)

**Skill available:**
- Type `/deploy-to-pi` — you should get the deploy instructions printed.

**MCP servers:**
- In Claude Code, run `/mcp` or ask: "What MCP servers are connected?" — both `context7` and `fetch` should appear.
- If they show as disconnected, ensure Node.js is installed and `npx` is on your PATH.

---

## File Locations

```
pypilot4arion/
├── .mcp.json                              ← MCP server configuration (project-scoped)
├── readme_claude_code.md                  ← This file
└── .claude/
    ├── settings.json                      ← Hook configuration (calls Python scripts)
    ├── hooks/
    │   ├── check_upstream_edit.py         ← PreToolUse: upstream file warning
    │   └── check_arduino_edit.py          ← PostToolUse: Arduino flash reminder
    ├── agents/
    │   └── marine-safety-reviewer.md      ← Safety review subagent
    └── skills/
        └── deploy-to-pi/
            └── SKILL.md                   ← /deploy-to-pi skill
```

---

## Modifying These Automations

**To add files to the upstream warning hook:**
Edit the regex in `.claude/hooks/check_upstream_edit.py`, the `re.search(...)` pattern.

**To add safety checks to the agent:**
Edit `.claude/agents/marine-safety-reviewer.md` — add bullet points under the relevant section.

**To add an MCP server:**
Add an entry to `.mcp.json` following the same `command`/`args` pattern.

**To add more skills:**
Create `.claude/skills/<name>/SKILL.md` following the format in `deploy-to-pi/SKILL.md`.
