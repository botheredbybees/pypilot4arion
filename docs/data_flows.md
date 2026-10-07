# Arion data flows and configuration

Authoritative description of how data moves between the three Pis, and of the settings that make it work.
Verified live on **2026-10-07**. If this file disagrees with an older doc, this file wins.

Contents: [Nodes](#nodes) · [Position](#position-gps) · [Heading, rudder and autopilot](#heading-rudder-and-autopilot) · [Wind](#wind) · [Signal K](#signal-k-configuration) · [OpenCPN](#opencpn) · [gpsd](#gpsd) · [Do not change](#things-that-must-stay-as-they-are) · [Access](#remote-access) · [Backups](#backups-and-rollback) · [Troubleshooting](#troubleshooting) · [Pitfalls](#pitfalls-we-hit) · [Open issues](#open-issues)

## Nodes

All on the **YachtArion** WiFi (router EZR23, `192.168.20.1`). SSH user is `bbb` on every Pi.

| Node | Hostname | IP | Hardware / OS | Role |
|---|---|---|---|---|
| Steering | `arionpypilot` | 192.168.20.100 | Pi 3B, Debian 13, pypilot 0.60 | pypilot (autopilot, web UI :8000), IMU, Arduino Nano motor controller, GPS puck #2 |
| Hub | `lysmarine` | 192.168.20.101 | Pi 4, Lysmarine (Debian 12), root on USB SATA SSD | Signal K, Mosquitto, InfluxDB, Grafana, OpenCPN, gpsd + GPS puck #1, Tailscale |
| Wind bridge | `arion-wx` | 192.168.20.102 | Pi Zero WX, **read-only root (overlayroot)** | Ecowitt WS80 via rtl_433, publishes to MQTT |

Ports worth knowing: pypilot web `100:8000`, pypilot server `100:23322`, pypilot NMEA `100:20220`, Signal K `101:3000`,
Signal K NMEA out `101:10110`, MQTT `101:1883`, gpsd `127.0.0.1:2947` (each Pi, local only).

## Position (GPS)

There are two independent GPS pucks, so the autopilot does not depend on the hub or the WiFi for position.

```
 PUCK #1 (hub, Prolific USB-serial, 4800 baud, GN talker)
   -> gpsd (hub, 127.0.0.1:2947)
        -> Signal K provider "local_gpsd"  => navigation.position, SOG, COG   ($source local_gpsd.GN)
        -> OpenCPN "GPSd" connection (127.0.0.1:2947)

 PUCK #2 (steering Pi, Prolific USB-serial, 4800 baud, GP talker)
   -> gpsd (steering, 127.0.0.1:2947)
        -> pypilot  (gps.source = gpsd; falls back to Signal K if the puck drops)
```

- Pypilot prefers a local gpsd over Signal K (`source_priority` in `pypilot/sensors.py`).
- Signal K does **not** take position from pypilot. See priorities below.
- Puck #1 reports the **GN** talker (multi-constellation). Signal K therefore names the source `local_gpsd.GN`.
  `local_gpsd.GP` only carries GSV (satellites in view). Priorities must name `GN`.

## Heading, rudder and autopilot

```
 IMU + Arduino motor controller -> pypilot (steering) --NMEA TCP :20220--> Signal K "Pypilot_Raw_Data"
        => navigation.headingMagnetic, navigation.rateOfTurn, steering.rudderAngle   ($source Pypilot_Raw_Data.AP)

 Signal K plugin "pypilot-autopilot-provider" --HTTP--> 192.168.20.100:8000   (controls the autopilot)
 Signal K "Send_Wind_to_Pypilot" --NMEA TCP :20220--> pypilot   (sends Signal K's NMEA output, e.g. wind, to pypilot)
```

Heading/rudder reach Signal K **only** through the NMEA link on port 20220. There is no native `pypilot` source for them.
Keep one reader and one writer on 20220 (see providers below). More than that duplicates every sentence.

## Wind

```
 Ecowitt WS80 --433 MHz--> rtl_433 on arion-wx --MQTT--> Mosquitto on the hub (topic rtl_433/arion-wx/events)
   --> Node-RED flow "WS80 Raw Data" (inside Signal K) --> Signal K deltas, source "node-red-ws80"
        environment.wind.angleApparent   (wind_dir_deg x 0.0174533 -> radians)
        electrical.batteries.ws80.voltage (battery_mV x 0.001 -> volts)
   --> Signal K "Send_Wind_to_Pypilot" (NMEA out) --> pypilot :20220  => "wind" appears in pypilot's mode list
   --> InfluxDB/Grafana, OpenCPN
```

`rtl_433 -F mqtt://192.168.20.101 1883 retain 1 events rtl_433/arion-wx/events`. MQTT client id `rtl_433-2546ffff847a`.

**Node-RED is not a separate service.** It is hosted by the Signal K plugin `signalk-node-red` (UI is inside the Signal K admin).
Flows: `/home/signalk/.signalk/red/flows.json` (credentials in `flows_cred.json`, never commit or print it). Broker: `localhost:1883`.

| Flow | In (MQTT topic) | Does | Out |
|---|---|---|---|
| WS80 Raw Data | `rtl_433/arion-wx/events` | degrees -> radians, mV -> V | `environment.wind.angleApparent`, `electrical.batteries.ws80.voltage` (source `node-red-ws80`) |
| BME680 Raw Data | `arion/sensors/cabin/bme680` | maps gas resistance to a rough air-quality value, drops bad readings | Signal K delta + debug node |

The BME680 topic is published by `scripts/getBME680data.py` (I2C `0x77`, broker `localhost`, so it runs on the **hub**, retained messages).
Unplugging the breakout board stops this flow; it does not affect steering.

Observation, not yet checked: the flow labels the WS80 direction `angleApparent`. The WS80 reports an absolute wind direction, so whether that is
truly apparent wind relative to the bow should be confirmed before wind-mode steering is trusted.

## Signal K configuration

Server runs as user `signalk`; config is `/home/signalk/.signalk/settings.json` (needs sudo). Admin UI: `http://192.168.20.101:3000`.

### Source priorities (Server -> Data Priorities)

`navigation.position`, `navigation.speedOverGround`, `navigation.courseOverGroundTrue` = **`local_gpsd.GN` only**.
Pypilot was deliberately removed as a fallback: pypilot has no GPS of its own on the hub path, so a fallback could only
republish stale data under a fresh timestamp.

### Providers (`pipedProviders`)

| Provider id | State | What it does |
|---|---|---|
| `local_gpsd` | enabled | gpsd client, `127.0.0.1:2947`. The real GPS source. |
| `Pypilot_Raw_Data` | enabled | TCP client to `192.168.20.100:20220`. The single reader of pypilot heading/ROT/rudder. |
| `Send_Wind_to_Pypilot` | enabled | TCP client to `192.168.20.100:20220` with `toStdout: nmea0183out`. Sends Signal K's NMEA to pypilot. Inbound `HDM`,`ROT`,`RSA` are ignored so it only transmits. |
| `pypilot_nmea` | disabled | Duplicate reader of 20220. |
| `nmea0183_feed` | disabled | Mis-typed leftover: an NMEA reader pointed at gpsd's JSON port 2947. |
| `OpenCPN` | disabled | Expected OpenCPN NMEA output on `localhost:30330`; nothing ever listened. |
| `Arion_OpenPlotter_GPS`, `_IMU` | removed | Leftovers from the OpenPlotter design. |

## OpenCPN

- **OpenCPN 5.10.2 runs as the desktop user `user`, not `bbb`.** The config that matters is `/home/user/.opencpn/opencpn.conf`.
  A stale `/home/bbb/.opencpn/opencpn.conf` once misled us (edited it, no effect); it has been deleted.
- Connection in use: **GPSd, 127.0.0.1, port 2947** (added in Options -> Connections -> Add Connection -> Network -> GPSD).
  Add a Signal K connection (`192.168.20.101:3000`) only if you want wind/depth/AIS in OpenCPN.
- OpenCPN rewrites its config on exit. Edit the file only while OpenCPN is closed, or use the GUI.

## gpsd

| Node | `/etc/default/gpsd` | Notes |
|---|---|---|
| Hub | `DEVICES="/dev/ttyUSB0"`, `GPSD_OPTIONS="-n -G"` | Puck #1. |
| Steering | `USBAUTO="false"`, `GPSD_OPTIONS="-n -b"`, `DEVICES="/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0"` | Puck #2 by stable path. `-b` is read-only. `USBAUTO=false` stops gpsd auto-grabbing the Arduino's FTDI port (`usb-FTDI_FT232R_USB_UART_BG02A9O7-if00-port0`). |

Always use `/dev/serial/by-id/...`, never `ttyUSB0/1`: the numbers change with plug order. Backup: `/etc/default/gpsd.bak-20261007`, `.bak2-20261007` on the steering node.

## Things that must stay as they are

1. **The hub's local pypilot stays disabled** (`pypilot@pypilot`, `pypilot_web` on :8080, `pypilot_detect`). Lysmarine installs it (pypilot 0.56).
   It read gpsd directly and published a competing `pypilot` position into Signal K. It also probes serial ports at boot, which risks fighting gpsd for the GPS puck.
   The real pypilot is on the steering node. Do not re-enable it.
2. **Steering node `USBAUTO="false"`.** Do not set it back to true; gpsd must not touch the motor controller's serial port.
3. **The wind Zero keeps its read-only root.** Changes, logs and SSH keys vanish at reboot by design (protects the SD card). Do not unlock it casually.
   Consequences: password login only, no local logs, and `systemd-remount-fs.service` shows failed (harmless).
4. **Signal K position priority stays `local_gpsd.GN` only.**

## Remote access

- Hub on Tailscale: `100.123.233.82` (account botheredbybees@), `--ssh`, subnet router `192.168.20.0/24`.
  The route was **approved in the admin console and key expiry disabled on 2026-10-07**. Clients must accept routes
  (`sudo tailscale set --accept-routes` on Linux; "Use Tailscale subnets" on Android). Verified from the laptop on a different network:
  `192.168.20.100:8000` (pypilot web UI) and `192.168.20.101:3000` (Signal K) load, and `.100/.101/.102` answer pings.
  Tailscale SSH asks for a one-off browser approval link; approve it once and sessions work for a while.
- Reach the other Pis by jumping through the hub:
  `ssh -o ProxyCommand="ssh -W %h:%p bbb@100.123.233.82" bbb@192.168.20.100`
  (add `-o HostKeyAlias=192.168.20.101` for the hub hop if it complains about a new host key).
- Keys are installed on the hub and the steering node. The wind Zero needs the password.
- Hosts, passwords and IPs are kept in `.env` at the repo root. It is git-ignored; never commit it or paste its values.

## Backups and rollback

| What | Where | How to undo |
|---|---|---|
| Signal K before priority fix | `/home/signalk/.signalk/settings.json.bak-20261007-171535` | `sudo systemctl stop signalk`, copy back, `sudo systemctl start signalk` |
| Signal K before provider cleanup | `...settings.json.bak-20261007-171655` | same |
| Signal K before link consolidation | `...settings.json.bak-20261007-173836` | same |
| gpsd (steering) | `/etc/default/gpsd.bak-20261007`, `.bak2-20261007` | copy back, `sudo systemctl restart gpsd` |
| OpenCPN | `/home/user/.opencpn/opencpn.conf` | close OpenCPN first; no automatic backup exists |

Signal K can overwrite `settings.json` while running, so always stop it before restoring a file.

Reboot watcher on the hub: `arion-zero-watch.service` logs the wind node's MQTT connects/disconnects to
`/var/log/arion/zero-mqtt-events.log` (rotated weekly). It is the only reboot history for the Zero.

## Troubleshooting

**OpenCPN shows no position**
1. Which user runs it? `ps -o user= -p $(pgrep -x opencpn)` -> `user`. Edit that user's config, not `bbb`'s.
2. Options -> Connections must list `GPSd 127.0.0.1:2947`. An empty list means no data.
3. Is gpsd live? `gpspipe -w -n 5` on the hub (or read `127.0.0.1:2947`). A `TPV` with `mode` 2 or 3 is a fix.
4. Is the puck seeing sky? On a windowsill expect few satellites (`uSat` small) and poor accuracy.

**Signal K position is wrong or frozen**
1. `curl -s localhost:3000/signalk/v1/api/vessels/self/navigation/position` -> `$source` must be `local_gpsd.GN`.
2. `curl -s localhost:3000/signalk/v1/api/sources` -> `local_gpsd` RMC/GGA timestamps must be current. If frozen, `sudo systemctl restart signalk`
   (seen once after an undervoltage event: gpsd recovered but Signal K's feed did not).

**Hub will not boot (splash <-> boot log loop)**
Unplug all peripherals and the breakout board; reconnect one at a time. The BME680 board is suspected. Check `vcgencmd get_throttled`
(`0x0` is healthy) and `dmesg | grep -i voltage`. There is no persistent journal by default; enable it with
`sudo mkdir -p /var/log/journal && sudo systemctl restart systemd-journald` so the next loop leaves evidence.

**Wind node keeps dropping**
Read `/var/log/arion/zero-mqtt-events.log` on the hub. `exceeded timeout` then `session taken over` means an unclean restart (power or WiFi), not a clean shutdown.

## Pitfalls we hit

- **GP vs GN talker.** A multi-GNSS puck reports `GN`; a priority list naming `GP` silently never matches, so a lower source wins.
- **Two config homes.** `bbb` and `user` each have a `~/.opencpn`; the running one is `user`'s.
- **A second pypilot on the hub** (installed by Lysmarine) competed with the real one as a Signal K source.
- **No RTC.** Clocks start at the last saved time and jump when NTP syncs, so early-boot services carry wrong timestamps and `logrotate` may fail once.
- **apt repo keys.** InfluxData (`NO_PUBKEY DA61C26A0585BD3B`) and Grafana (`EXPKEYSIG 963FA27710458545`) keys need refreshing, or those two never upgrade.
  `curl ... | sh` for Tailscale aborts on those errors: use `sudo apt-get install tailscale` after the repo is added.
- **Pypilot timestamps** from Signal K are offset by the local UTC offset (11 h in AEDT) because `pypilot/signalk.py:434` uses `time.mktime` on a UTC string. Cosmetic; nothing checks freshness with it.
- **Cheap 5V converters** are the prime suspect for hub undervoltage events and the wind node's unclean reboots. Better converters are on hand but not yet fitted.

## Open issues

- Steering node WiFi: ping varies from about 5 ms to 400 ms and dropped once. Fix before relying on it at sea.
- Wind node reboots (about 16:32, 17:07, 18:20 on 2026-10-07), cause unknown.
- Hub: one 4 s undervoltage event with the BME680 board disconnected; the board itself is still a suspect for the original boot loop.
- InfluxData and Grafana apt keys need refreshing.
- Node-RED labels the WS80 direction `angleApparent`; confirm the reference (see Wind) before trusting wind mode.
- Duplicate `HDM/ROT/RSA` flows were reduced to one reader; the pypilot -> Signal K path for any other values has not been audited.
