# Handoff

## State
Claude Code automations fully implemented: `.claude/settings.json` (hooks), `.claude/hooks/check_upstream_edit.py`, `.claude/hooks/check_arduino_edit.py`, `.claude/skills/deploy-to-pi/SKILL.md`, `.claude/agents/marine-safety-reviewer.md`, `.mcp.json` (context7 + fetch via `cmd /c npx`). `readme_claude_code.md` written in project root. Nothing committed yet.

## Next
1. Commit all new files: `.claude/`, `.mcp.json`, `readme_claude_code.md`, `docs/MPPT40_User_Guide.pdf`
2. Verify hooks fire correctly — edit a file in `pypilot/` and `arduino/motor/` and confirm messages appear
3. Add power architecture notes to `docs/24v_solar_system.md` (pump on starter battery, Pi on MPPT load output, USB isolator needed)

## Context
Hooks previously failed with "Python was not found" because they used bash syntax in CMD. Fixed by rewriting as Python scripts called with `C:\Python311\python.exe` (full path). MCP servers use `cmd /c npx` wrapper — plain `npx` fails in Windows CMD context. Git-bash is at `C:\Users\peter_sha\AppData\Local\Programs\Git\git-bash.exe`.
