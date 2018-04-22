# Jukebox Setup

## System Setup

1. Flash a micro-SD card with Raspbian Lite (Stretch) using Etcher.
2. Login with default username `pi` and default password `raspberry`.
3. Change password with `passwd`.

## Setup Apple USB Keyboard

The keyboard layout needs to be changed for keys to be mapped correctly. The default mapping is UK-based and doesn't work well with my US Apple USB keyboard.

1. Run `sudo dpkg-reconfigure locales` and select `en_US.UTF-8`.
2. Run `sudo dpkg-reconfigure keyboard-configuration` and select `Apple Aluminum Keyboard (ANSI)` and `English (US)`.
3. Reboot with `reboot`.

## Setup Wifi

1. Add a network to the config with `wpa_passphrase "SSID" "PASSWORD" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf`.
2. Remove the plaintext password with `nano /etc/wpa_supplicant/wpa_supplicant.conf`.
3. Run `wpa_cli -i wlan0 reconfigure`.
4. Check for an IP address with `ifconfig wlan0`.

Alternatively, I believe setup can be done with `sudo raspi-config`.

## Change Hostname

Change the hostname with the config utility.

1. `sudo raspi-config`.
2. Go to `Network Options` and then `Hostname` and change the hostname.
3. Reboot.

## Enable SSH

Enable and start SSH on the Pi.

1. `sudo systemctl enable ssh`
2. `sudo systemctl start ssh`

## MPD

1. `sudo apt-get install mpd`
2. `cd ~`
3. `mkdir music`
4. `mkdir playlists`
5. Add user `mpd` to group `pi` with `sudo usermod -a -G pi mpd`.
6. Allow group read/write access to `music` and `playlist` directories with `sudo chmod ug+rw music playlists`.
7. Edit the `mpd` config with `sudo nano /etc/mpd.conf`.
8. Change `music_directory` to `"/home/pi/music"`.
9. Change `playlist_directory` to `"/home/pi/playlists"`.
10. Restart `mpd` with `sudo systemctl restart mpd`.

## Configure USB Audio Interface

I'm using a [UGREEN USB audio interface](https://www.amazon.com/dp/B06XP5R449). It requires a little setup.

1. Verify presence with `lsusb`.
2. Verify presence with `amixer`.
3. `sudo nano /usr/share/alsa/alsa.conf`
4. Change `defaults.ctl.card` and `defaults.pcm.card` to `1`.
5. Reboot.

## Dependencies

1. `sudo apt-get install libusb-dev`
2. `sudo apt-get install python-pip`
3. `pip install -U nfcpy`
4. `pip install -U pyyaml`
5. `pip install -U python-mpd2`
6. `pip install -U libusb1`

## Setup NFC Reader

I have a Sony RC-S380 and these instructions work with it.

1. Plug reader in.
2. `python -m nfc`
3. Run the commands necessary to assign the device to the right group. (The output of the previous command should include them.)
4. Unplug and replug the reader.

## Configure GitHub Access

1. `sudo apt-get install git`
2. `ssh-keygen -t rsa -b 4096 -C "email@example.com"`
3. `cat ~/.ssh/id_rsa.pub`
4. Paste as a [new SSH public key on GitHub](https://github.com/settings/ssh/new).
5. Start `ssh-agent` in the background with `eval "$(ssh-agent -s)"`.
6. Add the private key to the agent with `ssh-add ~/.ssh/id_rsa`.

## Install Jukebox App

1. `cd ~`
2. `git clone git@github.com:danhudlow/jukebox.git`
3. `cd jukebox`
4. `python start.py`
