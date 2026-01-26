# Network & Data Topology Map

## Physical Network
*   **SSID**: `YachtArion`
*   **Gateway / AP**: EZR23 4G Router (192.168.20.1)
*   **Subnet Mask**: 255.255.255.0 (/24)
*   **DHCP Range**: 192.168.20.50 - 192.168.20.150
*   **Internet Access**: Dual-SIM 4G LTE with automatic failover
*   **WiFi Coverage**: ~100-200 yards (27dBm high-gain)

## Static IP Allocations

| Device | IP Address | Configuration Method | Role |
| :--- | :--- | :--- | :--- |
| **EZR23 Router** | `192.168.20.1` | Router default | Gateway / DHCP Server / 4G Internet / WiFi AP |
| **Lysmarine** | `192.168.20.100` | Static on Pi | Navigation / OpenCPN / Signal K Server |
| **TinyPilot** | `192.168.20.101` | Static on Pi | Autopilot Core / Motor Control |
| **User Laptop**| DHCP (50-150) | DHCP | Configuration / Monitoring |
| **Tablet/Phone**| DHCP (50-150) | DHCP | Remote Display / Control |

**Note**: Static IPs are configured directly on each Raspberry Pi for easier hardware replacement in marine environments. If a board fails, a replacement can be configured with the same IP without router changes.

## Service Ports

| Service | Port | Host | Address | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Router Admin** | `80` | EZR23 | `http://192.168.20.1` | Router configuration interface |
| **Signal K Admin** | `3000` | Lysmarine | `http://192.168.20.100:3000` | Sensor Dashboard & Config |
| **OpenCPN** | `None` | Lysmarine | Local display only | Navigation/Charting Software |
| **Pypilot Web** | `80` | TinyPilot | `http://192.168.20.101` | Autopilot Web UI |
| **Pypilot Control**| `20220` | TinyPilot | `192.168.20.101:20220` | JSON Control API (OpenCPN Plugin) |
| **SSH** | `22` | Both Pis | `ssh pi@192.168.20.10x` | Remote Command Line |
| **VNC** | `5900` | Lysmarine | `192.168.20.100:5900` | Remote Desktop to Chartplotter |

## Router Configuration

### Power
- **Input Voltage**: 9-48V DC (12V nominal)
- **Current Draw**: ~2A at 12V (24W typical)
- **Protection**: 5A fuse on positive lead from House Bus A
- **Wire Gauge**: Minimum 18 AWG / 0.75mm²

### Mobile Interface (4G)
- **Primary SIM**: Slot 1 (configured with carrier APN)
- **Secondary SIM**: Slot 2 (optional backup/failover)
- **Failover**: Automatic on network loss
- **Expected Coverage**: Check RSRP/RSRQ in router status page

### Antennas
- **Mobile (4G)**: 2x SMA connectors for external LTE antennas
- **WiFi**: 2x SMA connectors for high-gain WiFi antennas
- **Recommendation**: Mount 4G antennas as high as practical for best signal

## Power Distribution for Network Devices

All devices powered from **House Bus A** via individual fused circuits:

| Device | Input Voltage | Buck Converter | Fuse Size | Wire Gauge |
| :--- | :--- | :--- | :--- | :--- |
| **EZR23 Router** | 12V (native) | None | 5A | 18 AWG |
| **Lysmarine Pi 4** | 5V | 12V→5V Buck | 2A | 18 AWG |
| **TinyPilot Pi Zero** | 5V | 12V→5V Buck | 1A | 18 AWG |
| **Arduino Motor Controller** | 5V | 12V→5V Buck | 2A | 18 AWG |
| **Rudder Feedback (if separate)** | 5V/12V | As required | 1A | 18 AWG |

**Note**: All negative/ground connections share common negative bus bonded to engine ground.

## Signal Flow

```mermaid
graph TD
    subgraph Internet
        Mobile[4G Mobile Network<br/>Dual-SIM Failover]
    end
    
    subgraph Router
        EZR23[EZR23 4G Router<br/>192.168.20.1<br/>WiFi AP + Gateway]
    end
    
    subgraph Sensors
        WS80[Ecowit WS80 Wind] -.->|433MHz| RTL[RTL-SDR USB]
        GPS[GPS Antenna] -->|USB/Serial| Lysmarine
    end
    
    subgraph Computing
        RTL -->|USB| Lysmarine[Lysmarine Pi 4<br/>192.168.20.100<br/>Static IP]
        Lysmarine -->|rtl_433| SK[Signal K Server<br/>Port 3000]
        SK -->|WiFi JSON| TP[TinyPilot Pi Zero<br/>192.168.20.101<br/>Static IP]
        TP -->|I2C| IMU[IMU Sensor<br/>MPU-9250/BNO055]
    end
    
    subgraph Control
        TP -->|UART/PWM| IBT2[IBT-2 Motor Controller<br/>BTS7960B H-Bridge]
        IBT2 -->|12V High Amp| Pump[Octopus 1012<br/>Hydraulic Pump]
        Pump -->|Pressure| Steering[Hydraulic Steering Ram]
    end
    
    subgraph Users
        Laptop[Laptop<br/>DHCP] -->|WiFi| EZR23
        Tablet[Tablet/Phone<br/>DHCP] -->|WiFi| EZR23
    end
    
    Mobile <-->|4G LTE| EZR23
    EZR23 -->|WiFi 192.168.20.x| Lysmarine
    EZR23 -->|WiFi 192.168.20.x| TP
    
    Laptop -.->|Control| SK
    Tablet -.->|Control| SK
    Laptop -.->|Control| TP
    Tablet -.->|Control| TP
```

## Network Configuration Steps

### 1. Configure Router (see docs/EZR23_router_setup.md)

```bash
# Access router at default address
http://192.168.20.1

# Configure:
# - WiFi SSID: YachtArion
# - WiFi Password: [Strong password]
# - Mobile APN: [Carrier specific - telstra.internet for Telstra]
# - DHCP range: 192.168.20.50-150 (excludes .100 and .101)
# - Assign mobile interface to WAN firewall zone
```

### 2. Configure Static IPs on Raspberry Pis

**Important**: Static IPs are configured on the Pis themselves (not DHCP reservations) for easier hardware replacement. This allows you to swap a failed Pi with a pre-configured replacement without touching router settings.

#### Lysmarine (192.168.20.100)

**Using nmcli (NetworkManager - recommended)**:
```bash
# SSH into Lysmarine Pi
ssh pi@192.168.20.x  # Initially will have DHCP address

# Configure static IP on YachtArion WiFi connection
sudo nmcli con mod "YachtArion" ipv4.addresses 192.168.20.100/24
sudo nmcli con mod "YachtArion" ipv4.gateway 192.168.20.1
sudo nmcli con mod "YachtArion" ipv4.dns "8.8.8.8 1.1.1.1"
sudo nmcli con mod "YachtArion" ipv4.method manual
sudo nmcli con up "YachtArion"

# Verify configuration
ip addr show wlan0
ping 192.168.20.1
```

**Alternative: Edit dhcpcd.conf (for Raspberry Pi OS Lite)**:
```bash
sudo nano /etc/dhcpcd.conf

# Add at the end:
interface wlan0
static ip_address=192.168.20.100/24
static routers=192.168.20.1
static domain_name_servers=8.8.8.8 1.1.1.1

# Save and restart
sudo systemctl restart dhcpcd
```

#### TinyPilot (192.168.20.101)

**Using nmcli**:
```bash
# SSH into TinyPilot Pi
ssh pi@192.168.20.x  # Initially will have DHCP address

# Configure static IP
sudo nmcli con mod "YachtArion" ipv4.addresses 192.168.20.101/24
sudo nmcli con mod "YachtArion" ipv4.gateway 192.168.20.1
sudo nmcli con mod "YachtArion" ipv4.dns "8.8.8.8 1.1.1.1"
sudo nmcli con mod "YachtArion" ipv4.method manual
sudo nmcli con up "YachtArion"

# Verify
ip addr show wlan0
ping 192.168.20.1
ping 192.168.20.100  # Test connectivity to Lysmarine
```

**Alternative: Edit dhcpcd.conf**:
```bash
sudo nano /etc/dhcpcd.conf

# Add at the end:
interface wlan0
static ip_address=192.168.20.101/24
static routers=192.168.20.1
static domain_name_servers=8.8.8.8 1.1.1.1

# Save and restart
sudo systemctl restart dhcpcd
```

### 3. Verify Connectivity

```bash
# From either Pi, test local network
ping 192.168.20.1          # Router
ping 192.168.20.100        # Lysmarine
ping 192.168.20.101        # TinyPilot

# Test internet via 4G
ping 8.8.8.8
ping google.com

# Check routing table
ip route show
# Should show: default via 192.168.20.1 dev wlan0

# Verify DNS resolution
nslookup google.com
```

### 4. Configure Signal K Connections

In Signal K Admin (`http://192.168.20.100:3000`):

- Add pypilot connection:
  - **Protocol**: TCP
  - **Host**: `192.168.20.101`
  - **Port**: `20220`

### 5. Configure OpenCPN Pypilot Plugin

In OpenCPN pypilot plugin settings:

- **Host**: `192.168.20.101`
- **Port**: `20220`

## Hardware Replacement Procedure

**Advantage of Static IP Configuration**: When a Pi fails at sea, you can swap it with a spare that has been pre-configured with the same IP address. No router access needed.

### Preparing Spare Pis

1. Image SD cards with base OS (Lysmarine or Raspberry Pi OS)
2. Boot each spare and configure its static IP as shown above
3. Label SD cards clearly: "Lysmarine Spare - .100" or "TinyPilot Spare - .101"
4. Store spares in waterproof case with documentation

### Swapping a Failed Pi

1. Power down the failed Pi
2. Remove SD card and replace with pre-configured spare
3. Power up - it will immediately acquire the correct IP address
4. No router configuration changes needed
5. Services (Signal K, pypilot) will be reachable at same addresses

**Note**: Keep backup images of working SD cards for creating new spares.

## Troubleshooting

### Cannot Access Router

```bash
# Check WiFi connection
iwconfig
nmcli dev status

# If connected but no access, check IP:
ip addr show wlan0
# Should show 192.168.20.100 or .101

# Try pinging gateway
ping 192.168.20.1
```

### Pis Cannot See Each Other

```bash
# Check IP configuration on both
ip addr show wlan0

# Verify both have correct IPs:
# Lysmarine: 192.168.20.100
# TinyPilot: 192.168.20.101

# Check routing table
ip route

# Test connectivity
ping 192.168.20.100  # From TinyPilot
ping 192.168.20.101  # From Lysmarine
```

### Static IP Not Applied After Reboot

```bash
# Check if configuration persisted
nmcli con show "YachtArion" | grep ipv4

# Or check dhcpcd.conf
cat /etc/dhcpcd.conf | grep -A 5 "interface wlan0"

# Re-apply if needed (see configuration steps above)
```

### IP Conflict Warning

**Symptoms**: Router or devices report duplicate IP address.

**Cause**: Static IPs (.100, .101) overlap with DHCP range.

**Solution**: Ensure router DHCP range is `192.168.20.50-150` which excludes .100 and .101.

### No Internet via 4G

```bash
# Verify gateway is reachable
ping 192.168.20.1

# Check if router has internet
# (Access router web interface at http://192.168.20.1)

# Verify DNS is working
nslookup google.com

# Check routing
ip route show
# Must show: default via 192.168.20.1
```

### Signal K Cannot Connect to Pypilot

```bash
# From Lysmarine, test pypilot port
telnet 192.168.20.101 20220

# If connection refused, check pypilot is running:
ssh pi@192.168.20.101
sudo systemctl status pypilot

# Check pypilot is listening on correct interface:
sudo netstat -tlnp | grep 20220
# Should show: 0.0.0.0:20220 or 192.168.20.101:20220
```

## Security Considerations

### Router Access
- Change default admin password immediately
- Disable remote management from WAN if enabled
- Keep router firmware updated

### Pi Security
- Change default `pi` user password on both Pis
- Enable SSH key authentication
- Consider disabling password authentication for SSH (after keys configured)
- Keep OS and pypilot software updated
- Document passwords in secure location (boat safe)

### WiFi Security
- Use WPA2 or WPA3 encryption
- Use strong WiFi password (minimum 16 characters)
- Disable WPS if enabled
- Document WiFi password for crew
- Consider hiding SSID broadcast when not actively cruising

## Maintenance

### Regular Checks
- Monitor router 4G signal strength (RSRP/RSRQ)
- Check data usage if on metered plan
- Verify dual-SIM failover functionality before extended passages
- Test backup connectivity options
- Verify spare Pi SD cards boot correctly

### Before Extended Passages
- Test all network connections
- Verify internet access via 4G
- Confirm Signal K receiving pypilot data
- Check antenna connections are secure
- Test hardware replacement procedure with spares
- Document current configuration

### Backup Connectivity
- Keep Pixel 2 as backup hotspot (different subnet: 192.168.43.x)
- Document alternate APN settings for different carriers
- Consider satellite backup for offshore passages
- Carry spare SIM cards for both carriers

## Configuration Backup

### Router Configuration
- Export router config via admin interface (System > Backup/Restore)
- Store backup file in repository or secure cloud storage
- Document APN settings, WiFi password, and any custom firewall rules

### Raspberry Pi Configuration
- Create SD card images of working systems:
  ```bash
  # From another Linux system with SD card
  sudo dd if=/dev/sdX of=lysmarine-backup-YYYYMMDD.img bs=4M status=progress
  sudo dd if=/dev/sdX of=tinypilot-backup-YYYYMMDD.img bs=4M status=progress
  ```
- Store images on external drive
- Document all configuration changes in this repository

## References

- [EZR23 Router Setup](./EZR23_router_setup.md) - Detailed router configuration
- [Pypilot User Manual](https://pypilot.org/doc/pypilot_user_manual/)
- [Signal K Documentation](https://signalk.org/)
- [12V Solar System](./12v_solar_system.md) - Power system details
- [Raspberry Pi Network Configuration](https://www.raspberrypi.org/documentation/configuration/wireless/)
