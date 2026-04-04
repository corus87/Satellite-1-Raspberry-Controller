# Satellite 1 Raspberry Controller

Control the [Satellite 1 HAT by FutureProofHomes](https://futureproofhomes.net/) from a Raspberry Pi.

Tested on Raspberry Pi OS 13 (Trixie) 32-bit — Raspberry Pi Zero 2 W.

---

### Install

Install system dependencies:
```bash
sudo apt install python3-dev git
```

Create a virtualenv and install:
```bash
python -m venv sat1_venv
sat1_venv/bin/pip install git+https://github.com/corus87/Satellite-1-Raspberry-Controller
```

---

### Usage as a library

```python
from sat1_control import LedController, SpeakerController, Buttons
from time import sleep

# LED animations
led = LedController(timeout=30)
led.listen()
led.wait()
led.off()

# Speaker
spk = SpeakerController()
spk.set_volume(0.7)
spk.increase_volume()
spk.decrease_volume()
spk.mute_on()
spk.mute_off()
print(spk.volume)

# Buttons
btn = Buttons()
while True:
    if btn.up.pressed_edge:
        spk.increase_volume()
    if btn.down.pressed_edge:
        spk.decrease_volume()
    if btn.mute.pressed:
        spk.mute_on()
    sleep(0.05)
```

---

### CLI

```bash
sat1-control led --animation listen --timeout 30
sat1-control led --animation think
sat1-control led --animation speak
sat1-control led --animation on_error
sat1-control led --animation off

sat1-control speaker --set-volume 0.7
sat1-control speaker --increase
sat1-control speaker --decrease
sat1-control speaker --mute-on
sat1-control speaker --mute-off
sat1-control speaker --get-volume
```

**LED options:**
```
--animation, -a  on_start | on_error | listen | think | speak | off
--timeout,   -t  Auto-stop timeout in seconds (default: 10)
--pattern,   -p  Pattern to use (default: default)
```

**Speaker options:**
```
--set-volume, -v  Set volume 0.0–1.0
--increase,   -i  Increase volume by one step
--decrease,   -d  Decrease volume by one step
--mute-on,    -m  Mute
--mute-off,   -u  Unmute
--get-volume, -g  Print current volume
```

---

### Audio setup (I2S / ALSA)

To use the speaker and microphone, a device tree overlay is required.

Compile and install the overlay:
```bash
wget https://raw.githubusercontent.com/corus87/Satellite-1-Raspberry-Controller/refs/heads/main/extras/genericstereoaudiocodec.dts -O /tmp/genericstereoaudiocodec.dts
sudo dtc -@ -H epapr -O dtb -o /boot/overlays/genericstereoaudiocodec.dtbo -Wno-unit_address_vs_reg /tmp/genericstereoaudiocodec.dts
```

Edit `/boot/firmware/config.txt` — enable I2C, I2S, SPI and add the overlay:
```
dtparam=i2c_arm=on
dtparam=i2s=on
dtparam=spi=on

[all]
dtoverlay=genericstereoaudiocodec
```

Optionally install the ALSA config for software volume control, multi-app access and 48 kHz default:
```bash
wget https://raw.githubusercontent.com/corus87/Satellite-1-Raspberry-Controller/refs/heads/main/extras/asoundrc -O ~/.asoundrc
```

Reboot:
```bash
sudo reboot
```

Record and play back a test sample:
```bash
arecord -f S16_LE -r 48000 -c 1 -t wav -d 5 test.wav
aplay test.wav
```
