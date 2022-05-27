import busio
import random
import audiomp3
import audiopwmio
import board
import digitalio
import traceback
import time
import math

from pmk import PMK
from pmk import hsv_to_rgb
# from pmk.platform.keybow2040 import Keybow2040 as Hardware          # for Keybow 2040
from pmk.platform.rgbkeypadbase import RGBKeypadBase as Hardware  # for Pico RGB Keypad Base


led = digitalio.DigitalInOut(board.LED)
led.switch_to_output()
led.value = True

uart = busio.UART(tx=board.GP12, rx=board.GP13, baudrate=9600, timeout=0) #timeout=0 for non-blocking reads

# uart.write(bytes("hello world!\n", 'utf-8'))

def pln(s):
    if DEBUG: print('SEND', s)
    uart.write(bytes(f"{s}\r\n", 'utf-8'))



audio = audiopwmio.PWMAudioOut(left_channel=board.GP0, right_channel=board.GP1)
decoder = audiomp3.MP3Decoder(open("vocoded.mp3", "rb"))

DEBUG = True

GLOBAL_BRIGHTNESS = 0.5 #out of 1
DIMMING_WHEN_NOT_PRESSED = 0.2

#wrap the classes in better ones, the library makes no sense
#TODO fork the library and rewrite it?
class MyKey():
    def __init__(self, pmk_key):
        self.pmk_key = pmk_key
        self.is_pressed = False
        self.prev_is_pressed = False
        self.just_pressed = False
        self.just_released = False
        self.color_cycle = ColorCycle(["RGB","0","0","0"])
        self.update_rgb()
    def update(self):
        self.is_pressed = bool(self.pmk_key.state)
        self.just_pressed = not self.prev_is_pressed and self.is_pressed
        self.just_released = self.prev_is_pressed and not self.is_pressed
        self.prev_is_pressed = self.is_pressed
#         if self.just_pressed or self.just_released:
#             self.update_rgb()
        self.update_rgb()
    def update_rgb(self):
        dimming = DIMMING_WHEN_NOT_PRESSED
        if self.is_pressed:
            dimming = 1
        rgb = self.color_cycle.get_rgb()
        rgb = [int(x * GLOBAL_BRIGHTNESS * dimming + 0.5) for x in rgb]
        self.pmk_key.rgb = tuple(rgb)
        self.pmk_key.led_on()
    def set_color_cycle(self, color_cycle):
        self.color_cycle = color_cycle
        self.update_rgb()

class MyKeypad():
    def __init__(self, pmk):
        # Set up Keybow
        self.pmk = pmk
        k = self.pmk.keys
        # apply a rotation
        self.keys = [
            MyKey(k[3]), MyKey(k[7]), MyKey(k[11]), MyKey(k[15]),
            MyKey(k[2]), MyKey(k[6]), MyKey(k[10]), MyKey(k[14]),
            MyKey(k[1]), MyKey(k[5]), MyKey(k[9]),  MyKey(k[13]),
            MyKey(k[0]), MyKey(k[4]), MyKey(k[8]),  MyKey(k[12])
        ]
    def update(self):
        self.pmk.update()
        for key in self.keys:
            key.update()

def pop_color(line):
    color_type = line.pop(0)
    if color_type == 'RGB': #RGB values are from 0 to 255
        return (int(line.pop(0)), int(line.pop(0)), int(line.pop(0)))
    elif color_type == 'HSV': #HSV values are from 0.0 to 1.0
        return (hsv_to_rgb(float(line.pop(0)), float(line.pop(0)), float(line.pop(0))))
    else:
        raise Exception(f"invalid color type: {color_type}")

#factor is from 0 to 1
def rgb_blend(rgb1, rgb2, factor):
    factor2 = 1-factor
    return (
        int(rgb1[0] * factor + rgb2[0] * factor2),
        int(rgb1[1] * factor + rgb2[1] * factor2),
        int(rgb1[2] * factor + rgb2[2] * factor2)
    )

def renormalize(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]


class ColorCycle():
    # will pop the elements off the line needed to define a color, and remove the rest
    def __init__(self, line):
        self.colors = []
        self.times = []
        self.color_type = line[0]
        if self.color_type in ('RGB', 'HSV'): #solid color
            self.color_type = 'RGB'
            self.colors.append(pop_color(line))
            self.times.append(1)
        elif self.color_type in ('BLI', 'RAN', 'FAD', 'PUL'): #blink, random, fade, pulse
            #BLI,3,RGB,255,0,0,1.1,RGB,0,255,0,0.5,RGB,0,0,255,2.2
            line.pop(0) #remove the color type from the line
            num_colors = int(line.pop(0))
            for i in range(num_colors):
                self.colors.append(pop_color(line))
                total_time = 0
                if len(self.times) > 0:
                    total_time = self.times[-1]
                self.times.append(float(line.pop(0)) + total_time)
#                 if self.color_type not in ('RAN'):
#                     self.times[-1] += total_time
            #with 1 color, it should blink between that color and off for the same time
            #BLI,1,RGB,255,255,255,0.5
            if len(self.colors) == 1:
                self.colors.append((0,0,0))
                self.times.append(self.times[0] * 2)
        else:
            raise Exception(f"invalid color type: {self.color_type}")
        assert len(self.colors) == len(self.times)
        assert len(self.colors) > 0
    def get_rgb(self):
        time_loop = time.monotonic() % self.times[-1]
        if self.color_type == 'RGB':
            return self.colors[0]
        elif self.color_type in ('BLI', 'RAN'):
            if self.color_type == 'RAN': #weight randomness by times
                time_loop = random.uniform(0, self.times[-1])
            for time_cutoff, color in zip(self.times, self.colors):
                if time_loop < time_cutoff:
                    return color
            return self.colors[-1] #just in case
        elif self.color_type in ('FAD', 'PUL'):
            for i in range(len(self.colors)):
                if time_loop < self.times[i]:
                    prev_time = 0
                    if i > 0:
                        prev_time = self.times[i-1]
                    prev_color = self.colors[(i-1) % len(self.colors)]
                    #renormalize to be from 0 to 1, instead of between times
                    factor = renormalize(time_loop, (prev_time, self.times[i]), (0.0,1.0))
                    if self.color_type == 'PUL':
                        if i % 2 == 0:
                            factor = math.sin(factor * math.pi / 2)
                        else:
                            factor = -math.sin(-factor * math.pi / 2)
                    return rgb_blend(self.colors[i], prev_color, factor)
            return self.colors[-1] #just in case

keypad = MyKeypad(PMK(Hardware()))
keys = keypad.keys

def hex2int(h):
    h = ord(h)
    if h >= ord('0') and h <= ord('9'):
        return h - ord('0')
    if h >= ord('a') and h <= ord('f'):
        return h + 10 - ord('a')
    if h >= ord('A') and h <= ord('F'):
        return h + 10 - ord('A')

def int2hex(i):
    return '0123456789ABCDEF'[i]

def chunk_string(s, n):
    return [s[i:i+n] for i in range(0, len(s), n)]

buffer = b''

current_page = 'None'
lines = []
quit_key = None
#TODO disable listening when in the disconnect page

def goto_none_page():
    print('going to disconnect page')
    current_page = 'None'
    lines.append('@,RGB,0,0,0')
    lines.append('0,RGB,255,0,255')
    lines.append('F,RGB,255,255,0')
    pln(".")

goto_none_page()

pln("@") #ask for colors
while True:
    keypad.update()

    #the bluetooth module cannot handle anything more than 97 bytes or so for some reason
    data = uart.read(93) #by experimenting, the max here without errors is 93
    while data is not None:
#         print(data)
        buffer += data
        data = uart.read(93)
#     if data is not None:
#         print(data)
#         buffer += data
    found = None
    i = 0
    while i < len(buffer):
        b = buffer[i]
        if b == ord('\n'):
            found = i+1
            lines.append(buffer[:found].decode('utf-8').strip())
            if DEBUG: print('RECEIVE', lines[-1])
            buffer = buffer[found:]
            i = 0
            if current_page == 'None':
                print('#$(!&#($*!@')
                lines.append('F,RGB,0,255,0')
        i += 1
    while len(lines) > 0:
        line = lines.pop(0)
        try: #in a try block since the data received might not be as expected
            if ',' in line:
                line = line.split(',')
            else:
                more = line[1:] #everything except the first char
                line = [line[0]] #just the first char
                line.extend(chunk_string(more, 3))
                print('CONVERTED', ','.join(line))
            key_num = line.pop(0)
            if key_num == '.':
                pass
            elif key_num == '?':
                pln(f'?,{current_page}')
            elif key_num == '#':
                current_page = line.pop(0)
                pln(f'?,{current_page}')
                if current_page == 'None':
                    goto_none_page()
            elif key_num == 'Q':
                quit_key = line.pop(0)
                print('quit_key', quit_key)
            elif key_num == '@':
                color_cycle = ColorCycle(line)
                for key in keys:
                    key.set_color_cycle(color_cycle)
            else:
                color_cycle = ColorCycle(line)
                key = keys[hex2int(key_num)]
                key.set_color_cycle(color_cycle)
        except Exception as e:
            #https://docs.circuitpython.org/en/latest/shared-bindings/traceback/index.html
            error = ''.join(traceback.format_exception(etype=Exception, value=e, tb=e.__traceback__))
            error = '! ' + error.strip().replace('\n', '\n! ')
            pln(error)
#             print(bytes(error, 'utf-8'))
#             traceback.print_exception(etype=Exception, value=e, tb=e.__traceback__)

    for i, key in enumerate(keys):
        h = int2hex(i)
        if key.just_pressed:
            pln('+' + h)
            if current_page == 'None':
                if h == '0' and not audio.playing:
                    print("playing!")
                    audio.play(decoder)
                if h == 'F':
                    goto_none_page()
                    pln('@')
            if h == quit_key:
                goto_none_page()
                quit_key = None
        if key.just_released:
            pln('-' + h)




