# Satellite 1 Raspberry Controller

Use a Raspberry Pi to have basic control over the [Satellite 1 HAT by FutureProofHomes](https://futureproofhomes.net/).  
Tested on Raspberry OS 13 (trixie) (32Bit) - Raspberry Pi Zero 2 W

### Usage
To activate the speaker, run:  
```bash
pi@test-pi:~ $ sat1_venv/bin/sat1-control speaker
Speaker enabled
```

Record a sample and play: 
```
arecord  -f S16_LE -r 48000 -c 1 -t wav -d 5 test.wav
aplay test.wav
```

### Install

Install dependencies 
```bash
sudo apt install python3-dev git
```

Create a virtualenv 
```bash
python -m venv sat1_venv
sat1_venv/bin/pip install git+https://github.com/corus87/Satellite-1-Raspberry-Controller
```

### CLI Usage

Make sure you meet the [requirements](#requirements).

If you installed the Satellite 1 Controller in a virtualenv, you will find an executable e.g. ```~/sat1_venv/bin/sat1-control```


```bash
usage: sat1-control [-h] [--led] [--speaker] {led,speaker} ...

positional arguments:
  {led,speaker}  Choose action.

options:
  -h, --help     show this help message and exit
  --led          Run LED Pattern
  --speaker      Control Speaker
```

```bash
usage: sat1-control led [-h] --animation {on_start,on_error,listen,think,speak,off} [--timeout TIMEOUT] [--pattern {default}]

options:
  -h, --help            show this help message and exit
  --animation, -a {on_start,on_error,listen,think,speak,off}
                        Choose animation
  --timeout, -t TIMEOUT
                        Timeout when animation ends
  --pattern, -p {default}
                        Pattern to use

```

```bash
usage: sat1-control speaker [-h] [--set-volume SET_VOLUME] [--increase] [--decrease] [--mute_on] [--mute_off] [--button_control] [--get_volume]

options:
  -h, --help            show this help message and exit
  --set-volume, -v SET_VOLUME
                        Set volume between 0-1
  --increase, -i        Increase Volume
  --decrease, -d        Decrease Volume
  --mute_on, -m         Mute on
  --mute_off, -u        Mute off
  --button_control, -b  Control volume with HW buttons (Left: Mute/Unmute, Up: Increase, Down: Decrease volume)
  --get_volume, -g      Get volume
```

### Requirements

In order to use the speaker and microphone, we need an appropriate device tree overlay. We can use [this basic](https://github.com/AkiyukiOkayasu/RaspberryPi_I2S_Slave) overlay.

Run the following commands to setup the PI.

Compile and write the overlay to /boot/overlays  

```bash
wget https://github.com/corus87/Satellite-1-Raspberry-Controller/raw/branch/main/extras/genericstereoaudiocodec.dts -O /tmp/genericstereoaudiocodec.dts
sudo dtc -@ -H epapr -O dtb -o /boot/overlays/genericstereoaudiocodec.dtbo -Wno-unit_address_vs_reg /tmp/genericstereoaudiocodec.dts
```

Edit /boot/firmware/config.txt  
Enable/Uncomment I2S, SPI, I2C and add device tree overlay

```bash
# Uncomment some or all of these to enable the optional hardware interfaces
dtparam=i2c_arm=on
dtparam=i2s=on
dtparam=spi=on
...
[all]
dtoverlay=genericstereoaudiocodec
```

To be able to change the speaker and microphone volume via ALSA, you can use a asoundrc which does the following:

- Created two soft volumes mixer (playback and capture).
- Using dsnooper and dmixer to use the device by more then one application.
- Sets the the microphone and playback device as default.
- Sets the sample rate to 48khz

Get the asoundrc and write to users home directory 

```bash
wget https://github.com/corus87/Satellite-1-Raspberry-Controller/raw/branch/main/extras/asoundrc -O ~/.asoundrc
```

Reboot the PI 

```bash
sudo reboot
```


