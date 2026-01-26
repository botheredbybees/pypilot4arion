# EZR23 4G Router Setup

This document describes how to configure the EZR23 4G LTE router for use on Arion with the pypilot/autopilot and OpenPlotter stack.

The goals are:
- Provide a stable onboard Wi‑Fi/LAN for pypilot, OpenPlotter, and other devices
- Use a 4G Nano‑SIM for internet backhaul when in range
- Avoid routing conflicts between the routers LAN (192.168.20.0/24 by default) and any existing boat networks

## 1. Physical installation

1. Power the EZR23 from the 12 V house bank via a fused feed (2–3 A fuse is adequate for the 12 V / 2 A adapter rating).[page:0]
2. Connect the supplied 4G and Wi‑Fi SMA antennas. Use extension leads and/or mast/cockpit mounts if you later want better reception.[page:1]
3. Insert your Nano‑SIM into SIM1 (use SIM2 only if you intend to configure fail‑over).
4. Connect your Raspberry Pi / OpenPlotter box either:
   - By Ethernet to the EZR23 LAN port, or
   - By Wi‑Fi as a client to the routers SSID.

## 2. Initial access to the web UI

The factory default settings are:[page:0]
- Router LAN IP: `192.168.20.1`
- Subnet: `192.168.20.0/24`
- Login user: `root`

Steps:

1. Connect a laptop to the router by Ethernet or Wi‑Fi.
2. Manually set the laptop IP to something like `192.168.20.10/24` if DHCP is not yet active.
3. Browse to `http://192.168.20.1` and log in as `root` (set your own strong password immediately after first login).

## 3. Configure the LAN for the boat network

Decide whether the EZR23 will be the **primary router** on board or just a 4G uplink feeding an existing LAN. The simplest arrangement for pypilot is to treat the EZR23 as the boats main router and put the Raspberry Pi and other devices directly on its LAN.

Recommended basic LAN setup:

1. In the LAN / Network section, keep the default LAN subnet unless it conflicts with another network you routinely connect to (e.g. marinas that also use `192.168.20.0/24`).
   - If you already use another subnet on the boat (e.g. `192.168.1.0/24` on an existing router), either migrate to `192.168.20.0/24` **or** change the EZR23 LAN IP/subnet to match your existing plan (e.g. set LAN IP to `192.168.10.1`, mask `255.255.255.0`).
2. Ensure the DHCP server is enabled on the LAN and configured with a sensible pool, e.g. `192.168.20.100–192.168.20.199`.
3. Reserve static DHCP leases for key devices (optional but handy):
   - Raspberry Pi / OpenPlotter (e.g. `192.168.20.10`)
   - Any other fixed instruments or bridges.

Routing table notes:

- If the EZR23 is your only router, you normally **do not** need to change its routing table: it will default‑route all traffic from the LAN out via the 4G modem.
- If you have another router on board and want the EZR23 only as a 4G uplink, avoid having *two* devices doing NAT/DHCP on the same segment. Either:
  - Put the second router in bridge/AP mode so the EZR23 is the only gateway, **or**
  - Put the EZR23 on a different subnet (e.g. WAN of your existing router) and let that router do the NAT for the boat.

## 4. Configure the 4G SIM and APN

1. In the Mobile / WAN section, select SIM1 as active.
2. Enter your carrier APN details, typically provided by the provider when you activated the data SIM (e.g. `telstra.internet`, `optus.internet`, etc.).
3. Authentication: set to `PAP`/`CHAP` or `none` as required by the carrier; many Australian consumer SIMs use APN only (no username/password).
4. Set connection mode to `auto` or `always on` so the router will reconnect automatically after power cycles.
5. (Optional) Configure SIM2 with a different carrier and enable fail‑over if supported in the WAN policy page.

Routing table / CGNAT considerations:

- Most 4G providers use carrier‑grade NAT (CGNAT). You will get a private IP on the WAN side and cannot accept unsolicited inbound connections from the internet; for this project you generally only need outbound access (software updates, telemetry, remote support via reverse tunnel, etc.), which works fine under CGNAT.
- If you intend to reach the boat from shore directly (SSH/VNC into the Raspberry Pi), you will need either a VPN client running on the Pi or a provider that offers public IPv4/IPv6 with appropriate port‑forwarding. That configuration is beyond this document.

## 5. Integrate with pypilot / OpenPlotter

On the Raspberry Pi/OpenPlotter host:

1. Ensure the Pi either:
   - Uses Ethernet directly to the EZR23 and obtains an IP via DHCP, or
   - Connects as a Wi‑Fi client to the routers SSID.
2. Verify network:

```bash
ping 192.168.20.1        # router
ping 8.8.8.8             # internet reachability
ping pypilot.local       # if using mDNS/avahi
```

3. In pypilot / OpenPlotter, confirm that the web UI, NMEA 0183/2000 gateways, and any Signal K services bind on the Pis LAN address (e.g. `192.168.20.10`). Typically this is automatic as long as the interface is up.

You do **not** normally need any custom static routes for pypilot: everything remains on the local LAN, and the default route on the Pi points to the EZR23 for outbound internet.

## 6. Common routing and DNS issues

### Symptom: Internet works on laptop but not on Raspberry Pi

- Check that the Pi received a valid IP, subnet mask, gateway, and DNS from the router:

```bash
ip addr
ip route
cat /etc/resolv.conf
```

- The default route should point at `192.168.20.1` (or whatever you configured as the LAN IP).
- If DNS fails but pinging `8.8.8.8` works, set explicit DNS servers (e.g. `1.1.1.1`, `8.8.8.8`) in the routers LAN DHCP options.

### Symptom: Cant reach the router UI

- Make sure your device is on the same subnet. If you changed the LAN IP, adjust your static address or reconnect to obtain a fresh DHCP lease.
- Check for IP conflicts if you have another router present. Only one device on a given LAN should use `192.168.20.1`.

### Symptom: Two routers both handing out DHCP

- Either disable DHCP on one of them or split into two subnets (e.g. `192.168.20.0/24` on EZR23, `192.168.30.0/24` on a secondary router used only as an access point/bridge).

## 7. Security hardening

1. Change the default `root` password immediately.
2. Consider creating a non‑root admin user if supported, and disabling remote administration from the 4G (WAN) side so the web UI is only reachable from the LAN.
3. Use a strong Wi‑Fi passphrase and WPA2/WPA3 (as supported).
4. Optionally, create a dedicated Wi‑Fi SSID for navigation/autopilot gear and a separate SSID/VLAN for guest devices.

## 8. Notes specific to this project

- The routers job in this project is to provide a reliable IP backbone and 4G uplink; pypilot and your hydraulic steering hardware are entirely local to the boat network.
- Keep the router and antennas in a reasonably dry, ventilated area below decks, but avoid full Faraday cages (solid metal enclosures) that would attenuate RF.
- Once this is working, you can add remote logging, backups, or a control tunnel from shore, but the basic autopilot does not depend on 4G being up; it only needs local LAN/Wi‑Fi.
