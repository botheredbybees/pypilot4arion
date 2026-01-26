# EZR23 Router Setup for Pypilot4arion

This document describes the configuration of the EZR23 4G LTE router as the primary network gateway for the Arion pypilot system. The EZR23 replaces the phone-based hotspot (Pixel 2) providing dedicated, reliable connectivity with 12V marine-compatible power and high-gain antenna support.

## Overview

The EZR23 is a 4G LTE Cat.4 router designed for outdoor/marine applications. It runs directly on 9-48V DC power with typical consumption of 24W at 12V (2A). This router provides:

- **Dual-SIM support** with automatic failover for carrier redundancy
- **High-gain WiFi booster** (27dBm covering 100-200 yards)
- **Replaceable SMA antennas** for optimal marine 4G signal
- **Dedicated continuous operation** without phone battery/overheating concerns
- **12V native power** compatible with boat supply

## Quick Installation Steps

1. Connect antennas: Mobile SMA connectors (4G), WiFi SMA connectors (Wi-Fi)
2. Insert SIM card(s) into slot(s); SIM1 used as primary
3. Connect 12V power (via 5A fused marine-grade wiring)
4. Connect device (phone/laptop) to EZR23 at `192.168.20.1`
5. Configure 4G settings (APN, PIN, network modes)
6. Assign mobile interface to WAN firewall zone
7. Set up static DHCP leases for pypilot devices
8. Verify connectivity via router status page

## Router Login and Addressing

```bash
# Access router admin interface via browser
# Default credentials (check router label):
URL: http://192.168.20.1
Username: admin
Password: admin  # (or per manufacturer label)
```

### Default Network Settings

- **Router IP**: `192.168.20.1` (Gateway)
- **Subnet Mask**: `255.255.255.0` (/24)
- **DHCP Server**: Enabled (default range `192.168.20.50-150`)
- **WiFi SSID**: Default `EZR23-XXXX` (change to `YachtArion`)

**Important**: The LAN/WiFi subnet (`192.168.20.x`) differs from boat WiFi relays.

## Configuration Steps

### 1. Access Router Admin Interface

```bash
# Connect to EZR23 via WiFi or Ethernet, then open:
firefox http://192.168.20.1
```

Navigate to the status and configuration pages via tabs.

### 2. Configure Mobile (4G) Interface

Navigate to: `Network > Interfaces > Mobile (wwan0)`

**Note the following settings:**

| Setting | Description | Notes |
| :--- | :--- | :--- |
| **Active SIM** | Select SIM1 or SIM2 | SIM1 = primary |
| **Auto Switch** | Enable for dual-SIM failover | Automatic failover to other SIM if network drops |

**Mobile Modem Settings** (Network > Mobile > Mobile Modem):

| Setting | Recommended Value | Notes |
| :--- | :--- | :--- |
| **Protocol** | LTE/4G preferred | |
| **APN** | `telstra.internet` | For Telstra (Tasmania primary carrier) |
| **APN** (Optus) | `internet` | If using Optus as backup |
| **Username/Password** | Leave blank | Not required for Australian carriers |
| **Network Mode** | Set to supported modes for carrier | Default recommended |
| **Supported Bands** | Default | Compatible with carrier bands |

#### APN Settings for Tasmania Carriers

**Telstra** (Recommended - best coverage):
- **APN**: `telstra.internet`
- **Username**: (blank)
- **Password**: (blank)
- **Authentication**: None or PAP

**Optus** (Good urban coverage):
- **APN**: `internet`
- **Username**: (blank)
- **Password**: (blank)
- **Authentication**: None

**Vodafone** (Limited rural coverage):
- **APN**: `live.vodafone.com`
- **Proxy**: `010.202.002.060`
- **Port**: `8080`
- **Username**: (blank)
- **Password**: (blank)

### 3. Assign Mobile Interface to WAN Firewall Zone

**CRITICAL STEP**: The mobile interface must be assigned to the WAN zone for proper routing.

Navigate to: `Network > Interfaces > Mobile > Firewall Settings`

1. Find the **"Assign firewall zone"** dropdown
2. Select **"wan"** from the options (NOT "lan" or "guest")
3. Click **"Save & Apply"**

**Why WAN Zone?**
- The mobile/4G interface is your internet uplink (Wide Area Network)
- WAN zone provides NAT routing from your LAN (192.168.20.x) to the internet
- Firewall protection blocks unsolicited incoming traffic from the internet
- Allows your pypilot devices to access the internet while staying protected

**Traffic Flow**:
```
Internet (4G) <-> [WAN Zone] <-> Router Firewall/NAT <-> [LAN Zone] <-> Your Devices
```

### 4. Configure Wi-Fi

Navigate to: `Network > Wireless`

- Set SSID to `YachtArion` (consistent with existing docs)
- Set WPA2 or WPA3-PSK password (e.g., `StrongP@ss!123`)
- Set Transmit Power to High (100mW) for boat coverage
- Select a channel (e.g., 6 or 11) avoiding local interference

**Note**: The Wi-Fi hotspot defaults to the router's subnet (`192.168.20.x`).

### 5. Configure Static DHCP Leases for Pypilot Devices

**Important**: This ensures your Raspberry Pis always get the same IP addresses.

#### Step 5.1: View Active DHCP Leases

1. Navigate to: **Network > DHCP and DNS**
2. **Scroll down** on the page to find the **"Active DHCP Leases"** table
3. Note the MAC addresses of your devices:
   - Look for hostnames like `raspberrypi`, `lysmarine`, or `tinypilot`
   - MAC addresses starting with `b8:27:eb:` (older Pi), `dc:a6:32:`, or `e4:5f:01:` (Pi 4)

**Example Active Leases Table**:

| Hostname | IPv4 Address | MAC Address | Lease Time |
| :--- | :--- | :--- | :--- |
| raspberrypi | 192.168.20.52 | b8:27:eb:xx:xx:xx | 11h 45m |
| raspberrypi | 192.168.20.53 | dc:a6:32:yy:yy:yy | 11h 50m |

**Write down the MAC addresses** - you'll need them in the next step.

#### Step 5.2: Create Static Leases

1. On the same **Network > DHCP and DNS** page, **scroll further down** to the **"Static Leases"** section
2. Click the **"Add"** button
3. Fill in the details for each device:

**For Lysmarine (Pi 4)**:
- **Hostname**: `lysmarine`
- **MAC Address**: `dc:a6:32:yy:yy:yy` (from Active Leases table)
- **IPv4 Address**: `192.168.20.100`
- **Lease Time**: (leave blank - uses default)

4. Click **"Save & Apply"**
5. Click **"Add"** again for the next device

**For TinyPilot (Pi Zero)**:
- **Hostname**: `tinypilot`
- **MAC Address**: `b8:27:eb:xx:xx:xx` (from Active Leases table)
- **IPv4 Address**: `192.168.20.101`
- **Lease Time**: (leave blank)

6. Click **"Save & Apply"**

#### Step 5.3: Apply and Verify

1. Reboot both Raspberry Pis or disconnect/reconnect from WiFi
2. Check the **Active DHCP Leases** table again
3. Verify that your devices now show their assigned static IPs:
   - `lysmarine` at `192.168.20.100`
   - `tinypilot` at `192.168.20.101`

**From a Raspberry Pi, verify**:
```bash
ip addr show wlan0
# Should show 192.168.20.100 or 192.168.20.101

ping 192.168.20.1
# Should successfully ping the router

ping 192.168.20.100
ping 192.168.20.101
# Should ping between the Pis
```

### 6. Confirm DHCP Settings

Navigate to: `Network > DHCP and DNS`

- Ensure DHCP is enabled
- Confirm the dynamic pool (e.g., `192.168.20.50` to `192.168.20.150`)
- Your static leases (100, 101) are outside the dynamic pool range

### 7. Monitor Signal

Navigate to the router status page; observe:

- **RSRP**: Primary signal strength (LTE) - aim for > -100 dBm
- **RSRQ**: Signal quality - higher is better
- **RSSI**: Combined power (2G/3G indicator)

Adjust antenna placement and orientation for best RSRP.

## Recommended Static IPs for Pypilot Devices

With the EZR23 subnet (`192.168.20.x`), the following IPs are configured:

| Device | IP Address | MAC Address | Role |
| :--- | :--- | :--- | :--- |
| **EZR23 Router** | `192.168.20.1` | (Check router label) | Gateway / 4G Internet / AP |
| **Lysmarine** | `192.168.20.100` | (Set via static lease) | Navigation / OpenCPN / Signal K |
| **TinyPilot** | `192.168.20.101` | (Set via static lease) | Autopilot Core / Motor Control |
| **User Laptop**| DHCP (50-150) | - | Configuration / Monitoring |
| **Tablet/Phone**| DHCP (50-150) | - | Remote Display |

Note: Update the network documentation (`network_map.md`) to reflect these addresses.

## Routing and Internet Access

### 4G Internet via Mobile Interface

The router's default routing will send traffic destined for external networks via the Mobile interface (wwan0). The mobile connection obtains an external IPv4. You may verify this under `Network > Interfaces > Mobile`.

### Dual-SIM Failover Policy

Set (Network > Mobile > Mobile Modem > SIM Card Slot > Auto Switch):

| Setting | Description |
| :--- | :--- |
| **Auto Switch** | Enable to allow automatic failover between SIMs |
| **Primary SIM** | SIM1 (preferred - Telstra recommended) |
| **Switch Criteria** | Loss of network registration or inability to bring up link |

The router will try to recover the link on the current SIM before switching.

### IPv4 Routing and Default Gateway

- Internal LAN: `192.168.20.0/24`
- Router's internal IP: `192.168.20.1` (gateway for LAN hosts)
- Mobile interface IPv4: Assigned by your ISP (shown under Network > Interfaces)

All hosts configured with `gateway=192.168.20.1` will route external traffic via the Mobile interface.

**Note**: Ensure your 4G provider supports outbound data and does not block necessary ports.

## Common Routing Issues and Solutions

### Issue 1: No 4G Internet Connection

**Symptoms**: Devices connect to WiFi but have no internet access; router status shows no mobile IP assignment.

**Troubleshooting**:

1. Check SIM insertion and SIM carrier coverage in the area
2. Confirm APN settings match your 4G provider:
   - Telstra: `telstra.internet`
   - Optus: `internet`
3. **Verify mobile interface is assigned to WAN zone** (Network > Interfaces > Mobile > Firewall Settings)
4. Test the SIM in a phone at the location
5. Under Network > Interfaces > Mobile, click `Stop` then `Connect` to re-establish link
6. Ensure the correct Mobile mode/bands are selected for your carrier

### Issue 2: WiFi Relay Subnet Conflicts

**Symptoms**: Cannot connect to external WiFi networks routed via EZR23 due to overlapping IP ranges.

**Cause**: The EZR23 LAN interface (`192.168.20.x`) must be on a different subnet from any WiFi relay network to which you connect.

**Solution**: 

- Verify the EZR23 internal subnet under Network > DHCP (default `192.168.20.0/24`)
- Ensure your WiFi relay network uses a different range (e.g., `192.168.1.x` instead of `192.168.20.x`)

Example: EZR23 IP is `192.168.20.1`; WiFi relay network must not use `192.168.20.x`.

### Issue 3: Frequent SIM Failover or Drops

**Symptoms**: Router switches SIMs frequently; unstable mobile connection.

**Solutions**:

1. Optimize antenna placement for stronger RSRP (aim for > -100 dBm)
2. Under Mobile Modem, increase the number of failed attempts before switching (if adjustable)
3. If both SIMs are on the same carrier, check for local network congestion
4. Test SIM cards separately to identify the stronger carrier in your sailing area
5. Consider Telstra as primary for best Tasmania offshore coverage

### Issue 4: Devices Can't Access Local Services

**Symptoms**: You can ping `192.168.20.100` and `192.168.20.101`, but Signal K or pypilot web UI isn't reachable.

**Solutions**:

1. Ensure the correct ports are not blocked or filtered:
   - Signal K Admin: `3000`
   - Pypilot Web: `80`
   - Pypilot Control API: `20220`
   - SSH: `22`
   - VNC: `5900`
2. Disable any third-party firewall services on the hosts themselves
3. Confirm services are running on Lysmarine and TinyPilot
4. Access services locally via Ethernet to isolate a potential Wi-Fi issue

### Issue 5: DNS Resolution Problems

**Symptoms**: Devices obtain IP but can't resolve hostnames; only IPs work.

**Solutions**:

1. Verify DNS settings under Network > DHCP and DNS; use reliable public DNS:
   - Primary: `8.8.8.8` (Google)
   - Secondary: `1.1.1.1` (Cloudflare)
2. Check that DNS traffic isn't filtered by the router firewall
3. Test DNS resolution from hosts: `nslookup example.com`

### Issue 6: Static Leases Not Working

**Symptoms**: Devices still get different IPs despite static lease configuration.

**Solutions**:

1. Verify MAC addresses are correct in static lease table
2. Ensure static IP addresses (100, 101) are **outside** the DHCP dynamic pool range
3. Clear old leases: reboot the router or wait for existing leases to expire
4. On the Raspberry Pi, force DHCP renewal:
   ```bash
   sudo dhclient -r wlan0
   sudo dhclient wlan0
   ```
5. Check that you configured leases in **Network > DHCP and DNS > Static Leases**, not elsewhere

## Power Wiring for Marine Use

**Important**: Use proper marine-grade wiring and protection:

1. Connect the EZR23 to the boat's 12V bus using at least 18 AWG cabling
2. Install a 5A (or larger) fuse as close to the 12V source as practical
3. Ensure all connections are weather-resistant and corrosion-protected
4. Consider a marine DC-DC converter if input voltage may exceed 14.4V continuously
5. Verify proper grounding of the router case/connectors per manufacturer guidelines

## Signal K and Pypilot Port Forwarding (Optional)

If you need to access vessel services from the internet (not recommended for security), configure NAT/port forwarding under the router firewall:

| Service | Internal (LAN) | External (WAN) |
| :--- | :--- | :--- |
| Pypilot Web | `192.168.20.101:80` | `[Mobile IP]:80` |
| Signal K | `192.168.20.100:3000` | `[Mobile IP]:3000` |

**Warning**: Port forwarding exposes internal services to the internet. Consider VPNs and strong authentication if required.

## Maintenance and Monitoring

1. Periodically check RSRP/RSRQ in router status to ensure antenna placement optimal
2. Verify dual-SIM failover works when offshore by pulling one SIM's antenna
3. Monitor data usage via router interface; many carriers have offshore/data limits
4. Keep firmware updated to benefit from performance and security patches
5. Document any custom APN, PIN, or firewall settings
6. Review active DHCP leases periodically to ensure static assignments are working

## Quick Reference: Tasmania APN Settings

| Carrier | APN | Username | Password | Coverage |
| :--- | :--- | :--- | :--- | :--- |
| **Telstra** | `telstra.internet` | (blank) | (blank) | Best offshore/rural |
| **Optus** | `internet` | (blank) | (blank) | Good urban |
| **Vodafone** | `live.vodafone.com` | (blank) | (blank) | Limited rural |

**Recommendation**: Use Telstra as SIM1 (primary) for best coverage in Tasmanian waters.

## References

- [EZR23 Quick Guidance PDF](https://www.outdoorrouter.com/wp-content/uploads/EZR23T-4G-LTE-Router-Quick-Guidance_v1.02-Web.pdf)
- [EZR23 Documentation](https://indoor.router.works/ezr23)
- [Network Interfaces (EZR23T)](https://ezr23t.router.works/firmware/network-interfaces)
- [Mobile Modem (EZR23T)](https://ezr23t.router.works/firmware/mobile-modem)
- [WiFi Hotspot (EZR23)](https://indoor.router.works/ezr23/configuration/wi-fi-hotspot)
- [Router Status (EZR23)](https://indoor.router.works/ezr23/configuration/router-status)
- [DHCP Configuration (EZR3X)](https://www.outdoorrouter.com/news/ezr3x-dhcp-ip-configuration/)
- [Pypilot User Manual](https://pypilot.org/doc/pypilot_user_manual/pdf/pypilot_user_manual.pdf)
- Router-specific guides (from manufacturer or outdoorrouter.com)
