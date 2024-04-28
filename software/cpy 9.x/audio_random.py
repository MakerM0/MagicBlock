import board
import audiomp3
import audiobusio
import digitalio
import random
import analogio
import os
import gc
import time
import displayio
import terminalio
import busio
from adafruit_st7789 import ST7789
import adafruit_imageload

IMG_WIDTH=96
IMG_HEIGHT=96
IMG_FRAME=3 #gif frames

button = digitalio.DigitalInOut(board.GP11) 
button.switch_to_input(digitalio.Pull.UP)


battery = analogio.AnalogIn(board.A3)
bat_raw = battery.value

random.seed(bat_raw)


AUDIO_PWR = board.GP28
# audio power,Pull SD_MODE low to place the device in shutdown
audiopwr = digitalio.DigitalInOut(AUDIO_PWR)
audiopwr.direction = digitalio.Direction.OUTPUT
audiopwr.value = False   #power on


# Starting in CircuitPython 9.x fourwire will be a seperate internal library
# rather than a component of the displayio library
try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire
from adafruit_display_text import label
from adafruit_st7789 import ST7789

# First set some parameters used for shapes and text
BORDER = 20
FONTSCALE = 1
BACKGROUND_COLOR = 0x00FF00  # Bright Green
FOREGROUND_COLOR = 0xAA0088  # Purple
TEXT_COLOR = 0xFFFF00
 


#spi
SPI_SCLK= board.GP18
SPI_MOSI= board.GP19 
# SPI_MISO= board.IO15


#display
LCD_CS = board.GP17
LCD_DC = board.GP21
LCD_RST = board.GP22
LCD_BL = board.GP6

lcd_reset = digitalio.DigitalInOut(LCD_RST)
lcd_reset.direction = digitalio.Direction.OUTPUT

def disp_reset():
    lcd_reset.value = True   #power on
    time.sleep(0.1)
    lcd_reset.value = False   #power off
    time.sleep(0.1)
    lcd_reset.value = True   #power on
    time.sleep(0.1)

disp_reset()

# Release any resources currently in use for the displays
displayio.release_displays()

spi = busio.SPI(SPI_SCLK,SPI_MOSI)

while not spi.try_lock():
    pass
spi.configure(baudrate=24000000) # Configure SPI for 24MHz
spi.unlock()
 
 

display_bus = FourWire(spi, command=LCD_DC,chip_select=LCD_CS)
display = ST7789(
    display_bus, rotation=180, width=135, height=240, rowstart=40, colstart=53, backlight_pin=LCD_BL ,backlight_on_high = False 
)
# Make the display context
splash = displayio.Group()
display.root_group = splash

# sprit_sheet,palette = adafruit_imageload.load('/images/gongde.bmp',bitmap = displayio.Bitmap,palette = displayio.Palette)
# palette.make_transparent(0)
# spirite = displayio.TileGrid(sprit_sheet,pixel_shader=palette, 
#                              width=1,
#                              height=1,
#                              tile_width=IMG_WIDTH,
#                              tile_height=IMG_HEIGHT                             
#                              )
# palette.make_transparent(0)
# spirite[0]=0
# spirite.x = (display.width-IMG_WIDTH*1)//2
# spirite.y = (display.height-IMG_HEIGHT*1)//2
# 
# splash.append(spirite)

def audiopwr_on():
    audiopwr.value = True
    
def audiopwr_off():
    audiopwr.value = False    

trig=False

def get_files(base):
    files = os.listdir(base)
    file_names = []
    for isdir,filetext in enumerate(files):
        if  filetext.endswith('.mp3') or filetext.endswith('.bmp'):
            if filetext  not   in  ('code.py','launch.py','boot.py'):                
                stats = os.stat(base+filetext)
                isdir = stats[0]&0x4000
                if isdir:
                    pass
#                     file_names.append((filetext,True))
                else:
                    file_names.append(filetext)
                    
    return file_names
i2s = audiobusio.I2SOut(board.GP26, board.GP27, board.GP25)
def play_wave(filename):
    global trig
    print(filename)
    audiopwr_on()
    wave_file=None
    
    try :
        wave_file = open('audio/mp3/{}'.format(filename), "rb")
        wave = audiomp3.MP3Decoder(wave_file)
        i2s.play(wave)
        while i2s.playing:
            if button.value==0:
                i2s.stop()
                trig=True
                break
            pass
#         wave.deinit()
        wave_file.close()
        
         
    except Exception as e : 
        print (e)
#     i2s.deinit()
    audiopwr_off()
    wave_file=None
    gc.collect()
    pass

# playwave("大梦 (Live) - 瓦依那,任素汐.mp3")


 

 
def show_image(filename):
    sprit_sheet,palette = adafruit_imageload.load('/images/{}'.format(filename),bitmap = displayio.Bitmap,palette = displayio.Palette)
    palette.make_transparent(0)
    spirite = displayio.TileGrid(sprit_sheet,pixel_shader=palette, 
                                 width=1,
                                 height=1,
                                 tile_width=IMG_WIDTH,
                                 tile_height=IMG_HEIGHT                             
                                 )
    palette.make_transparent(0)
    spirite[0]=0
    spirite.x = (display.width-IMG_WIDTH*1)//2
    spirite.y = (display.height-IMG_HEIGHT*1)//2

    splash.append(spirite)
    
    
    display.refresh(target_frames_per_second=60)
    
    for i in range(3): 
        
        spirite[0]= i
        time.sleep(0.1)
    spirite[0]= 0
    


imagefiles = get_files("images/")
imagefiles_num = len(imagefiles)
print(imagefiles)
print(imagefiles_num)

mp3files = get_files("audio/mp3/")
print(mp3files)
mp3files_num = len(mp3files)
print(mp3files_num)
show_image(imagefiles[0])
while True:
    if button.value==0 or trig==True:
        trig=False
        splash.pop()
        show_image(imagefiles[random.randint(0,imagefiles_num-1)])
        
        play_wave(mp3files[random.randint(0,mp3files_num-1)])
        
        print(gc.mem_free())
        time.sleep(0.3)
    pass
    

