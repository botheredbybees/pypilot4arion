# Adding a CJMCU‑680 (BME680) Cabin Environment Sensor

This note describes how to add a CJMCU‑680 (BME680) environmental sensor to the Arion system to measure **cabin temperature, humidity, barometric pressure, and VOC‑based “air quality”** near the galley/pilothouse.

The CJMCU‑680 is a breakout board for Bosch’s **BME680**, which exposes I2C via pins `SCL`, `SDA`, `SDO`, and `CS`. [bosch-sensortec](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf)
We connect it to the **Raspberry Pi 4** that runs SignalK and use a BME680‑aware SignalK plugin to publish the data.

***

## Hardware and Wiring

### Pinout

The CJMCU‑680 board has the following pins (as per silkscreen):

- `VCC` – power in (3.3 V)
- `GND` – ground
- `SCL` – I2C clock
- `SDA` – I2C data
- `SDO` – I2C address select (and SPI MISO in SPI mode)
- `CS` – chip select (SPI mode) [techonicsltd](https://www.techonicsltd.com/bme680-temperature-humidity-pressure-and-gas-sensor/)

For our use we run the BME680 in **I2C mode**, so only `VCC`, `GND`, `SCL`, and `SDA` are required. `SDO` chooses the I2C address, and `CS` should remain tied to VCC internally (it usually is on these breakouts, but we do not drive it from the Pi). [itbrainpower](https://itbrainpower.net/a-gsm/RaspberryPI-BME680-sensor_howto)

### Raspberry Pi 4 Connections (I2C1)

Use the main I2C bus `I2C1` on the Pi 4:

| CJMCU‑680 | RPi 4 physical pin | RPi 4 signal                        |
|-----------|--------------------|-------------------------------------|
| `VCC`     | Pin 1              | 3V3                                 |
| `GND`     | Pin 9              | GND                                 |
| `SCL`     | Pin 5              | GPIO 3 (I2C1 SCL)                   |
| `SDA`     | Pin 3              | GPIO 2 (I2C1 SDA)                   |
| `SDO`     | (leave floating, or strap per address choice, see below) |
| `CS`      | (leave unconnected; board keeps it high for I2C)         |

References and examples for BME680 I2C wiring to Raspberry Pi show the same mapping (3V3, GND, SDA on GPIO 2, SCL on GPIO 3). [eng.libretexts](https://eng.libretexts.org/Courses/University_of_Arkansas_Little_Rock/IFSC_4399_-_The_Internet_of_Things_(IoT)/BME680_sensor_setup_using_I2C)

#### I2C Address (SDO)

The BME680 supports two I2C addresses: [bosch-sensortec](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf)

- `SDO` low (GND) → address `0x76`
- `SDO` high (3.3 V) → address `0x77`

On some CJMCU‑680 boards `SDO` is left floating and pulled internally; if you do nothing you’ll typically get `0x76`. If we ever need to change the address (e.g., another BME sensor on the same bus) we can:

- tie `SDO` to `3V3` for `0x77`, or
- tie `SDO` to `GND` for `0x76`.

After wiring, power up the Pi and verify the address:

```bash
sudo apt-get install -y i2c-tools
sudo i2cdetect -y 1
```

You should see either `0x76` or `0x77` in the table. [itbrainpower](https://itbrainpower.net/a-gsm/RaspberryPI-BME680-sensor_howto)

***

## Enabling I2C on the Pi 4

On the RPi 4 that runs SignalK:

```bash
sudo raspi-config
```

- Go to **Interfacing Options → I2C → Enable**.
- Reboot:

```bash
sudo reboot
```

Verify that `/dev/i2c-1` exists and `i2cdetect -y 1` shows the sensor address. [demo.signalk](https://demo.signalk.org/documentation/Installation/Raspberry_Pi.html)

***

## Installing a SignalK BME680 Plugin

We use the SignalK plugin **`@oehoe83/signalk-raspberry-pi-bme680`**, which is a BME680‑aware variant of the classic `signalk-raspberry-pi-bme280` plugin. [npmjs](https://www.npmjs.com/package/@oehoe83/signalk-raspberry-pi-bme680)

This plugin:

- Talks directly to the BME680 over I2C from the Pi.
- Publishes:
  - `environment.inside.temperature`
  - `environment.inside.humidity`
  - `environment.pressure`
  - a gas/VOC‑derived “air quality” value (path naming depends on plugin config; typically `environment.inside.airQuality` or a raw gas resistance value). [forum.openmarine](https://forum.openmarine.net/showthread.php?tid=3180)

### Install via npm

On the Pi 4 as the SignalK user:

```bash
cd ~/.signalk
npm install @oehoe83/signalk-raspberry-pi-bme680
```

Alternatively, use the SignalK web UI:

- Open the SignalK admin web interface.
- Go to **Appstore / Plugins**.
- Search for `@oehoe83/signalk-raspberry-pi-bme680`.
- Click **Install**. [demo.signalk](https://demo.signalk.org/documentation/Installation/Raspberry_Pi.html)

Restart the SignalK server if it does not restart automatically.

***

## Plugin Configuration

In the SignalK web UI, go to **Server → Plugin Config** and open the BME680 plugin configuration. The exact fields may vary slightly by version, but typically include: [npmjs](https://www.npmjs.com/package/@oehoe83/signalk-raspberry-pi-bme680)

- **I2C Bus**: `1` (for `/dev/i2c-1`).
- **I2C Address**: `0x76` or `0x77` (whichever you saw in `i2cdetect`).
- **Update interval**: e.g., `5` seconds (tweak for noise vs. responsiveness).
- **Oversampling / filtering**: Accept plugin defaults initially.

For mapping to SignalK paths:

- Temperature → `environment.inside.temperature`
- Humidity → `environment.inside.humidity`
- Pressure → `environment.pressure`
- Gas/VOC → use whatever default path the plugin provides; if it offers an option, map to `environment.inside.airQuality` so dashboards can find it easily.

OpenPlotter / OpenCPN can then subscribe to these SignalK paths to display cabin environment and barometric trends. [youtube](https://www.youtube.com/watch?v=GTo_DVZ4D6U)

***

## Notes on Interpretation and Safety

The BME680’s gas sensor provides a **resistance value that correlates with VOC concentration**, and some libraries convert that to an approximate “air quality index.” It is **not a calibrated CO, CO₂, or LPG detector** and should only be used as a **relative indicator** (e.g., “air quality worse when stove is on, better when venting”). [randomnerdtutorials](https://randomnerdtutorials.com/bme680-sensor-arduino-gas-temperature-humidity-pressure/)

For safety near the gas stove:

- Use the CJMCU‑680 as a **comfort / trend sensor** (temperature, humidity, pressure, VOC trend).
- Still rely on dedicated CO/CO₂ or LPG detectors with audible alarms for life‑safety. [robocraze](https://robocraze.com/blogs/post/what-is-bme680-sensor-specification-working)

***

## Quick Smoke‑Test from the Shell

Before depending on SignalK, it can be helpful to confirm that the Pi can talk to the sensor directly using a Python BME680 library (e.g., the Bosch or Adafruit BME680 Python drivers). [howtoraspberry](https://www.howtoraspberry.com/2022/02/running-the-bme680-humidity-temperature-barometer-voc-co2-sensor-with-circuitpython/)

Example (outline only):

```bash
# one-time
sudo pip3 install adafruit-circuitpython-bme680
```

```python
import board, busio
import adafruit_bme680

i2c = busio.I2C(board.SCL, board.SDA)
bme = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x76)  # or 0x77

print("Temp:", bme.temperature)
print("Humidity:", bme.humidity)
print("Pressure:", bme.pressure)
print("Gas:", bme.gas)
```

If those values look sane, the hardware is good and any remaining issues will be in the SignalK plugin configuration. [howtoraspberry](https://www.howtoraspberry.com/2022/02/running-the-bme680-humidity-temperature-barometer-voc-co2-sensor-with-circuitpython/)

***
