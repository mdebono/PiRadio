import glob, random, sys, vlc
from Adafruit_CharLCD import *
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time, subprocess

channels = [
    'http://stream.antenne1.de/stream1/livestream.mp3',
    'http://jamfm.hoerradar.de/jamfm-mp3-128',
    'http://s1.voscast.com:8132/',
    'http://173.192.137.34:8044',
    'http://188.94.97.91:80/radio21.mp3',
	'http://shoutcast.pondi.hr:8000/listen.pls'
]

channelNames = [
    'Antenne 1',
    'JAM FM',
    '89.7 Bay',
    'Antena Zagreb',
    'Radio 21 Hanover',
	'Radio Dalmacija'
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

def message(m, is_permanent=True, visible_time=0):
    global default_lcd_text
    global is_default_lcd_text
    print(m)
    lcd.clear()
    lcd.message(m)
    if is_permanent:
        default_lcd_text = m
        is_default_lcd_text = True
    else:
        is_default_lcd_text = False
        time.sleep(visible_time)

def play(ch):
    message('Playing\n' + channelNames[ch])
    mlplayer.play_item_at_index(ch)

def volume_change(delta):
    volume = player.audio_get_volume()
    volume = volume + delta
    player.audio_set_volume(volume)
    message('Volume: {0}'.format(volume), False, 0.2)

play(channel)

while True:
    if GPIO.input(VOLUME_UP) and GPIO.input(VOLUME_DOWN):
        #TEST: subprocess.call(['shutdown', '-k', 'now', 'Radio initiated shutdown!'])
        message('Shutting down...')
        subprocess.call(['shutdown', '-h', 'now', 'Radio initiated shutdown!'])
    elif GPIO.input(BUTTON_PLAY):
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
        
    time.sleep(0.1)

