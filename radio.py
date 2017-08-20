import glob, random, sys, vlc, os, csv
from Adafruit_CharLCD import *
from datetime import datetime
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import time, subprocess

channelsFilename = 'channels.csv'

BUTTON_PLAY = 14
BUTTON_NEXT = 15
VOLUME_UP = 18
VOLUME_DOWN = 10

print('Starting PiRadio...')

GPIO.setup(BUTTON_PLAY, GPIO.IN)
GPIO.setup(BUTTON_NEXT, GPIO.IN)
GPIO.setup(VOLUME_UP, GPIO.IN)
GPIO.setup(VOLUME_DOWN, GPIO.IN)

lcd = Adafruit_CharLCD()
MAX_LCD_LINE_CHARS = 16

default_lcd_text = None
is_default_lcd_text = False

path = os.path.abspath(os.path.dirname(sys.argv[0]))
channelsFilepath = '{}/{}'.format(path, channelsFilename)
print('Reading channels from {}...'.format(channelsFilepath))
urls = []
channelNames = []
print('Channels:')
with open(channelsFilepath) as f:
    reader = csv.reader(f)
    # skip header row
    next(reader, None)
    for row in reader:
        if len(row) >= 2:
            channelName = row[0]
            url = row[1]
            print('  {}'.format(channelName))
            channelNames.append(channelName)
            urls.append(url)

player = vlc.MediaPlayer()
medialist = vlc.MediaList(urls)

mlplayer = vlc.MediaListPlayer()
mlplayer.set_media_player(player)
mlplayer.set_media_list(medialist)

def message(m, is_permanent=True, visible_time=0):
    global default_lcd_text
    global is_default_lcd_text
    global now
    now = get_time()
    if is_permanent:
        align = MAX_LCD_LINE_CHARS - m.find('\n')
        output = m.replace('\n', '{:>{}}\n'.format(now, align))
        print(output)
        lcd.clear()
        lcd.message(output)
        default_lcd_text = m
        is_default_lcd_text = True
    else:
        print(m)
        lcd.clear()
        lcd.message(m)
        is_default_lcd_text = False
        time.sleep(visible_time)

def play(ch):
    message('\n{}'.format(channelNames[ch]))
    mlplayer.play_item_at_index(ch)

def volume_change(delta):
    volume = player.audio_get_volume()
    volume = volume + delta
    player.audio_set_volume(volume)
    message('Volume: {}'.format(volume), False, 0.2)

def get_time():
    return datetime.now().strftime('%d.%m.%Y %H:%M')

def check_update_time():
    global default_lcd_text
    global now
    new_time = get_time()
    # only send update if time is different
    if new_time != now:
        now = new_time
        message(default_lcd_text)

now = get_time()
channel = 0
play(channel)

while True:
    # TODO: Shutdown doesn't work anymore on Raspian Jessie, probably needs sudo
    #if GPIO.input(VOLUME_UP) and GPIO.input(VOLUME_DOWN):
    #    message('Shutting down...')
    #    subprocess.call(['shutdown', '-h', 'now', 'Radio initiated shutdown!'])
    #elif GPIO.input(BUTTON_PLAY):
    if GPIO.input(BUTTON_PLAY):
        if mlplayer.is_playing():
            mlplayer.stop()
            message('\n')
        else:
            play(channel)

    elif GPIO.input(BUTTON_NEXT):
        channel += 1
        if (channel >= len(urls)):
            channel = 0
        play(channel)
    elif GPIO.input(VOLUME_UP):
        volume_change(10)
    elif GPIO.input(VOLUME_DOWN):
        volume_change(-10)

    if not is_default_lcd_text:
        message(default_lcd_text)

    check_update_time()

    time.sleep(0.1)

