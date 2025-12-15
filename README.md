# Breadcrumb Tracker
-----


**Requirements:**

1. A raspberry pi (I'm using a Raspberry Pi 4, a Pi 0w 2 will work if you use a serial GPS module or a microUSB OTG adapter. the 0w will also work but conda is not supported which gets dicey)
2. A microSD card
3. A USB GPS module like [this one](https://www.amazon.com/dp/B01EROIUEW?ref_=ppx_hzsearch_conn_dt_b_fed_asin_title_8) (similar GPIO/serial modules may also work if properly configured)


**Installation:**

1. Image a blank SD card with the latest raspberry pi OS "lite" build.
2. Install git `sudo apt install git`
3. Clone this repo `git clone https://github.com/wx4stg/breadcrumb-tracker`
4. Optional but recommended, update the system `sudo apt update && sudo apt upgrade -y`
5. Optional but recommended, install tailscale and link your account: https://tailscale.com/download
6. Install gpsd: `sudo apt install gpsd chrony`
7. Plug in your USB GPS
8. Find the GPS' device path: `ls /dev/` (hopefully you will see a path called 'ttyACM0')
9. Configure gpsd: `sudo nano /etc/default/gpsd`
 
Make the following edits:

```
# Devices gpsd should collect to at boot time.
# They need to be read/writeable, either by user gpsd or the group dialout.
DEVICES="/dev/ttyACM0"

# Other options you want to pass to gpsd
GPSD_OPTIONS="-n"

# Automatically hot add/remove USB GPS devices via gpsdctl
USBAUTO="true"

# Start the gpsd daemon automatically at boot time
START_DAEMON="true"
```

10. Configure chrony: `sudo nano /etc/chrony/chrony.conf`

Make the following edits:

- Comment out the line `pool 2.debian.pool.ntp.org iburst` -> `#pool 2.debian.pool.ntp.org iburst`
- Comment out the line `sourcedir /run/chrony-dhcp` -> `#sourcedir /run/chrony-dhcp`
- Comment out the line `sourcedir /etc/chrony/sources.d` -> `#sourcedir /etc/chrony/sources.d`
- Add a line `refclock SHM 0 offset 0.5 delay 0.2 refid NMEA`

11. Install micromamba: https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html#automatic-install
12. Reboot: `sudo shutdown -r now`
13. Wait for a GPS fix: `cgps` (your lat/lon/alt/time will show up)
14. Make sure chrony has picked up GPS for time: `chronyc sources` (you should see a line `#* NMEA`)
15. Import the environment `cd breadcrumbs-tracker/ && micromamba create -f env.yml`
16. Import the systemd service `sudo cp ./breadcrumb.service /etc/systemd/system/`
17. Enable logging `sudo systemctl enable --now breadcrumb`
18. Make sure a csv file is created in the "breadcrumb-tracker" directory after 5 seconds.
