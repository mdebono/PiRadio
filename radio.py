import glob, random, sys, vlc
from Adafruit_CharLCD import *
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time

channels = [
    'http://stream.antenne1.de/stream1/livestream.mp3',
    'http://jamfm.hoerradar.de/jamfm-mp3-128',
    'http://s1.voscast.com:8132/',
    'http://173.192.137.34:8044'
]

channelNames = [
    'Antenne 1',
    'JAM FM',
    '89.7 bay',
    'Antena Zagreb'
]

channel = 0

BUTTON_PLAY = 14
BUTTON_NEXT = 15
VOLUME_UP = 18
VOLUME_DOWN = 10

GPIO.setup(BUTTON_PLAY, GPIO.IN)
GPIO.setup(BUTTON_NEXT, GPIO.IN)
GPIO.setup(VOLUME_UP, GPIO.IN)
GPIO.setup(VOLUME_DOWN, GPIO.IN)

player = vlc.MediaPlayer()
medialist = vlc.MediaList(channels)

mlplayer = vlc.MediaListPlayer()
mlplayer.set_media_player(player)
mlplayer.set_media_list(medialist)

lcd = Adafruit_CharLCD()

default_lcd_text = None
is_default_lcd_text = False

def message(m):
    global is_default_lcd_text
    print(m)
    lcd.clear()
    lcd.message(m)
    is_default_lcd_text = False

def play(ch):
    global default_lcd_text
    global is_default_lcd_text
    default_lcd_text = 'Playing\n' + channelNames[ch]
    is_default_lcd_text = False
    mlplayer.play_item_at_index(ch)

def volume_change(delta):
    volume = player.audio_get_volume()
    volume = volume + delta
    player.audio_set_volume(volume)
    message('Volume: {0}'.format(volume))
    time.sleep(0.2)

play(channel)

while True:
    if GPIO.input(BUTTON_PLAY):
        if mlplayer.is_playing():
            mlplayer.stop()
            message('Stopped :(')
        else:
            play(channel)
    elif GPIO.input(BUTTON_NEXT):
        channel += 1
        if (channel >= len(channels)):
            channel = 0
        play(channel)
    elif GPIO.input(VOLUME_UP):
        volume_change(10)
    elif GPIO.input(VOLUME_DOWN):
        volume_change(-10)

    if not is_default_lcd_text:
        message(default_lcd_text)
        is_default_lcd_text = True
        
    time.sleep(0.1)

