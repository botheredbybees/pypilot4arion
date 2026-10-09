#!/usr/bin/env python3
"""Snapshot SY Arion's live configuration into config/ (secrets removed).

Collects, over SSH and the Grafana API:
  hub       Signal K settings + plugin configs + Node-RED flows, Grafana/Influx/Mosquitto config,
            gpsd, NetworkManager, journald, logrotate, Arion systemd units/scripts, OpenCPN config
  steering  pypilot config (incl. IMU calibration), gpsd, NetworkManager, systemd units, boot config
  wind      rtl_433 service, boot config, fstab, overlayroot config
  grafana   dashboards, datasources, folders

Never collected: Signal K security.json (only a device/permission summary), Node-RED flows_cred.json,
~/.pypilot/signalk-token, NetworkManager/wpa_supplicant profiles (only SSID/mode summaries), SSH keys.
Secret-looking values are redacted and the finished tree is scanned for the real passwords in .env;
the script exits non-zero (and you must NOT commit) if anything leaks.

Usage:  python3 scripts/backup_config.py [--only hub,steering,wind,grafana]
Needs .env with ARION_PWD (Pi login/sudo) and GRAFANA_USER / GRAFANA_PWD. Hosts default to
192.168.20.100 (steering), .101 (hub), .102 (wind) unless ARION_*_PI_IP are set.
"""
import argparse
import base64
import io
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "config"
MAX_FILE = 2 * 1024 * 1024

SECRET_KEY = re.compile(
    r"(pass(word|wd|phrase)?|secret|token|jwt|psk|api[_-]?key|private[_-]?key|credential|^key$|_key$|^auth$)", re.I)
LINE_KV = re.compile(r"^(\s*[;#]?\s*)([\w.\-\[\]]+)(\s*[=:]\s*)(\S.*)$")
NOT_SECRET_WORDS = re.compile(r"compass|bypass|passthrough|passage|passive|passing", re.I)


PATH_LIKE = re.compile(r"^[A-Za-z0-9_]+(\.[A-Za-z0-9_*]+)+$")  # e.g. a Signal K path: environment.depth.belowSurface


def keep_value(key, value):
    """A bare 'key' field holding a dotted Signal K path is a name, not a secret."""
    return key.lower() == "key" and isinstance(value, str) and bool(PATH_LIKE.match(value))


def is_secret_key(key):
    """True for names like password/secret/token/psk/api_key; ignores false friends such as 'compass'."""
    return bool(SECRET_KEY.search(NOT_SECRET_WORDS.sub("", key)))


ACTIVE_ONLY = {"etc/grafana/grafana.ini", "etc/influxdb/influxdb.conf"}
POSITION_LINE = re.compile(r"^(\s*[\w.\-]*(latlon|latitude|longitude)[\w.\-]*\s*=\s*).*$", re.I)
# a quoted "lat, lon" string such as OpenCPN writes; plain numeric arrays (calibration data) do not match
COORD_PAIR = re.compile(r"[\"']\s*-?\d{1,2}\.\d{2,}\s*,\s*-?\d{1,3}\.\d{2,}\s*[\"']")
KEEP_WIFI = {"YachtArion", "lysmarine-hotspot", "lysmarine-hotspot 1"}


def load_env():
    text = (ROOT / ".env").read_text()
    text = re.sub(r"^([A-Z_]+_)\n(?=[A-Z_]+=)", r"\1", text, flags=re.M)  # tolerate a line split in two
    env = {}
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()
DEFAULT_IPS = {"steering": "192.168.20.100", "hub": "192.168.20.101", "wind": "192.168.20.102"}
ENV_IP_KEYS = {"steering": "ARION_PILOT_PI_IP", "hub": "ARION_HUB_PI_IP", "wind": "ARION_WX_PI_IP"}
_resolved = {}


def host(node):
    """Address that answers on SSH: the .env value first (may be a home-network address), then the boat defaults."""
    if node not in _resolved:
        cands = [ENV.get(ENV_IP_KEYS[node]), DEFAULT_IPS[node]]
        if node == "hub":
            cands.append(ENV.get("ARION_TAILSCALE_IP"))
        cands = [c for c in cands if c]
        for ip in cands:
            try:
                socket.create_connection((ip, 22), timeout=3).close()
                _resolved[node] = ip
                break
            except OSError:
                continue
        else:
            _resolved[node] = DEFAULT_IPS[node]
    return _resolved[node]


USER = ENV.get("ARION_USER", "bbb")
PWD = ENV.get("ARION_PWD", "")
SECRET_VALUES = [v for k, v in ENV.items()
                 if v and len(v) >= 6 and re.search(r"(pwd|pass|secret|token)", k, re.I)]

_askpass_dir = None


def _askpass_env():
    """SSH_ASKPASS helper that reads the password from the environment (never written to disk)."""
    global _askpass_dir
    if _askpass_dir is None:
        _askpass_dir = tempfile.mkdtemp(prefix="arion-askpass-")
        p = Path(_askpass_dir) / "askpass.sh"
        p.write_text('#!/bin/sh\nprintf "%s\\n" "$ARION_PWD"\n')
        p.chmod(0o700)
    env = dict(os.environ, ARION_PWD=PWD, SSH_ASKPASS=str(Path(_askpass_dir) / "askpass.sh"),
               SSH_ASKPASS_REQUIRE="force")
    return env


def ssh(node, cmd, sudo=True, timeout=240):
    """Run cmd on a node. wind uses password auth (its root is read-only, no persistent key)."""
    remote = "sudo -S -p '' sh -c %s" % shlex.quote(cmd) if sudo else "sh -c %s" % shlex.quote(cmd)
    args = ["ssh", "-o", "ConnectTimeout=20", "-o", "StrictHostKeyChecking=accept-new"]
    env = os.environ.copy()
    if node == "wind":
        args += ["-o", "PreferredAuthentications=password", "-o", "PubkeyAuthentication=no"]
        env = _askpass_env()
    else:
        args += ["-o", "BatchMode=yes"]
    args += ["%s@%s" % (USER, host(node)), remote]
    return subprocess.run(args, input=(PWD + "\n").encode(), capture_output=True, timeout=timeout, env=env)


def redact_json(o):
    if isinstance(o, dict):
        return {k: ("<redacted>" if is_secret_key(k) and isinstance(v, str) and v and not keep_value(k, v)
                    else redact_json(v))
                for k, v in o.items()}
    if isinstance(o, list):
        return [redact_json(x) for x in o]
    return o


def scrub_text(text):
    out = []
    for line in text.splitlines():
        pm = POSITION_LINE.match(line)
        if pm:
            line = pm.group(1) + "<redacted: position>"
        m = LINE_KV.match(line)
        if m and is_secret_key(m.group(2)) and m.group(4).strip() not in ("<redacted>", "<redacted: position>", ""):
            line = m.group(1) + m.group(2) + m.group(3) + "<redacted>"
        out.append(line)
    text = "\n".join(out) + "\n"
    for s in SECRET_VALUES:
        text = text.replace(s, "<redacted>")
    return text


def process(name, data):
    """Return sanitized text for a collected file, or None to skip it."""
    if len(data) > MAX_FILE or b"\x00" in data:
        return None
    text = data.decode("utf-8", errors="replace")
    if name.endswith(".json"):
        try:
            text = json.dumps(redact_json(json.loads(text)), indent=2) + "\n"
        except ValueError:
            pass
    if name in ACTIVE_ONLY:
        text = "\n".join(l for l in text.splitlines() if l.strip() and not l.lstrip().startswith((";", "#"))
                         or re.match(r"\s*\[", l)) + "\n"
    return scrub_text(text)


def write(node, rel, text):
    dest = OUT / node / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)


def collect(node, paths, excludes=("*/node_modules/*", "*.log")):
    ex = " ".join("--exclude=%s" % shlex.quote(e) for e in excludes)
    r = ssh(node, "cd / && tar -cf - --ignore-failed-read %s %s 2>/dev/null" % (ex, " ".join(paths)))
    if not r.stdout:
        print("  !! no data from %s: %s" % (node, r.stderr.decode(errors="replace")[:200]))
        return 0
    n = 0
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf:
        for m in tf:
            if not m.isreg() or ".." in m.name.split("/"):
                continue
            name = m.name.lstrip("./")
            text = process(name, tf.extractfile(m).read())
            if text is None:
                print("  skipped (binary/large):", name)
                continue
            write(node, name, text)
            n += 1
    return n


def hide_other_wifi(text):
    """Replace the names/SSIDs of WiFi profiles that are not the boat's (e.g. a home network)."""
    for name in re.findall(r"^== (.+)$", text, flags=re.M):
        if name not in KEEP_WIFI:
            text = re.sub(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", "<other-wifi>", text)
    return text


def command_file(node, rel, cmd, sudo=True):
    r = ssh(node, cmd, sudo=sudo)
    text = r.stdout.decode(errors="replace")
    if rel == "nmcli-connections.txt":
        text = hide_other_wifi(text)
    if r.returncode != 0 and not text.strip():
        text = "# command failed: %s\n" % r.stderr.decode(errors="replace")[:300]
    write(node, rel, scrub_text(text))


NMCLI = (
    "nmcli -f NAME,TYPE,DEVICE,AUTOCONNECT,AUTOCONNECT-PRIORITY,ACTIVE con show; echo; "
    "nmcli -g NAME con show | while IFS= read -r n; do "
    "case \"$(nmcli -g connection.type con show \"$n\")\" in *wireless*) echo \"== $n\"; "
    "nmcli -f connection.autoconnect,connection.autoconnect-priority,connection.autoconnect-retries,"
    "802-11-wireless.ssid,802-11-wireless.mode,802-11-wireless.band,ipv4.method con show \"$n\";; esac; done"
)
SERVICES = "systemctl list-unit-files --state=enabled --no-legend | awk '{print $1}'"
SECURITY_SUMMARY = r'''
import json
d = json.load(open("/home/signalk/.signalk/security.json"))
print(json.dumps({
  "devices": [{"clientId": x.get("clientId"), "description": x.get("description"), "permissions": x.get("permissions")} for x in d.get("devices", [])],
  "users": [{"type": x.get("type"), "userId": x.get("userId")} for x in (d.get("users") or [])],
  "allow_readonly": d.get("allow_readonly"), "expiration": d.get("expiration"), "acls": len(d.get("acls", [])),
  "note": "security.json itself (hashes, secrets, tokens) is deliberately NOT backed up"}, indent=2))
'''


def backup_hub():
    print("hub:", host("hub"))
    files = """home/signalk/.signalk/settings.json home/signalk/.signalk/baseDeltas.json
      home/signalk/.signalk/defaults.json home/signalk/.signalk/package.json home/signalk/.signalk/signalk-server
      home/signalk/.signalk/red/flows.json home/signalk/.signalk/red/package.json
      home/signalk/.signalk/plugin-config-data
      etc/mosquitto/mosquitto.conf etc/mosquitto/conf.d etc/grafana/grafana.ini etc/influxdb/influxdb.conf
      etc/default/gpsd etc/hostname etc/fstab etc/NetworkManager/conf.d etc/systemd/journald.conf.d
      etc/logrotate.d/arion etc/logrotate.d/rsyslog
      etc/systemd/system/arion-zero-watch.service etc/systemd/system/bme680-mqtt.service
      etc/systemd/system/signalk.service etc/systemd/system/wifi_powersave@.service
      etc/systemd/system/pypilot@.service etc/systemd/system/pypilot_web.service
      usr/local/bin/arion-zero-watch.sh home/bbb/getBME680data.py home/user/.opencpn/opencpn.conf""".split()
    print("  files:", collect("hub", files))
    command_file("hub", "nmcli-connections.txt", NMCLI)
    command_file("hub", "services-enabled.txt", SERVICES)
    command_file("hub", "versions.txt",
                 ". /etc/os-release; echo \"$PRETTY_NAME\"; uname -srm; "
                 "dpkg-query -W -f='${Package} ${Version}\\n' grafana influxdb mosquitto opencpn tailscale gpsd nodejs 2>/dev/null; "
                 "node -p \"'signalk-server ' + require('/usr/lib/node_modules/signalk-server/package.json').version\" 2>/dev/null; "
                 "pip3 show pypilot 2>/dev/null | grep -E '^(Name|Version)'")
    command_file("hub", "influxdb.txt",
                 "influx -execute 'show databases'; influx -database signalk -execute 'show retention policies'; "
                 "influx -database signalk -execute 'show measurements' | tail -n +3")
    b64 = base64.b64encode(SECURITY_SUMMARY.encode()).decode()
    command_file("hub", "signalk-security-summary.json", "echo %s | base64 -d | python3" % b64)


def backup_steering():
    print("steering:", host("steering"))
    home = "home/%s" % USER
    files = ["%s/.pypilot/%s" % (home, f) for f in
             ("pypilot.conf", "pypilot_client.conf", "servodevice", "serial_ports", "gpsd_baud_hint")]
    files += """etc/default/gpsd etc/hostname etc/fstab etc/NetworkManager/conf.d
      etc/systemd/system/pypilot.service etc/systemd/system/pypilot_web.service
      etc/udev/rules.d/99-rpi-keyboard.rules boot/firmware/config.txt boot/firmware/cmdline.txt""".split()
    print("  files:", collect("steering", files))
    command_file("steering", "nmcli-connections.txt", NMCLI)
    command_file("steering", "services-enabled.txt", SERVICES)
    command_file("steering", "versions.txt",
                 ". /etc/os-release; echo \"$PRETTY_NAME\"; uname -srm; pip3 show pypilot 2>/dev/null | grep -E '^(Name|Version)'; "
                 "dpkg-query -W -f='${Package} ${Version}\\n' gpsd 2>/dev/null")


def backup_wind():
    print("wind:", host("wind"))
    files = """etc/systemd/system/weather.service boot/firmware/config.txt boot/firmware/cmdline.txt
      etc/fstab etc/overlayroot.conf etc/hostname""".split()
    print("  files:", collect("wind", files))
    command_file("wind", "nmcli-connections.txt", NMCLI)
    command_file("wind", "services-enabled.txt", SERVICES)
    command_file("wind", "versions.txt",
                 ". /etc/os-release; echo \"$PRETTY_NAME\"; uname -srm; rtl_433 -V 2>&1 | head -1")


def backup_grafana():
    print("grafana:", host("hub") + ":3080")
    tok = base64.b64encode(("%s:%s" % (ENV["GRAFANA_USER"], ENV["GRAFANA_PWD"])).encode()).decode()

    def api(path):
        req = urllib.request.Request("http://%s:3080%s" % (host("hub"), path), headers={"Authorization": "Basic " + tok})
        return json.load(urllib.request.urlopen(req, timeout=30))

    n = 0
    for item in api("/api/search?type=dash-db&limit=500"):
        j = api("/api/dashboards/uid/%s" % item["uid"])
        slug = re.sub(r"[^a-z0-9]+", "-", j["meta"].get("slug") or item["title"].lower()).strip("-")
        write("grafana", "dashboards/%s.json" % slug, json.dumps(redact_json(j["dashboard"]), indent=2) + "\n")
        n += 1
    ds = api("/api/datasources")
    for d in ds:
        for k in ("password", "basicAuthPassword", "secureJsonData"):
            if d.get(k):
                d[k] = "<redacted>"
    write("grafana", "datasources.json", json.dumps(redact_json(ds), indent=2) + "\n")
    write("grafana", "folders.json", json.dumps(api("/api/folders"), indent=2) + "\n")
    write("grafana", "health.json", json.dumps(api("/api/health"), indent=2) + "\n")
    print("  dashboards:", n, "| datasources:", len(ds))


README = """# Arion live configuration snapshot

Generated by `scripts/backup_config.py` on {stamp}. **Secrets are removed**: Signal K `security.json`
(only `signalk-security-summary.json` is kept), Node-RED `flows_cred.json`, `~/.pypilot/signalk-token`,
WiFi profiles (only SSID/mode summaries in `nmcli-connections.txt`), SSH keys, and anything matching
password/secret/token/psk/key patterns. Re-run the script to refresh; use `git diff config/` to see what changed.

| Folder | Node | Contents |
|---|---|---|
| `hub/` | Pi 4 `lysmarine` (192.168.20.101) | Signal K `settings.json`, plugin configs, Node-RED `flows.json`; Grafana/InfluxDB/Mosquitto config (active lines only); gpsd; NetworkManager; journald; logrotate; Arion systemd units and scripts; OpenCPN config (user `user`); package versions |
| `steering/` | Pi 3B `arionpypilot` (192.168.20.100) | `~/.pypilot/pypilot.conf` (**includes IMU calibration**), gpsd, systemd units, boot config, versions |
| `wind/` | Pi Zero `arion-wx` (192.168.20.102) | `weather.service` (rtl_433), boot config, fstab, overlayroot config |
| `grafana/` | hub:3080 | dashboards (importable JSON), datasources, folders |

Paths mirror the real filesystem (e.g. `config/hub/home/signalk/.signalk/settings.json` -> `/home/signalk/.signalk/settings.json`).

## Restoring (outline)
- **Signal K:** stop `signalk`, copy back `settings.json` / `plugin-config-data/` / `red/flows.json` (Signal K can overwrite `settings.json` while running), start it.
  `security.json` is not here: re-create devices in the admin UI (Security -> Devices; the steering pypilot device needs **Read/Write**).
- **Grafana:** Dashboards -> New -> Import -> upload the JSON; recreate the InfluxDB datasource from `datasources.json` (uid `ffgddffc2s64gc`, database `signalk`).
- **pypilot:** copy `pypilot.conf` back to `~/.pypilot/` with pypilot stopped (it holds the IMU calibration and servo limits).
- **gpsd / NetworkManager / systemd:** copy to the same path, `systemctl daemon-reload`, restart the service. WiFi passwords must be re-entered.
- The Wind Zero has a read-only root: changes need the overlay unlocked (`raspi-config`) or are lost at reboot.

See `docs/data_flows.md` for how everything fits together and why each setting is what it is.
"""


def verify():
    """Fail if any real secret or obvious credential material is in the output tree."""
    bad = []
    patterns = [re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"), re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")]
    for p in OUT.rglob("*"):
        if not p.is_file():
            continue
        text = p.read_text(errors="replace")
        for s in SECRET_VALUES:
            if s in text:
                bad.append((p, "contains a value from .env"))
        for pat in patterns:
            if pat.search(text):
                bad.append((p, "looks like a JWT/private key"))
        if COORD_PAIR.search(text):
            bad.append((p, "contains a latitude,longitude pair"))
        for i, line in enumerate(text.splitlines(), 1):
            m = LINE_KV.match(line)
            if m and is_secret_key(m.group(2)) and m.group(4).strip() not in ("<redacted>", "") \
                    and not line.lstrip().startswith(("#", ";")):
                bad.append((p, "line %d has an unredacted secret-looking key" % i))
        if p.suffix == ".json":
            try:
                stack = [json.loads(text)]
            except ValueError:
                stack = []
            while stack:
                o = stack.pop()
                if isinstance(o, dict):
                    for k, v in o.items():
                        if is_secret_key(k) and isinstance(v, str) and v and v != "<redacted>" and not keep_value(k, v):
                            bad.append((p, "JSON key %r holds an unredacted value" % k))
                        stack.append(v)
                elif isinstance(o, list):
                    stack.extend(o)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="hub,steering,wind,grafana")
    args = ap.parse_args()
    todo = [x.strip() for x in args.only.split(",")]
    funcs = {"hub": backup_hub, "steering": backup_steering, "wind": backup_wind, "grafana": backup_grafana}
    for t in todo:
        if t in todo and t in funcs:
            shutil.rmtree(OUT / t, ignore_errors=True)
            try:
                funcs[t]()
            except Exception as e:  # keep going so one unreachable node does not lose the rest
                print("  !! %s failed: %s" % (t, e))
    OUT.mkdir(exist_ok=True)
    (OUT / "README.md").write_text(README.format(stamp=time.strftime("%Y-%m-%d %H:%M %Z")))
    if _askpass_dir:
        shutil.rmtree(_askpass_dir, ignore_errors=True)
    bad = verify()
    if bad:
        print("\nSECRET CHECK FAILED - do NOT commit:")
        for p, why in bad:
            print("  ", p.relative_to(ROOT), "-", why)
        sys.exit(1)
    nfiles = sum(1 for p in OUT.rglob("*") if p.is_file())
    print("\nOK: %d files in config/, secret check passed." % nfiles)


if __name__ == "__main__":
    main()
