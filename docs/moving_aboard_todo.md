# Moving the stack aboard: to-do list

Drawn up 2026-10-11, after the desk build and test of the shore link (see `network_map.md`). Items are ordered by how much they reduce the chance of a failure you cannot fix from home. Tick them off as they are done.

## 1. Do before it goes aboard

- [ ] **Ethernet for the hub and steering Pi.** The EZR23 has one LAN port, so add a small unmanaged gigabit switch fed from the boat's 12 V (look for wide-input 9-48 V or 12-56 V industrial 5-port types, or a 12 V mini switch). Cable hub and steering Pi to it, keep WiFi as a fallback profile, keep the `wifi-recovery` timer. Test that unplugging the cable falls back to WiFi.
- [ ] **Replace the cheap 5 V buck converters** with fused, decent-quality converters, one per node (see "Parts to consider" below). Then check `vcgencmd get_throttled` reads `0x0` under load on the hub and steering node.
- [ ] **Cold-boot soak:** power the whole stack up 5 to 10 times, including with the shore link off, and confirm the hub joins `YachtArion` every time. Check `sudo journalctl -t wifi-recovery` afterwards: this is the only way to see whether the timer ever fires.
- [ ] **Real-distance link test** (Bullet M2 with 12 dBi omni, Wavlink on the boat on its mooring): read signal and CCQ on the Bullet, test in wind. Decide then whether a directional antenna is needed. After any Bullet reset or firmware change, check the Main page shows `airMAX: Disabled`.
- [ ] **Autopilot stands alone:** switch off the hub, WiFi and shore link, and confirm the steering node still steers and holds heading. Nothing safety-critical should depend on the network.
- [ ] Calibrate the compass aboard (still at default; recalibrate after any physical move), and check the rudder reading once the sensor is connected (about -41 degrees when unconnected).

## 2. Cheap robustness

- [ ] Hardware watchdog on each Pi (`RuntimeWatchdogSec` in `/etc/systemd/system.conf`, plus `dtparam=watchdog=on` where needed) so a hung Pi reboots itself. The read-only wind Zero needs care: do not unlock it unless asked.
- [ ] Time without internet: confirm the hub keeps time from its GPS puck (gpsd + chrony) and that the wind Zero gets time from the hub. The Pis have no real-time clock.
- [ ] Image each Pi's SD/SSD once it is working, and keep a spare card for the steering node. Run `scripts/backup_config.py` before leaving. See `backup_and_recovery.md`.
- [ ] Check the 4G data plan and what can run unattended over `MOBILE` (updates, large syncs).
- [ ] Mosquitto is anonymous (LAN only). Fine on the boat LAN behind the EZR23; revisit if the LAN is ever bridged.

## 3. Useful additions

- [ ] **Battery and rail voltage monitoring** in Signal K and Grafana (see "Parts to consider").
- [ ] **Grafana alerts:** battery voltage low, hub offline, wind data stale.
- [ ] **Remote power-cycle for the hub** (switchable relay on the hub's feed). Design it so a failed relay cannot cut power to anything safety-critical; the steering node and autopilot are NOT on it.
- [ ] Pre-departure checklist: add the network items (Wavlink 2.4G Wi-Fi ON, airMAX disabled, `flow` client disabled, radio on channel 11, live-uplink check with `ping -c1 -t2 1.1.1.1`, `get_throttled`) to `preflight_checklist.md`.
- [ ] Update `docs/EZR23_router_setup.md` with the final uplink setup (mwan3 metrics 10/20/30).

## 4. Physical

- [ ] Drip loops, sealed connectors, PoE injector kept dry (passive PoE: injector "POE" port to the device only).
- [ ] Strain-relieved, labelled Ethernet cables.
- [ ] Wavlink antennas upright and clear of metal.
- [ ] Fuse each converter's input; keep converters away from the VHF and AIS antennas and cables, since cheap switchers radiate noise.

## 5. Small loose ends

- [ ] Clean the Wavlink's own WiFi password field (browser autofill junk). Use a private window.
- [ ] Set the Bullet's clock (cosmetic).
- [ ] Delete the hub's old `flow` NetworkManager profile if it is no longer wanted.
- [ ] Hub's `~/pypilot4arion` clone: pulled to `d6bdb80` on 2026-10-11; pull again after any laptop commit.

## Parts to consider

Prices and listings change; check the seller and reviews, and prefer a seller that shows a real input/output spec and a ripple figure.

**12 V to 5 V converters (per Pi, with margin)**
- A Pi 4 can draw about 3 A under load; a Pi 3B about 2.5 A. Choose 5 A (25 W) rated modules so they run cool.
- Input range should cover 8-32 V or better (a boat's charging voltage reaches 14.4 V and can spike). Look for reverse-polarity, over-current, over-temperature and short-circuit protection stated in the listing.
- USB-C output (with the supplied lead) or bare wires; either works. Measure the output at the Pi with a meter: it should hold 5.1 V or more under load, with the Pi's own `get_throttled` as the final judge.
- Prefer an enclosed or potted module and add an inline fuse (3 A to 5 A) on the 12 V side.
- Search terms: "12V 24V to 5V 5A USB-C step down converter 25W", "waterproof DC 8-32V to 5V 5A".
- A known-good alternative is the UCTRONICS 9-36 V to 5 V 5 A USB buck module (dearer than a generic AliExpress part).
- For anything near radios, a low-noise marine-oriented converter (for example the Quarkelec A013) exists, but it is only rated for 500 mA, so it suits a sensor such as the wind Zero, not a Pi 4.

**Voltage monitoring**
- INA219 or INA226 I2C module on a Pi: reads bus voltage (INA219 to 26 V) and current via a shunt. Signal K has an INA219 plugin (`signalk-raspberry-pi-4ch-ina219`). Fine for the 12 V house rail; use a proper shunt rating for any current measurement.
- An ADS1115 behind a resistor divider is a cheaper, voltage-only alternative.
- Check what the existing 12 V and solar documents already measure (`battery_system.md`, `12v_solar_system.md`, MPPT) before buying anything, in case the charger already reports battery voltage that Signal K can read.

**Switchable relays**
- An ESP32 relay board running Tasmota (for example the LILYGO T-Relay, 5-24 V supply, relays rated about 10 A at 28 V DC) gives remote on/off over WiFi and MQTT. The hub's Mosquitto is already on the LAN.
- Use it only on the hub's feed or non-critical loads, not the steering node. A latching or normally-closed arrangement is better so that a relay board failure leaves the hub powered.

**Ethernet switch**
- Unmanaged 5-port gigabit, wide DC input (about 9/12 V to 48/56 V), small, and fanless. Industrial DIN-rail types are sturdier than desktop ones but dearer.
