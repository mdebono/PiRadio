# Synopsis
This is a Python script for a Raspberry Pi internet radio.

# Installation
Edit your `rc.local` file:
`nano /etc/rc.local`
Add the following:
`sudo python3 /home/pi/Documents/Radio/radio.py &`
before
`exit 0`
