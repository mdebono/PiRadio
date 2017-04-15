import glob, random, sys, vlc
from Adafruit_CharLCD import *
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time

channels = [
    'http://stream.antenne1.de/stream1/livestream.mp3',
    'http://jamfm.hoerradar.de/jamfm-mp3-128'
]

channelNames = [
    'Antenne 1',
    'JAM FM'
]

channel = 0

BUTTON_PLAY = 14
BUTTON_NEXT = 15
LED = 18

GPIO.setup(BUTTON_PLAY, GPIO.IN)
GPIO.setup(BUTTON_NEXT, GPIO.IN)
GPIO.setup(LED, GPIO.OUT)

player = vlc.MediaPlayer()
medialist = vlc.MediaList(channels)

mlplayer = vlc.MediaListPlayer()
mlplayer.set_media_player(player)
mlplayer.set_media_list(medialist)

lcd = Adafruit_CharLCD()

def message(m):
    print(m)
    lcd.clear()
    lcd.message(m)

def play(ch):
    mlplayer.play_item_at_index(channel)
    message('Playing\n' + channelNames[channel])
    GPIO.output(LED, False)

play(channel)

while True:
    if GPIO.input(BUTTON_PLAY):
        if mlplayer.is_playing():
            mlplayer.stop()
            message('Stopped :(')
            GPIO.output(LED, True)
        else:
            play(channel)
    if GPIO.input(BUTTON_NEXT):
        channel += 1
        if (channel >= len(channels)):
            channel = 0
        play(channel)
        
    time.sleep(0.1)
