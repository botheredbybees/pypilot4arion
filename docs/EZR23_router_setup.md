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
6. Verify connectivity via router status page

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

| Setting | Recommended Value |
| :--- | :--- |
| **Protocol** | LTE/4G preferred |
| **APN** | Carrier-specific (e.g., `telstra.internet`) |
| **Network Mode** | Set to supported modes for carrier; default recommended |
| **Supported Bands** | Default (compatible with carrier bands) |

### 3. Configure Wi-Fi

Navigate to: `Network > Wireless`

- Set SSID to `YachtArion` (consistent with existing docs)
- Set WPA2 or WPA3-PSK password (e.g., `StrongP@ss!123`)
- Set Transmit Power to High (100mW) for boat coverage
- Select a channel (e.g., 6 or 11) avoiding local interference

**Note**: The Wi-Fi hotspot defaults to the router's subnet (`192.168.20.x`).

### 4. Confirm DHCP Settings

Navigate to: `Network > DHCP` (or `Status > DHCP`)

- Ensure DHCP is enabled
- Set the pool (e.g., `192.168.20.50` to `192.168.20.150`)

### 5. Monitor Signal

Navigate to the router status page; observe:

- **RSRP**: Primary signal strength (LTE)
- **RSRQ**: Signal quality
- **RSSI**: Combined power (2G/3G indicator)

- Adjust antenna placement and orientation for best RSRP.

## Recommended Static IPs for Pypilot Devices

With the EZR23 subnet (`192.168.20.x`), reserve static IPs via DHCP or configure via router's host table:

| Device | IP Address | MAC Address (use actual) | Role |
| :--- | :--- | :--- | :--- |
| **EZR23 Router** | `192.168.20.1` | `[From Router]` | Gateway / 4G Internet / AP |
| **Lysmarine** | `192.168.20.100` | `[Pi 4 MAC]` | Navigation / OpenCPN / Signal K |
| **TinyPilot** | `192.168.20.101` | `[Pi Zero MAC]` | Autopilot Core / Motor Control |
| **User Laptop**| DHCP | - | Configuration / Monitoring |
| **Tablet/Phone**| DHCP | - | Remote Display |

Note: Update the network documentation (`network_map.md`) to reflect these addresses.

## Routing and Internet Access

### 4G Internet via Mobile Interface

The router's default routing will send traffic destined for external networks via the Mobile interface (wwan0). The mobile connection obtains an external IPv4. You may verify this under `Network > Interfaces > Mobile`.

### Dual-SIM Failover Policy

Set (Network > Mobile > Mobile Modem > SIM Card Slot > Auto Switch):

| Setting | Description |
| :--- | :--- |
| **Auto Switch** | Enable to allow automatic failover between SIMs |
| **Primary SIM** | SIM1 (preferred) |
| **Switch Criteria** | Loss of network registration or inability to bring up link |

The router will try to recover the link on the current SIM before switching.

### IPv4 Routing and Default Gateway

- Internal LAN: `192.168.20.0/24`
- Router’s internal IP: `192.168.20.1` (gateway for LAN hosts)
- Mobile interface IPv4: Assigned by your ISP (shown under Network > Interfaces)

All hosts configured with `gateway=192.168.20.1` will route external traffic via the Mobile interface.

**Note**: Ensure your 4G provider supports outbound data and does not block necessary ports.

## Common Routing Issues and Solutions

### Issue 1 No 4G Internet Connection

**Symptoms**: Devices connect to WiFi but have no internet access; router status shows no mobile IP assignment.

**Troubleshooting**:

1. Check SIM insertion and SIM carrier coverage in the area
2. Confirm APN settings match your 4G provider (consult carrier documentation)
3. Test the SIM in a phone at the location
4. Under Network > Interfaces > Mobile, click `Stop` then `Connect` to re-establish link
5. Ensure the correct Mobile mode/bands are selected for your carrier

### Issue 2 WiFi Relay Subnet Conflicts

**Symptoms**: Cannot connect to external WiFi networks routed via EZR23 due to overlapping IP ranges.

**Cause**: The EZR23 LAN interface (`192.168.20.x`) must be on a different subnet from any WiFi relay network to which you connect.

**Solution**: 

- Verify the EZR23 internal subnet under Network > DHCP (default `192.168.20.0/24`);
- Ensure your WiFi relay network uses a different range (e.g., `192.168.1.x` instead of `192.168.20.x`).

Example: EZR23 IP is `192.168.20.1`; WiFi relay network must not use `192.168.20.x`.

### Issue 3 Frequent SIM Failover or Drops

**Symptoms**: Router switches SIMs frequently; unstable mobile connection.

**Solutions**:

1. Optimize antenna placement for stronger RSRP
2. Under Mobile Modem, increase the number of failed attempts before switching (if adjustable)
3. If both SIMs are on the same carrier, check for local network congestion
4. Test SIM cards separately to identify the stronger carrier in your sailing area

### Issue 4 Devices Can’t Access Local Services

**Symptoms**: You can ping `192.168.20.100` and `192.168.20.101`, but Signal K or pypilot web UI isn’t reachable.

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

### Issue 5 DNS Resolution Problems

**Symptoms**: Devices obtain IP but can’t resolve hostnames; only IPs work.

**Solutions**:

1. Verify DNS settings under the router’s DHCP settings; use reliable public DNS (e.g., `8.8.8.8`, `1.1.1.1`) if carrier DNS is unreliable
2. Check that DNS traffic isn’t filtered by the router firewall
3. Test DNS resolution from hosts (`nslookup example.com`)

## Power Wiring for Marine Use

**Important**: Use proper marine-grade wiring and protection:

1. Connect the EZR23 to the boat’s 12V bus using at least 18 AWG cabling
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
2. Verify dual-SIM failover works when offshore by pulling one SIM’s antenna
3. Monitor data usage via router interface; many carriers have offshore/data limits
4. Keep firmware updated to benefit from performance and security patches
5. Document any custom APN, PIN, or firewall settings

## References

- [EZR23 Quick Guidance PDF](https://www.outdoorrouter.com/wp-content/uploads/EZR23T-4G-LTE-Router-Quick-Guidance_v1.02-Web.pdf)
- [EZR23 Documentation](https://indoor.router.works/ezr23)
- [Network Interfaces (EZR23T)](https://ezr23t.router.works/firmware/network-interfaces)
- [Mobile Modem (EZR23T)](https://ezr23t.router.works/firmware/mobile-modem)
- [WiFi Hotspot (EZR23)](https://indoor.router.works/ezr23/configuration/wi-fi-hotspot)
- [Router Status (EZR23)](https://indoor.router.works/ezr23/configuration/router-status)
- [Pypilot User Manual](https://pypilot.org/doc/pypilot_user_manual/pdf/pypilot_user_manual.pdf)
- Router-specific guides (from manufacturer or outdoorrouter.com)
