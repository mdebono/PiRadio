# Synopsis
This is a Python script for a Raspberry Pi internet radio.

# Installation
1. Clone the repository into `~/Documents`  
   `git clone git@gitlab.com:michael.debono/PiRadio.git`
2. Edit your `rc.local` file:  
   `nano /etc/rc.local`  
   Add the following:  
   `sudo python3 /home/pi/Documents/PiRadio/radio.py &`  
   before  
   `exit 0`
3. Restart Raspberry Pi

# Stopping the radio
1. Show the radio processes  
   `ps -ef | grep "radio"`
2. Look for `python3 /home/pi/Documents/PiRadio/radio.py`
3. Kill the process  
  `sudo kill -9 <PID>`
