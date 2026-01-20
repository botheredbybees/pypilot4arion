# Backup & Disaster Recovery Strategy

## Philosophy
The SD cards in your Raspberry Pis are the most fragile component of the system. They **will** fail eventually due to write-wear or power corruption. A verified backup image is the only way to recover quickly.

## What to Backup
1.  **TinyPilot Config**: The tuning gains and calibration.
    *   *Path*: `/home/tc/.pypilot/pypilot.conf`
2.  **Full SD Images**:
    *   TinyPilot (Pi Zero W)
    *   Lysmarine (Pi 4)

## Backup Procedure

### Method A: Config Text Backup (Fast)
Do this after every successful tuning session.
1.  Connect to TinyPilot via SSH (`ssh tc@192.168.43.101`).
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
    sudo dd if=/dev/sdb of=~/arion_backups/tinypilot_backup_date.img bs=4M status=progress
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

**Tip**: Keep a "Spare" Pre-Flashed SD card taped to the inside of the electronics cabinet for 5-minute recovery at sea.
