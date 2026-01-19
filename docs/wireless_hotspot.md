# Wireless Hotspot Configuration for YachtArion

## Introduction

The YachtArion pypilot system uses a **Google Pixel 2 Android phone** as a dedicated wireless access point to create a private onboard network. This approach provides a reliable, low-cost networking solution specifically suited for marine environments where traditional WiFi routers may be impractical.

### Why Use a Phone as a Hotspot?

The Pixel 2 phone serves multiple purposes in the YachtArion system:

1. **Dedicated Network Hub**: Creates a stable WiFi network (SSID: "YachtArion") that connects the Raspberry Pi Zero W (Tinypilot) and Raspberry Pi 4 (Lysmarine) in a private network topology
2. **Low Power Consumption**: Modern phones are optimized for battery life, consuming less power than traditional marine WiFi routers (~2-5W typical)
3. **Built-in Battery Backup**: Phone's internal battery provides automatic UPS functionality during power interruptions
4. **GPS Receiver**: Can provide backup GPS data via USB tethering or network (though each Pi has its own dedicated GPS)
5. **Display Integration**: Acts as an auxiliary navigation display at the nav station
6. **Internet Access**: Optional mobile data connection provides weather, AIS, and chart updates when in cellular coverage
7. **Compact Form Factor**: Small footprint suitable for mounting at nav station without consuming valuable space

### Network Architecture

The phone creates a **WiFi hotspot in Infrastructure Mode** (not Ad-Hoc), acting as both access point and DHCP server:

```
         Pixel 2 Phone Hotspot (192.168.43.1)
         Gateway & DHCP Server
                    |
                    | WiFi (5GHz or 2.4GHz)
                    |
    ┌───────────────┴───────────────┐
    |                               |
RPi Zero W                      RPi 4
Tinypilot                    Lysmarine
192.168.43.101              192.168.43.100
(Autopilot)                 (Navigation)
```

**Key Point**: The autopilot system is **network-independent**. The Pi Zero can operate in Compass and GPS modes even if the phone hotspot fails, as it has a dedicated USB GPS receiver. Network connectivity is only required for:
- Wind mode (receives wind data from Lysmarine via SignalK)
- NAV mode (receives waypoint data from OpenCPN)
- Remote monitoring/control via OpenCPN plugin

## Power Supply Configuration

### DC-DC Buck Converter Modules

The YachtArion system uses **two DC-DC buck converter modules** to provide clean, regulated 5V USB power from the boat's 12V system. These compact switching regulators convert ship's 12V DC (nominal 10-15V range) to stable 5V output suitable for USB devices.

#### Buck Converter Specifications
- **Input Voltage**: 6-35V DC (wide range accommodates voltage fluctuations)
- **Output Voltage**: 5V DC (USB standard)
- **Output Current**: 3A per module (continuous)
- **Efficiency**: ~85-95% (minimal heat generation)
- **Protection**: Over-current, over-temperature, short-circuit
- **Connectors**: Screw terminals (input), dual USB-A ports (output)

### Dual Converter Architecture (Recommended)

**Why Two Converters?**

Using both buck converters provides **redundancy, load distribution, and electrical isolation** for the critical autopilot system:

#### Advantages of Dual-Converter Configuration

1. **Load Distribution**: Splits power demand across two independent supplies, preventing overload
2. **Thermal Management**: Lower load per converter = cooler operation = longer lifespan in marine heat
3. **Redundancy**: If one converter fails, critical autopilot continues on the other
4. **Electrical Isolation**: Separates autopilot circuit from navigation/communication systems, reducing electrical noise coupling
5. **Maintenance Flexibility**: Can service one converter while system remains operational

#### Power Distribution Schema

```
12V Ship's Power Bus (Fused)
         |
         ├─────────────────────────────────┐
         |                                   |
   Buck Converter #1                Buck Converter #2
   (Critical Autopilot)            (Navigation/Comms)
   Input: 12V, 3A fuse             Input: 12V, 5A fuse
   Output: 5V @ 3A                 Output: 5V @ 3A
         |                                   |
         |                                   |
    USB Port 1: Pi Zero W              USB Port 1: Pi 4 (Lysmarine)
    (~500mA, 2.5W)                     (~1.5-3A, 7.5-15W)
         |                                   |
    USB Port 2: Arduino Motor          USB Port 2: Pixel 2 Phone
    Controller                         (~1-2A, 5-10W)
    (~200mA, 1W)
         |
   Total Load: ~3.5W                Total Load: ~15-25W
   (Well under 15W capacity)        (Within 15W capacity)
```

#### Load Analysis

**Buck Converter #1 - Critical Autopilot Circuit**:
- **Raspberry Pi Zero W** (Tinypilot): 500mA @ 5V = 2.5W
- **Arduino Motor Controller**: 100-200mA @ 5V = 0.5-1W
- **Total Maximum Load**: ~3.5W (23% of 15W capacity)
- **Headroom**: 76% (excellent margin for reliability)

**Buck Converter #2 - Navigation & Communications**:
- **Raspberry Pi 4 8GB** (Lysmarine): 1.5A @ 5V = 7.5W (idle), up to 3A = 15W (peak)
- **Google Pixel 2 Phone**: 1-2A @ 5V = 5-10W (charging + hotspot active)
- **Total Maximum Load**: ~20-25W (shared between dual USB ports)
- **Note**: Pi 4 and phone will share 15W capacity, but rarely both peak simultaneously

### Installation and Wiring

#### Mounting Locations

**Buck Converter #1 (Autopilot)**:
- Mount near Pi Zero installation (minimize 5V cable runs)
- Ensure adequate ventilation (though switching regulators run cool)
- Protect from moisture and spray
- Secure with marine-grade adhesive or screws

**Buck Converter #2 (Navigation)**:
- Mount near nav station (accessible for phone connection/disconnection)
- Position for easy USB cable routing to Pi 4 and phone
- Consider waterproof enclosure if exposed location

#### Input Wiring (12V Side)

**For Both Converters**:
```
12V Positive Bus → Inline Fuse → Red Wire → Buck Converter IN+
12V Negative Bus → Black Wire → Buck Converter IN-
```

**Wire Specifications**:
- **Wire Gauge**: 18 AWG or heavier (15A capacity for short runs < 10 feet)
- **Fuse Rating**: 
  - Converter #1 (Autopilot): 3A fast-blow (1.5x load)
  - Converter #2 (Navigation): 5A fast-blow (1.5x load)
- **Fuse Type**: ATO/ATC automotive blade fuse or AGC glass tube
- **Fuse Location**: As close to power source as practical (< 12 inches)

**Installation Steps**:
1. **Power OFF**: Ensure 12V bus is de-energized before wiring
2. **Strip Wire**: 1/4 inch exposed conductor, no fraying
3. **Connect Input**:
   - Positive (red) wire to IN+ screw terminal (tighten securely)
   - Negative (black) wire to IN- screw terminal
4. **Verify Polarity**: Double-check connections (reversed polarity can damage converter)
5. **Install Fuse**: Insert fuse in holder on positive wire
6. **Secure Wiring**: Use cable ties and conduit to protect from chafe

#### Output Wiring (5V USB Side)

**Buck Converter #1 (Autopilot)**:
- **USB Port 1**: Connect micro-USB cable to Raspberry Pi Zero W
  - Cable length: < 3 feet (minimize voltage drop)
  - Cable quality: Use quality cable with 24/28 AWG power/data wires (not cheap thin cables)
- **USB Port 2**: Connect USB cable to Arduino motor controller (if powered via USB)
  - Alternative: Arduino may be powered from Pi Zero 5V pin if current budget allows

**Buck Converter #2 (Navigation)**:
- **USB Port 1**: Connect USB-C cable to Raspberry Pi 4 (via Argon ONE case USB-C port)
  - Use quality USB-C cable rated for 3A
  - Pi 4 official power supply specification: 5V 3A
- **USB Port 2**: Connect USB-C cable to Google Pixel 2 phone
  - Use quality USB-C cable (Pixel 2 standard charging cable)
  - Phone should remain connected for continuous operation

### Alternative Single-Converter Configuration (Not Recommended)

If you choose to use only **one buck converter** for all devices:

**Single Converter Load**:
- Pi Zero W: 2.5W
- Pi 4: 7.5-15W
- Pixel 2: 5-10W
- Arduino: 0.5-1W
- **Total**: 15-28.5W peak (approaching or exceeding 15W capacity)

**Risks of Single-Converter Setup**:
1. **Overload Risk**: Total load can exceed 15W capacity, causing voltage sag or converter shutdown
2. **No Redundancy**: Single point of failure—if converter fails, entire system goes offline
3. **Thermal Stress**: Continuous high load reduces converter lifespan in warm marine environment
4. **Voltage Drop**: Heavy load on single converter can cause voltage sag affecting all devices
5. **No Isolation**: Electrical noise from navigation system can couple into sensitive autopilot circuit

**If Single Converter is Used (Emergency Only)**:
- Monitor converter temperature (should not exceed 60°C)
- Add heatsink to converter if available
- Ensure excellent ventilation
- Limit simultaneous high-power operations (e.g., don't update Pi 4 while phone fast-charging)
- Consider the single converter a temporary solution until second unit is installed

### Voltage and Current Monitoring

#### Verifying Output Voltage

Use a multimeter to verify proper 5V output:

```bash
# Measure voltage at USB port with no load connected
# Should read 5.0-5.2V DC (slightly high is normal for switching regulators)

# Measure voltage at device end of USB cable under load
# Should read 4.8-5.2V DC (some drop is normal due to cable resistance)
```

**Acceptable Voltage Range**:
- **No Load**: 5.0-5.3V (slight overvoltage compensates for cable drop)
- **Under Load**: 4.75-5.25V (USB specification allows ±5%)
- **Undervoltage**: < 4.75V indicates overload or poor connections
- **Overvoltage**: > 5.3V indicates converter malfunction (disconnect immediately)

#### Current Monitoring

**Measure Current Draw** (optional, for diagnostics):

Use a USB power meter (available for ~$10-15 AUD) to monitor:
- Real-time current draw per device
- Voltage sag under load
- Total power consumption (Watts)
- Cumulative energy (mAh, Wh)

**Normal Current Readings**:
- **Pi Zero W**: 200-500mA idle, 500-700mA peak (WiFi active)
- **Pi 4 8GB**: 600-1500mA idle, 2000-3000mA peak (CPU intensive)
- **Pixel 2 Phone**: 500-1500mA charging, 1500-2000mA fast-charging
- **Arduino**: 50-200mA typical

### Troubleshooting Power Issues

#### Converter Won't Output 5V

**Symptoms**: No voltage at USB ports

**Solutions**:
1. Check 12V input voltage is present (measure at converter input terminals)
2. Verify input polarity is correct (IN+ to positive, IN- to negative)
3. Check input fuse is intact (replace if blown)
4. Inspect screw terminals for loose connections
5. Test converter with known-good load (USB desk fan, etc.)
6. Replace converter if faulty

#### Voltage Drop Under Load

**Symptoms**: Devices reboot or undervoltage warnings (Pi 4 shows lightning bolt icon)

**Solutions**:
1. Measure voltage at device end of USB cable (not just at converter output)
2. Replace cheap/thin USB cables with quality cables (24 AWG power wires)
3. Shorten USB cable length (< 3 feet ideal)
4. Reduce load on converter (move devices to second converter)
5. Check for corroded connectors or poor crimps
6. Verify converter output current rating (should be 3A minimum)

#### Converter Overheating

**Symptoms**: Converter feels very hot to touch (> 60°C), or thermal shutdown occurs

**Solutions**:
1. Reduce load (move devices to second converter)
2. Improve ventilation around converter (add fan if necessary)
3. Add heatsink to converter module if available
4. Check for short circuit on output (disconnect all loads and measure)
5. Verify input voltage not too high (> 15V can increase heat)

#### Devices Intermittently Reboot

**Symptoms**: Raspberry Pis or phone randomly reboot, especially under high load

**Solutions**:
1. Check for loose USB connections (reseat all cables)
2. Verify voltage at device remains above 4.75V under load
3. Inspect for corroded or oxidized contacts (clean with contact cleaner)
4. Reduce simultaneous high-power operations (stagger startups)
5. Upgrade to dual-converter configuration for isolation

## Setting Up the YachtArion Hotspot

### Prerequisites

- Google Pixel 2 phone (or compatible Android device)
- DC-DC buck converter with USB outputs (configured per power section above)
- USB-C cable for phone charging
- MicroSD card (optional, for expanded storage)
- Both Raspberry Pis configured with WiFi credentials

### Phone Power Connection

**Continuous Ship's Power (Recommended)**:

1. **Connect USB-C cable** from Buck Converter #2 (Navigation) to Pixel 2 phone
2. Phone will show **"Charging" status** when connected
3. **Do not disconnect** during operation—phone should remain powered at all times
4. Phone's **internal battery acts as UPS** during brief power interruptions

**Power Management Strategy**:
- Phone battery remains charged (90-100%) during normal operation
- During power failure, phone battery provides hotspot for 4-6 hours (depending on usage)
- When ship's power restored, phone automatically resumes charging
- This provides **continuous network availability** even during power cycling

**Battery Longevity Considerations**:
- Keeping phone at 100% charge continuously can reduce battery lifespan
- Modern Android devices use "trickle charging" to minimize degradation
- Pixel 2 battery is replaceable (DIY or repair shop) if capacity degrades
- Typical battery lifespan: 2-3 years of continuous charging in marine environment
- Consider keeping spare phone with fresh battery as backup

### Initial Phone Configuration

#### 1. Factory Reset and Clean Install (Recommended)

For a dedicated marine installation, start with a clean Android install:

1. Backup any important data from the phone
2. Navigate to **Settings → System → Reset Options → Erase All Data (Factory Reset)**
3. Complete initial Android setup wizard
4. Disable unnecessary services to conserve power:
   - **Settings → Apps → See All Apps** → Disable unused apps (Gmail, Photos sync, etc.)
   - **Settings → Display → Sleep** → Set to 30 minutes (or install always-on display app)
   - **Settings → Network & Internet → Data Saver** → Enable (conserves mobile data if SIM installed)

#### 2. Enable Developer Options (Optional but Recommended)

For advanced control and USB debugging:

1. **Settings → About Phone**
2. Tap **Build Number** 7 times to enable Developer Mode
3. **Settings → System → Developer Options**
4. Enable **Stay Awake** (screen stays on when charging—useful for nav station display)
5. Enable **USB Debugging** (allows ADB access for remote configuration)

### Configuring the Hotspot

#### 1. Enable WiFi Hotspot

1. **Settings → Network & Internet → Hotspot & Tethering → WiFi Hotspot**
2. Tap **Turn on WiFi Hotspot**
3. Tap **Set up WiFi Hotspot** to configure:
   - **Network name**: `YachtArion`
   - **Security**: WPA2-PSK (recommended) or WPA3 if supported
   - **Password**: Use a strong password (minimum 8 characters, record securely)
   - **AP Band**: 
     - **5GHz**: Higher speed, less interference, shorter range
     - **2.4GHz**: Better range, better penetration through bulkheads (recommended for boats)
   - **Hidden network**: Leave OFF (clients need to see SSID to connect)

**Recommended Settings for Marine Use**:
- **AP Band**: 2.4GHz (better range and bulkhead penetration)
- **Network name**: `YachtArion` (clear identification)
- **Security**: WPA2-PSK (maximum compatibility)
- **Auto turn off hotspot**: Disable (prevent accidental shutdown)

#### 2. Configure DHCP Reservation (Static IPs)

Most Android hotspots use automatic DHCP assignment, but you can ensure consistent IP addresses through two methods:

**Method A: DHCP Reservation (Advanced, requires root or ADB)**

If your Pixel 2 is rooted or you have ADB access, you can configure static DHCP leases:

```bash
# Via ADB (requires USB debugging enabled)
adb shell
su  # (requires root)

# Edit dnsmasq configuration (if available)
echo "dhcp-host=<Pi_Zero_MAC>,192.168.43.101" >> /data/misc/dhcp/dnsmasq.conf
echo "dhcp-host=<Pi_4_MAC>,192.168.43.100" >> /data/misc/dhcp/dnsmasq.conf

# Restart hotspot
```

**Method B: Static IP on Clients (Recommended, No Root Required)**

Configure static IPs directly on each Raspberry Pi:

**For Tinypilot Pi Zero W** (`/etc/dhcpcd.conf` or network manager config):
```bash
interface wlan0
static ip_address=192.168.43.101/24
static routers=192.168.43.1
static domain_name_servers=192.168.43.1 8.8.8.8
```

**For Lysmarine Pi 4** (via Lysmarine web interface or `/etc/NetworkManager/system-connections/YachtArion`):
```ini
[connection]
id=YachtArion
type=wifi
autoconnect=true

[wifi]
ssid=YachtArion
mode=infrastructure

[wifi-security]
key-mgmt=wpa-psk
psk=your_hotspot_password

[ipv4]
method=manual
address1=192.168.43.100/24,192.168.43.1
dns=192.168.43.1;8.8.8.8;
```

#### 3. Test Connectivity

After configuring both Pis:

1. Boot both Raspberry Pis with hotspot enabled
2. From Lysmarine Pi 4, test connectivity:
   ```bash
   ping 192.168.43.1      # Ping phone gateway
   ping 192.168.43.101    # Ping Tinypilot
   ```
3. From Tinypilot web interface (http://192.168.43.101), verify connection
4. From OpenCPN on Pi 4, test pypilot plugin connection to 192.168.43.101:20220

### Making YachtArion Network Available to Other Devices

The YachtArion hotspot can be extended to other instruments and crew devices:

#### Connecting Additional Devices

**Tablets and Phones** (crew devices for monitoring):
1. Device WiFi settings → Select "YachtArion"
2. Enter hotspot password
3. Access Lysmarine web interface: `http://192.168.43.100`
4. Access Tinypilot web interface: `http://192.168.43.101`
5. Access SignalK: `http://192.168.43.100:3000`

**Marine Instruments with WiFi** (AIS receivers, wind sensors, etc.):
1. Configure instrument to connect to SSID "YachtArion"
2. Set static IP in 192.168.43.x range (avoid .1, .100, .101)
3. Configure instrument to send data to:
   - SignalK: `192.168.43.100:3000` (WebSocket or TCP)
   - NMEA TCP: `192.168.43.100:10110` (if supported)

**Recommended IP Allocation**:
- `192.168.43.1` - Pixel 2 phone (gateway)
- `192.168.43.100` - Lysmarine Pi 4 (navigation)
- `192.168.43.101` - Tinypilot Pi Zero W (autopilot)
- `192.168.43.102-109` - Crew tablets/phones (DHCP pool)
- `192.168.43.110-119` - Marine instruments (AIS, wind, depth, etc.)
- `192.168.43.120-199` - Reserved for future expansion

#### Network Security Considerations

For a production installation:

1. **Change default hotspot password** to a strong passphrase (16+ characters)
2. **Disable WPS** if available (potential security vulnerability)
3. **Disable UPnP** on phone hotspot (not typically available, but check if rooted)
4. **Consider MAC filtering** for critical instruments (if phone supports it)
5. **Regular password rotation** (every 6-12 months or when crew changes)

## Assigning the Phone a Fixed IP Address

### Internal Hotspot IP

The phone's **internal hotspot IP is fixed by Android** at:
- **192.168.43.1** (Pixel phones and most Android devices)
- Some manufacturers use 192.168.49.1 or 192.168.137.1

To verify your phone's hotspot IP:
```bash
# From a connected device (e.g., Lysmarine Pi 4)
ip route show default
# Output: default via 192.168.43.1 dev wlan0
```

This IP is **not configurable** without root access or custom ROMs.

### External Network IP (SIM Card Connection)

If you add a SIM card (see next section), the phone will have **two IP addresses**:
1. **Hotspot LAN IP**: 192.168.43.1 (internal network)
2. **Cellular WAN IP**: Assigned by mobile carrier (external internet)

The cellular IP is typically **dynamic** (changes each connection) unless you subscribe to a static IP service from your carrier.

## Adding a Mobile SIM Card

### Benefits of Cellular Data

Adding a SIM card to the Pixel 2 enables:

1. **Weather Data**: GRIB files, weather forecasts, storm warnings
2. **Chart Updates**: Download updated charts and notices to mariners
3. **AIS Data**: Shore-based AIS aggregators (e.g., MarineTraffic, VesselFinder)
4. **Email & Messaging**: Ship-to-shore communication
5. **Software Updates**: Update pypilot, OpenCPN, and system packages remotely
6. **Remote Monitoring**: Access boat systems via VPN or dynamic DNS

### SIM Card Selection for Marine Use

**Recommended Carrier Features**:
- **Strong coastal coverage** (check coverage maps for Australian coast)
- **Reasonable data plans** (2-10GB/month typical for marine use)
- **No hard data caps** (throttling acceptable, hard cutoffs problematic)
- **International roaming** (if cruising outside Australian waters)

**Australian Carrier Options**:
- **Telstra**: Best coastal coverage, more expensive
- **Optus**: Good coastal coverage, mid-range pricing
- **Vodafone**: Limited coastal coverage outside major cities
- **Aldi Mobile** (Telstra network): Budget option with good coverage

**Typical Data Usage**:
- GRIB weather files: 50-200KB each (multiple times per day)
- Chart updates: 1-500MB per region (infrequent)
- AIS data streaming: 10-50MB per day
- Email/messaging: 1-10MB per day
- Software updates: 50-500MB (infrequent)
- **Estimated monthly use**: 1-5GB typical, 10GB for frequent updates

### SIM Card Installation

1. **Power off phone** before inserting SIM
2. Locate **SIM tray** on side of Pixel 2 (use ejection tool)
3. Insert **nano-SIM** (Pixel 2 uses nano-SIM format)
4. Power on phone and verify carrier connection
5. **Settings → Network & Internet → Mobile Network**
6. Configure APN if required by carrier (usually automatic)

### Hotspot Behavior with SIM Card

When SIM card is active, the phone acts as a **NAT router**:

```
Internet (Cellular Network)
          ↓
   Pixel 2 Phone
   - WAN IP: x.x.x.x (carrier assigned)
   - LAN IP: 192.168.43.1
   - NAT enabled
          ↓
   YachtArion WiFi Network
   192.168.43.0/24
          ↓
   Connected Devices
   (Pis, tablets, instruments)
```

**Key Implications**:

1. **Internet Access**: All devices on YachtArion network can access internet via NAT
2. **Data Usage**: **All client traffic counts toward phone's data plan**
3. **Speed Limitations**: Cellular speed shared among all connected devices
4. **Inbound Connections**: External internet cannot directly reach devices on 192.168.43.x without port forwarding
5. **Carrier NAT**: Most mobile carriers use CGNAT (Carrier-Grade NAT), preventing inbound connections even with port forwarding

### Data Management with SIM Card

#### 1. Enable Data Saver Mode
**Settings → Network & Internet → Data Saver → Use Data Saver**
- Restricts background data usage
- Apps must explicitly request network access
- Reduces unexpected data consumption

#### 2. Limit Hotspot Data Usage
**Settings → Network & Internet → Hotspot & Tethering → WiFi Hotspot → Advanced → Hotspot Data Limit**
- Set monthly limit (e.g., 5GB)
- Automatic shutdown when limit reached (useful for cost control)

#### 3. Configure Per-Device Data Priorities

On each Raspberry Pi, configure bandwidth priority:

**For Lysmarine Pi 4** (heavy user: charts, weather, updates):
```bash
# Disable automatic updates over metered connections
sudo systemctl stop unattended-upgrades
sudo systemctl disable unattended-upgrades

# Configure apt to avoid large downloads
sudo nano /etc/apt/apt.conf.d/02periodic
# Set: APT::Periodic::Update-Package-Lists "0";
```

**For Tinypilot Pi Zero** (minimal user: autopilot only):
- No configuration needed—Tinypilot uses minimal bandwidth
- Optional: Block internet access entirely via firewall to prevent updates

#### 4. Schedule Updates for Marina WiFi

Configure devices to **only update when connected to specific SSIDs**:

```bash
# On Lysmarine Pi 4, create connection-specific profile
sudo nmcli connection modify YachtArion ipv4.route-metric 200
sudo nmcli connection modify Marina_WiFi ipv4.route-metric 100
# Lower metric = preferred connection, updates will use Marina WiFi when available
```

### Monitoring Data Usage

#### On Phone
**Settings → Network & Internet → Mobile Network → App Data Usage**
- View per-app data consumption
- Set warnings and limits
- Reset statistics monthly

#### On Raspberry Pi
```bash
# Install vnstat for bandwidth monitoring
sudo apt-get install vnstat
vnstat -i wlan0  # View network statistics
vnstat -m        # View monthly totals
```

#### Via Lysmarine Web Interface
SignalK and Lysmarine provide network statistics dashboards for monitoring real-time usage.

## Phone Display as Nav Station Component

The Pixel 2's OLED screen provides an excellent auxiliary display for navigation data:

### Mounting Solutions

**Option 1: RAM Mount**
- Use **RAM X-Grip** phone holder with marine base
- Mount at eye level on nav station bulkhead
- Allows adjustment for glare reduction
- Easy removal for maintenance

**Option 2: Fixed Panel Mount**
- Install in blank instrument panel cutout
- Use foam gasket for moisture seal
- Secure with machine screws through case
- Professional appearance, permanent installation

**Option 3: Swing Arm Mount**
- Articulating arm allows position adjustment
- Useful if phone needs to be shared between helm and nav station
- Requires strong mounting point due to lever forces

### Recommended Android Apps for Marine Use

#### Navigation and Charts

**OpenCPN for Android** (already installed)
- Full-featured chartplotter with plugin support
- Sync charts via SD card or network from Lysmarine
- Backup navigation if Lysmarine fails
- **Use case**: Emergency navigation if main Pi 4 fails

**qtVlm** (optional)
- Tactical sailing navigation and weather routing
- GRIB file visualization
- Polar diagram integration
- **Use case**: Passage planning and weather strategy

#### Pypilot and Autopilot Control

**Pypilot App for Android** (highly recommended)
- Direct control of autopilot from phone
- Change modes (Compass, GPS, Wind, NAV)
- Adjust heading and tack/jibe commands
- Monitor rudder angle and motor current
- **Install from**: https://pypilot.org (APK available)
- **Connection**: Configure to 192.168.43.101:20220

**OpenCPN Pypilot Plugin** (via OpenCPN Android)
- Control autopilot within OpenCPN interface
- Integrated with route planning
- **Use case**: Integrated navigation and autopilot control

#### Marine Data Display

**WilhelmSK** (SignalK client for Android)
- Real-time marine instrument display
- Customizable dashboards
- Displays data from SignalK server on Lysmarine
- **Connection**: Configure to 192.168.43.100:3000
- **Use case**: Instrument panel replacement, tactical sailing data

**SignalK Instrument Panel** (web-based)
- Access via phone browser: `http://192.168.43.100:3000`
- Customizable gauges (wind, speed, depth, heading)
- Responsive design works well on phone screens
- **Use case**: No app installation required, universal access

#### Weather and Forecasting

**PredictWind** (subscription service)
- Marine weather forecasts optimized for passage planning
- GRIB file downloads
- Offshore weather routing
- **Use case**: Passage planning, heavy weather avoidance

**Windy** (free, excellent UI)
- Visual weather maps with wind, waves, temperature
- Satellite imagery and radar
- Excellent for near-coastal and offshore forecasting
- **Use case**: Quick visual weather checks, storm tracking

**BOM Weather** (Australian Bureau of Meteorology)
- Official Australian marine forecasts
- Coastal warnings and storm alerts
- Free, authoritative source
- **Use case**: Australian coastal waters primary forecast source

#### AIS and Traffic

**Marine Traffic** (freemium)
- Real-time AIS data from shore stations
- Vessel identification and tracking
- Requires cellular data
- **Use case**: Busy shipping lanes, port approaches

**Boat Beacon** (AIS transmitter app)
- Broadcasts phone GPS position as AIS target
- Useful for small craft visibility
- Requires cellular data or VHF AIS
- **Use case**: Safety in shipping lanes (not a replacement for physical AIS)

#### System Monitoring and Remote Access

**Termux** (terminal emulator)
- Full Linux terminal on Android
- SSH client for accessing Raspberry Pis
- Python, vim, git support
- **Use case**: Emergency system administration from phone

**JuiceSSH** (SSH client)
- User-friendly SSH terminal
- Saved connections and port forwarding
- **Configure profiles**:
  - Tinypilot: `ssh pi@192.168.43.101`
  - Lysmarine: `ssh pi@192.168.43.100`
- **Use case**: System monitoring, log checks, troubleshooting

**VNC Viewer** (remote desktop)
- Graphical access to Raspberry Pi desktops
- **Configure connections**:
  - Lysmarine: `192.168.43.100:5900` (VNC server must be enabled)
  - Tinypilot: Typically headless (web interface only)
- **Use case**: Full GUI access to OpenCPN and system settings

#### Offline Documentation

**Kiwix** (offline Wikipedia and docs)
- Download marine, navigation, and technical documentation
- Works without internet connectivity
- **Recommended content**:
  - Wikipedia (marine, navigation, weather)
  - OpenCPN manual
  - Pypilot documentation
- **Use case**: Offshore reference material

#### Power and Battery Management

**AccuBattery** (battery health monitoring)
- Tracks charge cycles and battery degradation
- Alerts for overcharging
- **Use case**: Maximize battery lifespan in marine environment

**Tasker** (automation, advanced)
- Automate hotspot startup on power connection
- Auto-enable airplane mode in specific locations
- Custom battery management rules
- **Use case**: Hands-free operation, power optimization

### Display Configuration for Nav Station Use

#### 1. Enable Always-On Display
**Settings → Display → Advanced → Ambient Display**
- Shows critical info (time, notifications) without unlocking
- Low power consumption on OLED screen

Or install **Always On AMOLED** app for more customization

#### 2. Adjust Brightness for Marine Environment
**Settings → Display → Brightness Level**
- Set **Adaptive Brightness** ON (auto-adjusts for day/night)
- Configure **Night Light** (red-shift for night vision preservation)
- **Settings → Display → Night Light** → Schedule from sunset to sunrise

#### 3. Disable Screen Timeout When Charging
**Settings → System → Developer Options → Stay Awake**
- Screen remains on when connected to power
- Essential for continuous nav station display

#### 4. Configure Lock Screen for Quick Access
**Settings → Security → Lock Screen**
- Set **Smart Lock** → Trusted Places (home dock) for auto-unlock
- Configure **Lock Screen Shortcuts** for OpenCPN and pypilot app
- **Use case**: Quick access without unlocking

#### 5. Reduce Distractions
**Settings → Sound → Do Not Disturb**
- Enable DND mode automatically during night hours
- Disable notification sounds (visual only)
- **Use case**: Reduce disruption during night watch

## Backup Network Configuration

For redundancy, configure secondary WiFi networks on both Raspberry Pis:

### Marina and Home WiFi

**On Tinypilot Pi Zero** (`/etc/wpa_supplicant/wpa_supplicant.conf`):
```bash
country=AU
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

# Primary: YachtArion hotspot
network={
    ssid="YachtArion"
    psk="your_hotspot_password"
    priority=10
    id_str="yacht_primary"
}

# Secondary: Home/marina WiFi for updates
network={
    ssid="Cygnet_Marina_WiFi"
    psk="marina_password"
    priority=5
    id_str="marina"
}

network={
    ssid="Home_WiFi"
    psk="home_password"
    priority=3
    id_str="home"
}
```

**Priority system**:
- Higher priority = preferred connection
- YachtArion (10) connects first if available
- Falls back to marina/home WiFi for updates

**On Lysmarine Pi 4** (via NetworkManager web UI):
- Add multiple connection profiles
- Set YachtArion as default
- Configure marina/home networks for updates and remote access

### Cellular Backup (Future Consideration)

For extended offshore cruising, consider adding a **4G USB modem** to Lysmarine Pi 4:
- Provides internet when phone battery depleted
- Independent backup communication path
- Recommended: Huawei E3372 or similar marine-rated USB modem

## Troubleshooting

### Hotspot Won't Start

**Symptoms**: "Hotspot error" or immediate shutdown after enabling

**Solutions**:
1. Disable Bluetooth (can conflict on some Android versions)
2. Restart phone
3. Check carrier restrictions (some plans disable hotspot)
4. Clear cache: **Settings → Apps → See All Apps → Hotspot → Storage → Clear Cache**

### Devices Can't Connect

**Symptoms**: Clients see YachtArion SSID but can't authenticate

**Solutions**:
1. Verify password entry (case-sensitive)
2. Check maximum device limit (some phones limit to 5-10 clients)
3. Try 2.4GHz band instead of 5GHz (better compatibility)
4. Disable MAC filtering if enabled
5. Restart hotspot on phone

### Intermittent Disconnections

**Symptoms**: Clients randomly lose connection to YachtArion

**Solutions**:
1. Check phone battery level (hotspot may throttle when low battery)
2. Ensure phone is adequately powered (use 2A+ USB charger)
3. Reduce number of connected devices (bandwidth congestion)
4. Check for WiFi interference (change channel if possible)
5. Verify phone isn't overheating (reduce screen brightness, improve ventilation)

### No Internet Access (with SIM Card)

**Symptoms**: Connected to YachtArion but no internet on clients

**Solutions**:
1. Check cellular signal strength on phone
2. Verify mobile data is enabled: **Settings → Network & Internet → Mobile Network**
3. Check APN settings (carrier-specific)
4. Verify data plan is active (not exceeded quota)
5. Toggle airplane mode on/off to reset cellular connection

### High Data Usage

**Symptoms**: Unexpected cellular data consumption

**Solutions**:
1. Check per-app usage: **Settings → Network & Internet → Mobile Network → App Data Usage**
2. Enable Data Saver mode
3. Disable automatic updates on Raspberry Pis
4. Check for background app sync (disable unnecessary apps)
5. Verify no malware/rogue apps running

### Poor Hotspot Range

**Symptoms**: Weak signal at helm or other boat locations

**Solutions**:
1. Reposition phone higher or more centrally
2. Switch to 2.4GHz band (better range than 5GHz)
3. Add USB-powered WiFi repeater (marine-rated)
4. Upgrade to external marine WiFi access point (future)
5. Check for interference from metal structures (reposition away from bulkheads)

## Maintenance and Best Practices

### Regular Maintenance Schedule

**Weekly (at sea)**:
- Check hotspot is active and devices connected
- Monitor phone battery health
- Review data usage if SIM card active
- Verify buck converters not overheating (touch test < 60°C)

**Monthly (in port)**:
- Restart phone to clear memory
- Update Android OS and apps
- Clean phone case and screen
- Verify backup WiFi connections work
- Inspect USB cables and connectors for corrosion
- Check buck converter screw terminals for tightness

**Annually**:
- Factory reset phone for clean install (backup first)
- Replace phone if battery degraded (< 80% health)
- Update WiFi credentials (password rotation)
- Replace USB cables showing wear or corrosion
- Clean buck converter contacts with electrical contact cleaner

### Power Management

**Best Practices for Marine Environment**:

1. **Constant 12V USB Power**: Keep phone connected to ship's power via buck converter (2.4A+ output)
2. **Avoid Deep Discharge**: Keep battery above 20% even when on ship's power (battery longevity)
3. **Temperature Control**: Ensure adequate ventilation—OLED screens and batteries degrade faster in heat
4. **Backup Battery**: Phone's internal battery acts as UPS during power interruptions
5. **Solar Charging**: Buck converters work excellently with solar charge controllers (12V input)

**Buck Converter Maintenance**:
- Inspect screw terminals quarterly for looseness
- Keep converters dry (waterproof enclosure if in exposed location)
- Ensure adequate air circulation (don't enclose tightly)
- Monitor temperature during high load operations
- Replace converters if output voltage drifts outside 4.75-5.25V range

### Security Hardening

**For Long-Term Marine Deployment**:

1. **Disable Unused Services**:
   - Bluetooth (unless needed for instruments)
   - NFC
   - Location services (unless using phone GPS)
2. **Encrypt Device**: **Settings → Security → Encrypt Phone**
3. **Regular Password Updates**: Change hotspot password every 6-12 months
4. **Firewall Configuration** (requires root): Install AFWall+ or similar to restrict per-app network access
5. **VPN for Remote Access** (if SIM installed): Use WireGuard or OpenVPN for secure remote monitoring

### Backup and Recovery

**Critical Data to Backup**:
1. Hotspot configuration (SSID, password)
2. Installed app list and APKs
3. OpenCPN Android charts and settings
4. WiFi connection credentials

**Backup Methods**:
- **Android Backup**: **Settings → System → Backup** (to Google account)
- **Manual Backup**: ADB pull of critical files
- **App-Specific**: OpenCPN chart export, Pypilot app settings

**Recovery Plan**:
- Keep second phone with identical configuration (hot spare)
- Store backup phone in waterproof dry bag
- Document all network settings in ship's log
- Keep written record of IP addresses and passwords
- **Spare buck converter**: Keep one spare converter onboard for emergency replacement

## Future Enhancements

### Hardware Upgrades

**WiFi 6 Access Point**: Replace phone with dedicated marine WiFi 6 router for:
- Better range and bulkhead penetration
- More simultaneous clients (MU-MIMO)
- Lower latency for real-time data
- PoE power delivery (simplify wiring)

**4G/5G Router**: Dedicated marine cellular router with:
- External antenna (better signal in offshore conditions)
- Dual SIM (carrier redundancy)
- Gigabit Ethernet for hardwired critical systems
- DIN rail mounting for electrical panel integration

**Starlink Maritime**: For extended offshore cruising:
- High-bandwidth satellite internet
- Global coverage (beyond cellular range)
- Requires significant power (75-150W) and mounting structure
- Expensive but enables full internet access anywhere

### Software Enhancements

**Network Monitoring Dashboard**: Install Grafana on Lysmarine for:
- Real-time bandwidth usage graphs
- Device connection status
- Data plan usage tracking
- Historical network performance

**Automatic Failover**: Configure systemd scripts to:
- Auto-detect hotspot failure
- Switch to backup WiFi (marina/home)
- Alert crew via notification

**Remote VPN Access**: Configure WireGuard VPN for:
- Secure access to boat systems from shore
- Remote monitoring of autopilot status
- Download logs and diagnostics
- Requires static IP or dynamic DNS service

---

## Summary

The Google Pixel 2 hotspot provides a reliable, low-cost, and power-efficient networking solution for YachtArion's pypilot system. Key advantages include:

- **Dedicated marine network** with stable IP addressing
- **Built-in battery backup** for continuous operation during power interruptions
- **Optional internet access** via SIM card for weather, charts, and updates
- **Integrated display** for auxiliary navigation and instrument monitoring
- **Low maintenance** with familiar Android interface
- **Dual buck converter power** for redundancy and electrical isolation

**Remember**: The autopilot is network-independent—compass and GPS modes work without any WiFi connectivity. The hotspot enhances functionality but is not critical for safe autopilot operation.

For questions or improvements to this documentation, please open an issue at https://github.com/botheredbybees/pypilot4arion

---

**Document Version**: 1.1  
**Last Updated**: January 19, 2026  
**Maintainer**: botheredbybees  
**Vessel**: SY Arion
