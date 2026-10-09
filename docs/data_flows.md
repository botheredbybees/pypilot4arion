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
Signal K NMEA out `101:10110`, MQTT `101:1883`, Grafana `101:3080` (not 3000, that is Signal K), InfluxDB `101:8086`, gpsd `127.0.0.1:2947` (each Pi, local only).

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

Heading, rudder and attitude reach Signal K by **two routes** (since 2026-10-08):
- **Native:** the steering pypilot's own Signal K client (`signalk.enabled`, source `pypilot`, device `pypilot-90687870926`). This needed that device set to **Read/Write** in Signal K (Security -> Devices); it was read-only, so pypilot could listen but not publish, and nothing wrote `navigation.attitude` after the hub's pypilot was disabled. It publishes `navigation.headingMagnetic`, `navigation.attitude` (pitch, roll, yaw), `steering.rudderAngle` and, from its own sensors, position/SOG/COG. Publish period was lowered from 0.1 s to **0.5 s** (`pypilot_client signalk.period=0.5`).
- **NMEA:** the `Pypilot_Raw_Data` reader on :20220 (HDM, ROT, RSA).
Signal K priorities prefer native `pypilot`, then `Pypilot_Raw_Data.AP` after 10 s, for `navigation.headingMagnetic` and `steering.rudderAngle`; position/SOG/COG stay `local_gpsd.GN` only (pypilot's own puck does **not** override it, verified). The two routes agree (heading 345.7 deg and identical rudder values on both). InfluxDB still logs both (a few hundred points/min, harmless). The NMEA route is **not an independent fallback**: it uses the same WiFi and the same pypilot process. After granting a device write access, **restart Signal K** so pypilot reconnects; an already-open websocket keeps its old (read-only) permission.
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

**WS80 power:** `battery_mV` has stayed between 3.00 and 3.08 V since April 2026 (3.06 V on 2026-10-07; InfluxDB `electrical.batteries.ws80.voltage`), so the sensor's own supply is healthy. The wind Zero's outages are therefore *not* explained by a flat WS80 battery: the Zero (receiver, MQTT client) has its own 5V supply and WiFi.

**Node-RED is not a separate service.** It is hosted by the Signal K plugin `signalk-node-red` (UI is inside the Signal K admin).
Flows: `/home/signalk/.signalk/red/flows.json` (credentials in `flows_cred.json`, never commit or print it). Broker: `localhost:1883`.

| Flow | In (MQTT topic) | Does | Out |
|---|---|---|---|
| WS80 Raw Data | `rtl_433/arion-wx/events` | degrees -> radians, mV -> V | `environment.wind.angleApparent`, `electrical.batteries.ws80.voltage` (source `node-red-ws80`) |
| BME680 Raw Data | `arion/sensors/cabin/bme680` | maps gas resistance to a rough air-quality value, drops bad readings | Signal K delta + debug node |

The BME680 topic is published by `scripts/getBME680data.py` (I2C `0x77`, broker `localhost`, so it runs on the **hub**, retained messages).
Unplugging the breakout board stops this flow; it does not affect steering.

**WS80 angle label (checked 2026-10-07).**
- The flow publishes `wind_dir_deg` x pi/180 as `environment.wind.angleApparent` in the range 0..2pi (272 deg = 4.747 rad). Wind *speed* arrives separately from the `signalk-mqtt-sensors` plugin as `environment.wind.speedApparent`.
- The label is **correct if the WS80's "N" mark points at the bow**: a fixed anemometer on a moving boat then reads apparent wind, relative to the bow. The WS80 has no moving parts and, as far as we know, no compass, so the angle is relative to the mark, not to north. **Owner confirmed 2026-10-07: aboard Arion it will face forward and turn with the boat**, so `angleApparent` is right. (It is currently on the carport, so readings are relative to wherever it is pointing.) If the mark is later found off the centreline, apply the offset.
- **Fixed 2026-10-08:** Signal K's spec gives `angleApparent` as -pi..pi (negative to port). The Node-RED function now wraps values above pi (`windRad -= 2*Math.PI`). The 0..2pi range made Grafana's `mean()` return nonsense whenever the wind hovered near 0/360 (the mean of 359 and 1 deg is 180), and it disagreed with pypilot's own republished copy (which was already -pi..pi). The NMEA converter still sends pypilot a 0-360 MWV (its tests: -pi/2 becomes `MWV 270.00`). Backups: `/home/signalk/.signalk/red/flows.json.bak-20261008-071123`, `settings.json.bak-20261008-071123`.
- **Pypilot republishes wind to Signal K** (source `pypilot`, about 2 points/s) because it receives wind over NMEA (`wind.source = tcp`) and, now it may write, echoes it back. That is the SK -> MWV -> pypilot -> SK loop. Values agree with the original sources (checked after the wrap fix), so both are written to InfluxDB and Grafana averages them. Priorities `signalk-node-red.XX` / `signalk-mqtt-sensors` ahead of `pypilot` were added for `environment.wind.angleApparent` / `speedApparent`, but Signal K still serves the `pypilot` value, so they have **no visible effect**; leave or remove them. Filter a panel with `WHERE "source" = 'signalk-node-red.XX'` if exact sensor values are wanted.
- **SOG at rest is noisy** (median 0.24 kn, max 0.81 kn over 3 h on the windowsill puck: 3 satellites used, HDOP about 2.9). It is **not** coupled to apparent wind (correlation r = 0.09 with speed, -0.23 with angle before the wrap fix). It does feed pypilot's *true wind* (`truewind.source = gps+wind`) and Signal K's derived true wind. Best fix is the puck's position on the boat; display-level fixes: Grafana value mapping 0-0.5 kn -> 0.0, OpenCPN *Filter NMEA Course and Speed data*.
- The `signalk-wind-calibration` plugin is configured with the path `"environment.wind.angleApparent "` (**trailing space**) and offset 0, so it matches nothing. Harmless while the offset is 0, but it would silently do nothing if you set an offset. Fix the path before relying on it.
- Pypilot gets wind via Signal K -> `sk-to-nmea0183` (MWVR/MWVT enabled) -> `Send_Wind_to_Pypilot` -> pypilot :20220 (`wind.source = tcp`).

## Route following (pypilot `nav` mode)

Verified 2026-10-07: pypilot's mode list is `[compass, gps, wind, true wind]`; **`nav` is missing and `apb.source = none`**.
`nav` appears only when pypilot receives an **APB** sentence (`pypilot/nmea.py parse_nmea_apb`) or the Signal K path `steering.autopilot.target.headingTrue`.
Nothing currently provides it:
- OpenCPN (user `user`) has only the GPSd input connection and **no output connection**, so an active route sends nothing.
- Signal K's `sk-to-nmea0183` plugin has `APB: false`, and the Signal K -> pypilot link carries nothing OpenCPN produces.

To enable it: in OpenCPN (Options -> Connections) the connection added on 2026-10-07 was **Input, localhost:20220**, which does nothing (that is the hub, and nothing listens there). Edit it to **Network / TCP, address `192.168.20.100`, port `20220`, Direction Output** (untick Receive input), with APB allowed in the output filter; keep GPSd and Signal K as inputs and use *Adjust communication priorities* to put GPSd first for position. Then activate a route: `nav` should appear in the pypilot mode list (check with `pypilot_client ap.modes apb.source`). Test at the dock with **AP off**. Status: before a route is active, modes are `[compass, gps, wind, true wind]` and `apb.source = none`. **Verified 2026-10-08:** with the OpenCPN Output connection to `192.168.20.100:20220` and a route activated, `ap.modes = [compass, gps, nav, wind, true wind]`, `apb.source = tcp`, `apb.track` and `apb.xte` update. Not yet tried: engaging the pilot in `nav` mode (do it at the dock with the helm manned first).

Pypilot streams its own NMEA to every :20220 client; OpenCPN's Output-only link never reads it, so pypilot's per-client 64 KB output buffer eventually overflows and it drops that socket (log line `overflow in pypilot socket`); OpenCPN reconnects. Harmless; if route data ever cuts out periodically, look for that line in `journalctl -u pypilot` on the steering node.
Pypilot's NMEA module also probes USB serial ports (38400 and 4800 baud); probes of the Arduino and GPS ports fail with `Errno 16` (busy) because pypilot's servo and gpsd already hold them.
Pypilot's own `gps.source` falls back from `gpsd` to `signalk` if the steering puck has no fix (seen 2026-10-07 when the puck on the windowsill lost its fix); that is by design.

## Grafana

Grafana (`http://192.168.20.101:3080`) allows **anonymous Viewer access** (no login), set in `/etc/grafana/grafana.ini` under `[auth.anonymous]` (`enabled = true`, `org_role = Viewer`) on 2026-10-07. Dashboards: `Arion`, `Arion Master Sailing Hub`, `Arion Sailing Dashboard`. To edit a dashboard, log in as the Grafana admin. Anyone on YachtArion or the tailnet can *view*; if that is not acceptable, set `enabled = false`. Data source: InfluxDB 1.x database `signalk` (fed by the Signal K `signalk-to-influxdb` plugin).

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
| Signal K before heading/rudder priorities | `...settings.json.bak-20261008-070337` | same |
| gpsd (steering) | `/etc/default/gpsd.bak-20261007`, `.bak2-20261007` | copy back, `sudo systemctl restart gpsd` |
| OpenCPN | `/home/user/.opencpn/opencpn.conf` | close OpenCPN first; no automatic backup exists |
| Journal / WiFi / logrotate changes (hub) | `/etc/systemd/journald.conf.d/persistent.conf`, `/etc/NetworkManager/conf.d/wifi-powersave-off.conf` (also on steering), `/root/backup-20261007/logrotate-rsyslog.bak` | delete the drop-ins and restart `systemd-journald` / NetworkManager; restore the logrotate file |
| Grafana config before anonymous access | `/etc/grafana/grafana.ini.bak-20261007` (hub) | copy back, `sudo systemctl restart grafana-server` |
| Grafana DB + InfluxDB before the 2026-10-07 upgrades | `/root/backup-20261007/` (hub) | `grafana.db`, `etc-grafana/`, portable `influx/` backup (`influxd restore -portable`) |

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
(`0x0` is healthy) and `dmesg | grep -i voltage`. The hub's journal is **persistent since 2026-10-07** (Lysmarine ships `Storage=volatile`; the drop-in `/etc/systemd/journald.conf.d/persistent.conf` sets `Storage=persistent`, `SystemMaxUse=500M`), so after a loop read the failed boot with `sudo journalctl --list-boots` then `sudo journalctl -b -1`.

**Wind node keeps dropping**
Read `/var/log/arion/zero-mqtt-events.log` on the hub. `exceeded timeout` then `session taken over` means an unclean restart (power or WiFi), not a clean shutdown.

## Pitfalls we hit

- **GP vs GN talker.** A multi-GNSS puck reports `GN`; a priority list naming `GP` silently never matches, so a lower source wins.
- **Two config homes.** `bbb` and `user` each have a `~/.opencpn`; the running one is `user`'s.
- **A second pypilot on the hub** (installed by Lysmarine) competed with the real one as a Signal K source.
- **No RTC.** Clocks start at the last saved time and jump when NTP syncs, so early-boot services carry wrong timestamps.
- **`logrotate.service` failed on the hub** (not the clock): `/etc/logrotate.d/rsyslog` had a `/var/log/messages` stanza with no `missingok`. Fixed 2026-10-07. Never leave `.bak` files inside `/etc/logrotate.d/`: logrotate reads them and reports duplicate entries.
- **The hub can boot onto its own hotspot instead of YachtArion** (seen 2026-10-09 after a power-up: the router was not up yet, so NetworkManager started the Lysmarine AP profile `lysmarine-hotspot`, `mode ap`, `ipv4.method shared`, and the hub stayed there: off the boat LAN, off Tailscale, unreachable from the Pis' side). Fixed: `connection.autoconnect no` on both `lysmarine-hotspot` and `lysmarine-hotspot 1` (profiles kept), `YachtArion` given `autoconnect-priority 10` and `autoconnect-retries 0` (retry forever). Undo with `nmcli con modify "lysmarine-hotspot" connection.autoconnect yes`. After any power-up, if the hub is not on the tailnet, check which SSID it joined. A `flow` WiFi profile (home network) also autoconnects at priority 0.
- **WiFi power saving** is left at the driver default, which can cause latency spikes and dropouts on an always-on node. `/etc/NetworkManager/conf.d/wifi-powersave-off.conf` (`wifi.powersave = 2`) was added on the hub and the steering node on 2026-10-07; it takes effect at the next WiFi reconnect/reboot (not applied live to the pilot). The locked wind Zero has not been changed.
- **apt repo keys (fixed 2026-10-07).** InfluxData (`NO_PUBKEY DA61C26A0585BD3B`) and Grafana (`EXPKEYSIG 963FA27710458545`) keys were refreshed from the vendors; they now live in `/usr/share/keyrings/influxdata-archive.gpg` and `/usr/share/keyrings/grafana.gpg` (scoped with `signed-by`). Old files are backed up in `/root/apt-key-backup-20261007/`. Fingerprints: InfluxData `24C975CBA61A024EE1B631787C3D57159FC2F927`, Grafana `B53AE77BADB630A683046005963FA27710458545`. Re-check when the subkeys expire (Grafana 2027).
  `curl ... | sh` for Tailscale aborts on those errors: use `sudo apt-get install tailscale` after the repo is added.
- **Pypilot timestamps** from Signal K are offset by the local UTC offset (11 h in AEDT) because `pypilot/signalk.py:434` uses `time.mktime` on a UTC string. Cosmetic; nothing checks freshness with it.
- **Cheap 5V converters** are the prime suspect for hub undervoltage events and the wind node's unclean reboots. Better converters are on hand but not yet fitted.

## Open issues

- Steering node WiFi: ping varies from about 5 ms to 400 ms and dropped once. Fix before relying on it at sea.
- Wind node reboots (about 16:32, 17:07, 18:20 on 2026-10-07), cause unknown.
- Hub: one 4 s undervoltage event with the BME680 board disconnected; the board itself is still a suspect for the original boot loop.
- Upgraded 2026-10-07: Grafana 12.0.0 -> 13.2.3 and InfluxDB 1.11.8 -> 1.13.1 (health ok, Signal K still writing). Pre-upgrade backups on the hub: `/root/backup-20261007/` (`grafana.db`, `etc-grafana/`, `influx/` portable backup ~1.2 GB). 24 other packages are still not upgraded.
- **Wind Zero keeps dropping off**: outages at about 16:32, 17:07, 18:20, 20:34-20:37 and again after 20:37:35 on 2026-10-07 (see `/var/log/arion/zero-mqtt-events.log` on the hub). While it is down, pypilot loses `wind`/`true wind` modes. It is currently on the carport (WiFi range?) with a cheap 5V supply; cause not yet isolated (power vs WiFi).
- **Grafana "Autopilot State" panel** must read the text field and not filter by time: query `SELECT last("stringValue") FROM "steering.autopilot.state"`, and set the stat panel's *Value options -> Fields* to **All fields** (the default "numeric fields" hides text).
- The rudder reads about -41 deg (pypilot `rudder.angle` 40.5, `servo.position` 44) on the desk, which is what an unconnected/uncalibrated rudder pot would show. Check the rudder feedback wiring and calibration before relying on the rudder gauge.
- Wind-calibration plugin's trailing-space path: see Wind (mounting reference confirmed, angle range fixed).
- `nav` mode needs an APB feed that does not exist yet: see Route following.
- Duplicate `HDM/ROT/RSA` flows were reduced to one reader; the pypilot -> Signal K path for any other values has not been audited.
