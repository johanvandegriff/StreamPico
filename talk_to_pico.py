#!/usr/bin/python3
import subprocess
import serial
import time
import traceback
from queue import Queue
from threading import Thread


start_page = '1'
current_page = start_page
OBS_PASSWORD='1234' #TODO

pages = {
    '1': {
#         'color': 'RGB,255,0,0',
        'keys': {
            '0': {
                #'colors': ['RGB,255,0,0', 'RGB,255,255,255'],
                'colors': {
                    None: 'RGB,128,128,0',
                    'lights off! (toggled)': 'RGB,128,0,0',
                    'lights on! (toggled)': 'RGB,255,255,255',
                },
                'action': {
                    'type': 'command',
                    'parameters': ['/home/user/nextcloud/bin/lights-toggle'],
                },
            },
            '1': {
                'colors': {
                    None: 'RGB,128,128,0',
                    'relay off! (toggled)': 'RGB,128,0,0',
                    'relay on! (toggled)': 'RGB,255,255,255',
                },
                'action': {
                    'type': 'command',
                    'parameters': ['/home/user/nextcloud/bin/relay-toggle'],
                },
            },
            #'4': {
                #'colors': 'RGB,128,0,128',
                #'action': {
                    #'type': 'command',
                    #'parameters': ['/home/user/nextcloud/bin/weznethack'],
                #},
            #},
            #'5': {
                #'colors': 'RGB,0,0,128',
                #'action': {
                    #'type': 'command',
                    #'parameters': ['/home/user/nextcloud/bin/weznethack', 'number_pad'],
                #},
            #},
            'E': {
                'colors': 'RGB,0,0,255',
                'action': {
                    'type': 'set_page',
                    'parameters': ['None'],
                },
            },
            'F': {
                'colors': 'RGB,0,255,0',
                'action': {
                    'type': 'set_page',
                    'parameters': ['2'],
                },
            },
        },
        'quit': 'E', #a special action that is managed on the device
    },
    '2': {
        'color': 'RGB,255,0,255',
        'keys': {
            '0': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'cam+chat'],
                },
            },
            '1': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'screen+cam+chat'],
                },
            },
            '2': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', '1080+cam+chat+vmpk'],
                },
            },
            '3': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'split screen'],
                },
            },
            '4': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'be right back'],
                },
            },
            '5': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'stream ending'],
                },
            },
            '6': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'vine'],
                },
            },
            '7': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'airhorn'],
                },
            },
            '8': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'sir vander'],
                },
            },
            '9': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', 'sir vander cam'],
                },
            },
            #'A': {
                #'action': {
                    #'type': 'command',
                    #'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', '?'],
                #},
            #},
            #'B': {
                #'action': {
                    #'type': 'command',
                    #'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'scene', 'switch', '?'],
                #},
            #},
            #'8': {
                #'colors': 'RGB,0,0,0',
            #},
            #'9': {
                #'colors': 'RGB,0,0,0',
            #},
            'A': {
                'colors': 'RGB,0,0,0',
            },
            'B': {
                'colors': 'RGB,0,0,0',
            },
            'C': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'source', 'toggle-mute', 'komplete desktop'],
                },
            },
            'D': {
                'action': {
                    'type': 'command',
                    'parameters': ['obs-cli', '--password', OBS_PASSWORD, 'source', 'toggle-mute', 'komplete mic'],
                },
            },
            'E': {
                'colors': 'RGB,0,0,255',
                'action': {
                    'type': 'set_page',
                    'parameters': ['1'],
                },
            },
            'F': {
                'colors': 'RGB,0,0,0',
            },
        },
    },
}


apps_to_page_mapping = {
    'org.wezfurlong.wezterm.desktop': '1',
    'librewolf.desktop': '1',
    'org.kde.kate.desktop': '2',
    'org.kde.dolphin.desktop': '2',
    'com.obsproject.Studio.desktop': '2',
}


#new thread to listen to gnome events and find when the active window changes
#so that the keypad can change context based on the active window
def monitor_active_app():
    proc = subprocess.Popen(['dbus-monitor'], stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline().decode('utf-8')
        if "member=RunningApplicationsChanged" in line:
            #print(line)
            last4 = ["", "", "", ""]
            while True:
                line = proc.stdout.readline().decode('utf-8')
                last4.append(line)
                last4.pop(0)
                if "active-on-seats" in line:
                    app = last4[0].split('"')[1]
                    q.put(app)
                    break

q = Queue()
t = Thread(target=monitor_active_app)
t.daemon = True
t.start()





ser = serial.Serial('/dev/rfcomm0', 9600)

"""
try:
    ser = serial.Serial('/dev/rfcomm0', 9600)
except serial.serialutil.SerialException:
    output = subprocess.Popen(['sudo', 'rfcomm', 'bind', '0', '98:D3:31:FD:5D:34'], stdout=subprocess.PIPE ).communicate()[0]
    print('output:', output)
    #os.system('sudo rfcomm bind 0 98:D3:31:FD:5D:34')
    time.sleep(2) #minimum 0.2
    #time.sleep(0.5) #minimum 0.2
    ser = serial.Serial('/dev/rfcomm0', 9600)
"""
#"""

def pln(s):
    print('SEND', s)
    ser.write(bytes(f"{s}\r\n", 'utf-8'))

def gln():
    line = ser.readline().decode('utf-8').strip()
    print('RECEIVE', line)
    return line

def activate_page():
    print('activate page', current_page)
    if not current_page in pages:
        print(f'page {current_page} not found')
        return
    page = pages[current_page]
    color = 'RGB,0,0,0'
    if 'color' in page:
        color = page['color']
    pln('@,'+color)
    if 'keys' in page:
        for key, data in page['keys'].items():
            colors = data.get('colors')
            action = data.get('action')
            if type(colors) == list:
                pln(key+','+colors[0]) #TODO
            elif type(colors) == dict:
                pln(key+','+colors[action.get('last_output')])
            elif colors is not None:
                pln(key+','+colors)
    if 'quit' in page:
        pln('Q,'+page['quit'])
    else:
        pln('Q,None')
    

send_init = True
while True:
    if not q.empty():
        app = q.get()
        new_page = apps_to_page_mapping.get(app)
        print('APP', app, 'PAGE', new_page)
        if new_page is not None and new_page != current_page:
            current_page = new_page
            activate_page()
    try:
        if send_init:
            pln("?")
            send_init = False
        if ser.inWaiting() > 0:
            line = gln()
        else:
            time.sleep(0.05)
            continue
        if line == '@':
            pln("#,"+start_page)
#             send_init = True
#         print('line[0]', line[0])
        if line[0] == '?':
            current_page = line.split(',')[1]
            activate_page()
        if line[0] == '+':
            key = line[1]
            if current_page in pages and key in pages[current_page]['keys']:
                action = pages[current_page]['keys'][key].get('action')
                if action is not None:
                    print('action', action, 'type', type(action))
                    if action['type'] == 'set_page':
                        pln('#'+',' + ','.join(action['parameters']))
                    elif action['type'] == 'command':
                        print('command', action['parameters'])
                        output = subprocess.Popen(action['parameters'], stdout=subprocess.PIPE ).communicate()[0]
                        print('output', output)
                        pages[current_page]['keys'][key]['action']['last_output'] = output.decode('utf-8').strip()
                        activate_page() #TODO dont update the whole page
                    else:
                        raise Exception('unsupported action type ' + action['type'])
#         if line == '+0':
#             os.system("echo /home/user/nextcloud/bin/lights-toggle &")
#         if line[0] == '+':
# #             pln(line[1]+',RGB,255,255,255')
#             pln(line[1]+',BLI,1,RGB,255,255,255,0.1')
# #             pln(line[1]+'BLI001RGB2552552550.1') #without commas, everthing is 3 wide
# #            pln('A,HSV,0.5,0,1')
#         if line[0] == '-':
# #             pln(line[1]+',RGB,255,0,255')
# #             pln(line[1]+',BLI,3,RGB,255,0,0,1.1,RGB,0,255,0,0.5,RGB,0,0,255,2.2')
#             if line[1] in ('A', 'B', 'E', 'F'):
#                 pln(line[1]+',PUL,2,RGB,0,255,0,1.1,RGB,255,0,0,0.5')
#             else:
#                 pln(line[1]+',FAD,2,RGB,0,255,0,1.1,RGB,255,0,0,0.5')
# #                 pln(line[1]+',PUL,2,RGB,255,0,0,1.1,RGB,0,255,0,0.5')
# #             pln(line[1]+',FAD,3,RGB,255,0,0,1.1,RGB,0,255,0,0.5,RGB,0,0,255,2.2')
# #             pln(line[1]+',FAD,2,RGB,0,255,0,0.5,RGB,0,0,0,2.2')
# #             pln(line[1]+'RAN003RGB255000000101RGB0002550000.5RGB0000002552.2')
# #            pln('A,HSV,0.9,0.9,0.9')
    except (serial.serialutil.SerialException, OSError) as e:
        #print(e)
        print(traceback.format_exc())
        #time.sleep(1)
        ser = serial.Serial('/dev/rfcomm0', 9600)
        send_init = True
