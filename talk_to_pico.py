#!/usr/bin/env python
import os
import subprocess
import bluetooth
import time
import traceback
from queue import Queue
from threading import Thread
import json
import platform
import appdirs

try:
    import pygetwindow
except:
    #TODO contribute Linux (X11 and wayland) and Mac support to pygetwindow
    pass

# https://newbedev.com/reliably-detect-windows-in-python
is_linux = platform.system() == 'Linux'

DEFAULT_BLUETOOTH_NAME = 'HC-06'
CONFIG_DIR = appdirs.user_config_dir()+'/StreamPico'
CONFIG_FILE = CONFIG_DIR + '/config.json'

if not os.path.exists(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'pages': {'mypage': {'color': 'RGB,255,255,255'}}}, f, indent=4)

#TODO documentation for configs, some example configs
#TODO ui to change config
with open(os.path.expanduser(appdirs.user_config_dir()+'/StreamPico/config.json'), 'r') as f:
    config = json.load(f)
    constants = config.get('constants', {})
    switch_on_active_app = config.get('switch_on_active_app') == True
    pages = config.get('pages', {})
    first_page = list(pages.keys())[0] if len(pages) else None
    START_PAGE = config.get('start_page', first_page) #start with the first page if none specified
    current_page = START_PAGE

apps_to_page_mapping = {}
for page, v in pages.items():
    apps = v.get('apps')
    if apps is not None:
        for app in apps:
            apps_to_page_mapping[app] = page


q = Queue()
if switch_on_active_app and is_linux:
    from gnome_wayland_monitor_active_app import monitor_active_app
    #new thread to listen to gnome events and find when the active window changes
    #so that the keypad can change context based on the active window
    t = Thread(target=monitor_active_app, args=[q])
    t.daemon = True
    t.start()

def find_device_by_name(name):
  print(f'searching for bluetooth device "{name}"...')
  for addr in bluetooth.discover_devices():
    print(f'found "{addr}", checking name...')
    if name == bluetooth.lookup_name(addr):
      print('name matches!')
      return addr
  print('no matches found')
  raise Exception(f'Bluetooth device {name} not found')


if 'bluetooth_addr' in config:
  BLUETOOTH_ADDR = config['bluetooth_addr']
else:
  BLUETOOTH_ADDR = find_device_by_name(config.get('bluetooth_name', DEFAULT_BLUETOOTH_NAME))

def pln(s):
    print('SEND', s)
    sock.send(bytes(f'{s}\r\n', 'utf-8'))

RECV_DATA = b''
def gln():
    global RECV_DATA
    try:
        RECV_DATA += sock.recv(1024)
    except bluetooth.btcommon.BluetoothError as e: #Linux
        if e.args[0] != 'timed out':
            raise e
    except OSError as e:
        if not 'did not properly respond after a period of time' in e.args[0]: #Windows
            raise e
    if b'\r\n' not in RECV_DATA:
        return None
    lines = RECV_DATA.split(b'\r\n')
    line = lines[0].decode('utf-8')
    lines = lines[1:] #delete the 1st
    RECV_DATA = b'\r\n'.join(lines)
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
                if len(colors) > 0:
                    index = action.get('index', 0)
                    pln(key+','+colors[index]) #TODO test: cycle thru when pressed
                    action['index'] = (index + 1) % len(colors)
            elif type(colors) == dict:
                last_output = str(action.get('last_output'))
                if last_output in colors:
                    pln(key+','+colors[last_output])
            elif type(colors) == str:
                pln(key+','+colors)
    if 'quit' in page:
        pln('Q,'+page['quit'])
    else:
        pln('Q,None')


send_init = True
while True:
    if switch_on_active_app and not is_linux:
        q.put(pygetwindow.getActiveWindow().title)
    if not q.empty():
        app = q.get()
        new_page = apps_to_page_mapping.get(app) #TODO regex or glob especially needed on windows
        #TODO add an optional catchall page for apps not on any list
        #TODO pattern matching for apps
        #TODO add an action to set/toggle if app focus jumps to page
        print('APP', app, 'PAGE', new_page)
        if new_page is not None and new_page != current_page:
            current_page = new_page
            activate_page()
    try:
        if send_init:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((BLUETOOTH_ADDR, 1))
            sock.settimeout(0.05)
            pln("?")
            send_init = False

        if (line := gln()) is None:
            continue

        if line[0] == '.':
            pln('.')
        elif line[0] == '@':
            pln("#,"+START_PAGE)
        elif line[0] == '?':
            current_page = line.split(',')[1]
            activate_page()
        elif line[0] == '+':
            key = line[1]
            if key in pages.get(current_page, {}).get('keys', {}):
                action = pages[current_page]['keys'][key].get('action')
                if action is not None:
                    print('action', action, 'type', type(action))
                    if action['type'] == 'set_page':
                        pln('#'+',' + ','.join(action['parameters']))
                    elif action['type'] == 'command': #TODO direct obs-websocket support
                        print('command', action['parameters'])
                        parameters = []
                        for param in action['parameters']:
                            if type(param) == str:
                                parameters.append(param)
                            elif type(param) == dict:
                                constant = param['constant']
                                if not constant in constants:
                                    raise ValueError(f"constant {constant} not defined")
                                parameters.append(constants[constant])
                        try:
                            output = subprocess.Popen(parameters, stdout=subprocess.PIPE).communicate()[0] #TODO non blocking option
                        except Exception as e:
                            output = bytes(str(e), 'utf-8')
                            print(traceback.format_exc())
                        print('output', output)
                        pages[current_page]['keys'][key]['action']['last_output'] = output.decode('utf-8').strip()
                        activate_page() #TODO dont update the whole page
                    else:
                        raise Exception('unsupported action type ' + action['type'])
    except bluetooth.btcommon.BluetoothError as e: #TODO windows cannot detect bluetooth disconnect
        if e.args[0] == 110: #[Errno 110] Connection timed out
            print(traceback.format_exc())
            print("Attempting to reconnect...")
            send_init = True
        else:
            raise e



