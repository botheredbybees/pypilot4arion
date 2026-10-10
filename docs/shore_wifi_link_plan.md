# Shore Wi-Fi link plan (Bullet M2 HP + Wavlink)

Status: **planned, not started** (written 2026-10-10). The whole stack is currently on the desk at home (lab supply 12.7 V); test everything there before mounting anything.

## Goal

Give the boat a reliable internet link from the home network while moored, and free the EZR23's radio from repeater duty.

Today the EZR23 uses its single Wi-Fi radio both as a client of the home `flow` network and as the `YachtArion` access point. That halves throughput and locks both networks to the same channel.

## Target layout

```
home router ──LAN── 24V PoE injector ──outdoor cable── Bullet M2 HP (AP, SSID "flow-dock")
                                                              )))  2.4 GHz  (((
boat 12V ── PoE injector ──outdoor cable── Wavlink (client) ──Ethernet── EZR23 WAN port
                                                                            │
                                               EZR23 Wi-Fi: YachtArion only (Pis, phones)
                                               EZR23 4G: backup when shore link is down
```

Unit choice: the Wavlink is 24 V passive PoE, while the Bullet M2 HP accepts **10.5-24 V passive PoE** and could run from boat 12 V directly. The Wavlink still suits the boat better: its two omni antennas cope with the boat swinging on its mooring, and the Bullet's directional antenna belongs on the fixed shore end. The cost is a small 12->24 V step-up converter on board.

## What we learned on 2026-10-10

- The EZR23's **"PoE & LAN" port is PoE input** (an alternative way to power the router). It does **not** supply power, which is why neither unit lit up when plugged into it.
- The Wavlink is a **WL-WN570HA1 Rev A1**. Factory defaults from its label: `192.168.10.1` (or `http://wifi.wavlink.com`), user/password `admin`/`admin`. It has a single `WAN/LAN (PoE)` port, plus a ground screw for a lightning/earth lead. The clip-on block under it is its **passive PoE injector**: a DC barrel jack and a blue RJ45 for data. Its power brick is marked **24 V**, so it is **24 V passive PoE**, not 802.3af. Confirmed 2026-10-10.
- **Passive PoE warning:** an injector's **POE** port always carries voltage. Plug it only into the Bullet or the Wavlink, never into the router, a Pi or a laptop. The injector's **LAN** port is the safe data-only end.

## Step 0: Power each unit on the desk

1. Bullet: its own 24 V injector, **POE** port to the Bullet, injector to the mains. It should light up within seconds.
2. Wavlink: same, with its own adapter.
3. For setup, run a cable from the injector's **LAN** port to a laptop.

## Step 1: Shore side (Bullet M2 HP, airOS)

1. Default address `192.168.1.20`, user `ubnt`, password `ubnt`. Give the laptop a static `192.168.1.50/24` and browse to `https://192.168.1.20`. **Change the password** immediately (store it in `.env`, not in this repo).
2. **Network tab:** mode **Bridge**, IP by DHCP. If the home LAN is also `192.168.1.x`, set the IP before connecting the Bullet to it, so `.20` doesn't clash.
3. **Wireless tab:**
   - Wireless mode: **Access Point**
   - **airMAX: off.** With it on, only Ubiquiti gear can connect.
   - SSID: **`flow-dock`**, never `flow`. The hub has an autoconnecting `flow` NetworkManager profile and could jump onto a second "flow" and drop off the boat LAN.
   - Security: WPA2-AES. Channel width: 20 MHz. Channel: 1, 6 or 11, whichever the home router isn't using.
   - Country: **Australia** (keeps the high-power radio plus antenna within legal EIRP).
4. Connect the injector's LAN port to the home router.
5. Later: mount it high, with line of sight to the boat, and aim the antenna at the mooring. Seal the RJ45 boot with self-amalgamating tape. Use outdoor-rated (ideally shielded) cable.

## Step 2: Boat side (Wavlink)

1. **Power from 12 V:** keep the Wavlink's own clip-on injector. Feed its barrel jack from a **12->24 V DC-DC step-up converter** (at least 1 A output, potted/waterproof type) instead of the mains brick.
   - Before buying, check the barrel plug size on the brick (most likely 5.5 x 2.1 mm, centre positive) and its current rating.
   - Fuse close to the 12 V tap (2 A).
   - For the desk test, just use the 24 V mains brick. Don't change the lab supply, which is powering the stack.
2. Log in at `192.168.10.1` (laptop static `192.168.10.50/24`, cable to the blue RJ45 on the injector). **Change the admin password** (store it in `.env`).
3. Configure it as a **client of `flow-dock`** on its **2.4 GHz** radio (the Bullet M2 is 2.4 GHz only). The mode is called WISP, Client or Repeater, depending on firmware.
   - Preferred: **client-bridge**, so the EZR23 gets its address straight from the home router.
   - If WISP/router mode: its own subnet must not be `192.168.20.x` (boat) or the home range. Use e.g. `192.168.50.x`.
4. Cable: Wavlink (via the injector's LAN port) to the **EZR23 WAN** port.

## Step 3: EZR23

1. Network -> Interfaces: WAN (Ethernet) = **DHCP client**, firewall zone **wan** (same as the mobile interface).
2. Prefer the shore link: WAN metric lower than mobile (e.g. WAN 10, mobile 20), or mwan3/failover if available. 4G becomes the backup.
3. Remove the repeater/client connection to `flow` from the router's radio, so the radio serves only `YachtArion`. Pick a `YachtArion` channel away from `flow-dock`.

## Step 4: Verify (Claude can do this from the hub)

- Hub route goes hub -> `192.168.20.1` -> Wavlink -> home router (`traceroute 1.1.1.1`).
- All three Pis stay on `YachtArion` (.100/.101/.102 reachable). Tailscale stays up.
- Unplug the Wavlink: the EZR23 fails over to 4G. Plug it back: it returns to the shore link.
- Signal K, Grafana and the pypilot links are unaffected (check `$source` timestamps).

## Still needed

- Distance from house to boat and line of sight.
- Bullet antenna type (directional or omni).
- Hardware to buy: 12->24 V step-up converter with the right barrel plug, outdoor-rated Ethernet cable, inline fuse holder.
- After it works: update `EZR23_router_setup.md` and `network_map.md`, and consider deleting the hub's `flow` NetworkManager profile.
