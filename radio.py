import glob, random, sys, vlc, os, csv
from datetime import datetime

GPIO = None
try:
    import RPi.GPIO as GPIO
    from Adafruit_CharLCD import *
except ImportError as err:
    print(err)
    print('WARNING: Not running in Raspberry Pi mode!')

if GPIO:
    GPIO.setmode(GPIO.BCM)
    
import time, subprocess, sched, threading, queue
import urllib.request, json

CHANNELS_FILENAME = 'channels.csv'
WEATHER_API_KEY_FILENAME = 'WEATHERAPIKEY'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather?id=2918632&appid=WEATHERAPIKEY&units=metric'
DEBUG = False

BUTTON_PLAY = 14
BUTTON_NEXT = 15
VOLUME_UP = 18
VOLUME_DOWN = 10

print('Starting PiRadio...')

if GPIO:
    GPIO.setup(BUTTON_PLAY, GPIO.IN)
    GPIO.setup(BUTTON_NEXT, GPIO.IN)
    GPIO.setup(VOLUME_UP, GPIO.IN)
    GPIO.setup(VOLUME_DOWN, GPIO.IN)
    lcd = Adafruit_CharLCD()
    
MAX_LCD_LINE_CHARS = 16

default_lcd_text = None
is_default_lcd_text = False
weather = ''
weather_new = ''
weather_api_key = ''
weather_url = ''

path = os.path.abspath(os.path.dirname(sys.argv[0]))

# read channels
channelsFilepath = '{}/{}'.format(path, CHANNELS_FILENAME)
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

# read WEATHER API KEY
weatherApiKeyFilepath = '{}/{}'.format(path, WEATHER_API_KEY_FILENAME)
print('\nReading Weather API KEY from {}...'.format(weatherApiKeyFilepath))
with open(weatherApiKeyFilepath) as f:
    weather_api_key = f.readline()
    print('Weather API Key: {}\n'.format(weather_api_key))
    weather_url = WEATHER_API_URL.replace('WEATHERAPIKEY', weather_api_key)

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
        if GPIO:
            lcd.clear()
            lcd.message(output)
        default_lcd_text = m
        is_default_lcd_text = True
    else:
        print(m)
        if GPIO:
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
    global weather
    new_time = get_time()
    # only send update if time is different
    if new_time != now:
        now = new_time
        return True
    else:
        return False

def check_update_weather():
    global weather
    global new_weather
    if new_weather != weather:
        weather = new_weather
        return True
    else:
        return False
    
class Weather(threading.Thread):
    scheduler = sched.scheduler()
    global DEBUG
    if DEBUG:
        debug = 0
        T = 10
    else:
        T = 60*10
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        self.scheduler.enter(0, 1, self.get_weather)
        self.scheduler.run()
    def get_weather(self):
        global new_weather
        js = json.loads(urllib.request.urlopen(weather_url).read().decode("utf-8"))
        temp = round(float(js['main']['temp']), 1)
        condition = js['weather'][0]['main']
        # save weather
        if DEBUG:
            if self.debug == 1000:
                self.debug = 0
            new_weather = '{}C [{}]'.format(temp, self.debug)
            print(js)
            self.debug += 1
        else:
            new_weather = '{}C {}'.format(temp, condition)
        print('Weather: {}'.format(new_weather))
        self.scheduler.enter(self.T, 1, self.get_weather)
    
now = get_time()
channel = 0
play(channel)

thread = Weather(1, "Weather Thread", 1)
thread.start()

while True:
    # TODO: Shutdown doesn't work anymore on Raspian Jessie, probably needs sudo
    #if GPIO.input(VOLUME_UP) and GPIO.input(VOLUME_DOWN):
    #    message('Shutting down...')
    #    subprocess.call(['shutdown', '-h', 'now', 'Radio initiated shutdown!'])
    #elif GPIO.input(BUTTON_PLAY):
    if GPIO and GPIO.input(BUTTON_PLAY):
        if mlplayer.is_playing():
            mlplayer.stop()
            check_update_weather()
            message('\n{}'.format(weather))
            # TODO: trigger weather to download
        else:
            play(channel)

    elif GPIO and GPIO.input(BUTTON_NEXT):
        channel += 1
        if (channel >= len(urls)):
            channel = 0
        play(channel)
    elif GPIO and GPIO.input(VOLUME_UP):
        volume_change(10)
    elif GPIO and GPIO.input(VOLUME_DOWN):
        volume_change(-10)

    if not is_default_lcd_text:
        message(default_lcd_text)

    if check_update_time():
        message(default_lcd_text)
    if not mlplayer.is_playing():
        if check_update_weather():
            message('\n{}'.format(weather))

    time.sleep(0.1)

