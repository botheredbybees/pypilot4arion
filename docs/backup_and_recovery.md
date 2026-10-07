# Backup & Disaster Recovery Strategy

## Philosophy
The SD cards in your Raspberry Pis are the most fragile component of the system. They **will** fail eventually due to write-wear or power corruption. A verified backup image is the only way to recover quickly.

## What to Backup
1.  **Pypilot Config** (Steering node `arionpypilot`, 192.168.20.100): The tuning gains and calibration.
    *   *Path*: `/home/bbb/.pypilot/pypilot.conf`
2.  **Signal K config** (Hub `lysmarine`, 192.168.20.101): `/home/signalk/.signalk/settings.json` (provider and source-priority setup; timestamped `.bak-*` copies exist beside it, restore one and restart `signalk` to revert a change).
3.  **OpenCPN config** (Hub): `/home/user/.opencpn/opencpn.conf`. OpenCPN runs as the desktop user `user`, not `bbb`, and rewrites its conf on exit, so copy or edit it only while OpenCPN is closed.
4.  **Full SD Images**:
    *   Steering Pi 3B (`arionpypilot`)
    *   Wind bridge Pi Zero WX (`arion-wx`): read-only overlayroot; it holds no logs or changing data, so one image of the card is enough.
    *   The Hub (Pi 4) root is on a USB SATA SSD, not an SD card; image that SSD if a full backup is wanted.

> The hub's Lysmarine-installed local pypilot (`pypilot@pypilot.service`, `pypilot_web.service`) must stay **disabled** after any restore or reinstall; the real pypilot is on the Steering node.

## Backup Procedure

### Method A: Config Text Backup (Fast)
Do this after every successful tuning session.
1.  Connect to the Steering Pi via SSH (`ssh bbb@192.168.20.100`).
2.  Copy the config content:
    ```bash
    cat .pypilot/pypilot.conf
    ```
3.  Save this text to a file on your laptop (e.g., `Arion_Pypilot_Backup_2026.conf`).

### Method B: Full SD Card Image (Complete)
Do this annually or after major changes.

**On Linux/Mac:**
1.  Shutdown Pi and remove SD card. Insert into laptop.
2.  Identify drive (e.g., `/dev/sdb`). **Be careful!**
3.  Read image:
    ```bash
    sudo dd if=/dev/sdb of=~/arion_backups/steering_pi_backup_date.img bs=4M status=progress
    ```

**On Windows:**
1.  Use **Win32DiskImager**.
2.  Select Device letter.
3.  Click "Read" to save to an `.img` file.

## Recovery Procedure (Flashing)

If a card fails:
1.  Get a **New** SD card (High Endurance preferred, SanDisk Max Endurance).
2.  Use **BalenaEtcher**.
3.  Select your backup `.img` file.
4.  Flash to the new card.
5.  Insert into Pi and boot.

> Never restore an old TinyPilot (Pi Zero) image: that design is superseded. Restore only an image of the matching node (Steering Pi 3B for 192.168.20.100).

**Tip**: Keep a "Spare" Pre-Flashed SD card taped to the inside of the electronics cabinet for 5-minute recovery at sea.
