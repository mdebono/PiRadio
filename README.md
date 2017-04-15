# Synopsis
This is a Python script for a Raspberry Pi internet radio.

# Installation
1. Clone the repository into `~/Documents`  
   `git clone git@gitlab.com:michael.debono/PiRadio.git`
2. Clone MissPhilbin/Adventure_9 repository into `~/Documents`  
   `git clone https://github.com/MissPhilbin/Adventure_9.git`
3. Move the `*.py` files into the PiRadio directory.
4. Install VLC  
   `sudo apt-get install vlc`
5. Test the radio from its directory  
   `sudo python3 radio.py`
6. Edit your `rc.local` file:  
   `nano /etc/rc.local`  
   Add the following:  
   `sudo python3 /home/pi/Documents/PiRadio/radio.py &`  
   before  
   `exit 0`
7. Restart Raspberry Pi

# Stopping the radio
1. Show the radio processes  
   `ps -ef | grep "radio"`
2. Look for `python3 /home/pi/Documents/PiRadio/radio.py`
3. Kill the process  
  `sudo kill -9 <PID>`
