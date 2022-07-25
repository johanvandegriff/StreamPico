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
import obswebsocket, obswebsocket.requests

try:
    import pygetwindow
except:
    #TODO contribute Linux (X11 and wayland) and Mac support to pygetwindow
    pass

# https://newbedev.com/reliably-detect-windows-in-python
is_linux = platform.system() == 'Linux'

DEFAULT_BLUETOOTH_NAME = 'HC-06'
CONFIG_DIR = os.path.join(appdirs.user_config_dir(roaming=True), 'StreamPico')
CONFIG_FILE = CONFIG_DIR + '/config.json'

if not os.path.exists(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'pages': {'mypage': {'color': 'RGB,255,255,255'}}}, f, indent=4)

#TODO use more colors in example config: 'RGB', 'HSV', 'BLI', 'RAN', 'FAD', 'PUL'
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

#TODO break code into modules: bluetooth, command parsing, page switching, command running, obs
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


obs_websocket_ip = config.get('obs_websocket_ip', 'localhost')
obs_websocket_port = config.get('obs_websocket_port', '4444')
obs_websocket_password = config.get('obs_websocket_password', '')

try:
    obs_client = obswebsocket.obsws(obs_websocket_ip, obs_websocket_port, obs_websocket_password)
    obs_client.connect()
    print('obs-websocket version:', obs_client.call(obswebsocket.requests.GetVersion()).getObsWebsocketVersion())
except obswebsocket.exceptions.ConnectionFailure as e:
    #[Errno 111] Connection refused
    #Authentication Failed.
    print(traceback.format_exc())
    print('Continuing without OBS connection')
    obs_client = None

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
                    idx = action.get('idx', 0) #TODO only cycle when pressed, not when page re-renders
                    pln(key+','+colors[idx]) #cycle thru when pressed
                    action['idx'] = (idx + 1) % len(colors)
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


def expand_parameters(parameters, constants):
    new_parameters = []
    for param in parameters:
        if type(param) == dict:
            constant = param.get('constant')
            if not constant in constants:
                print(f'warning: constant {constant} not defined, putting {constant} literally instead')
            new_parameters.append(constants.get(constant, constant))
        elif type(param) == list:
            new_parameters.append(expand_parameters(param, constants)) #explore recursively
        else:
            new_parameters.append(param)
    return new_parameters

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
            pln('?')
            send_init = False

        if (line := gln()) is None:
            continue

        #TODO handle line not having enough items
        if line[0] == '.':
            pln('.')
        elif line[0] == '@':
            pln('#,'+START_PAGE)
        elif line[0] == '?':
            current_page = line.split(',')[1]
            activate_page()
        elif line[0] == '+':
            key = line[1]
            action = pages.get(current_page, {}).get('keys', {}).get(key, {}).get('action')
            if action is not None:
                output = None
                action_type = action.get('type')
                parameters = expand_parameters(action.get('parameters', []), constants)
                print('action:', action)
                print('parameters:', parameters)
                if action_type == 'set_page':
                    pln('#'+',' + ','.join(action['parameters']))
                elif action_type == 'command':
                    try:
                        output = subprocess.Popen(parameters, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip() #TODO non blocking option
                    except Exception as e:
                        output = str(e)
                        print(traceback.format_exc())
                elif action_type == 'obs': #high level convenient interface to OBS, inspired by obs-cli, mostly not implemented
                    supported = False
                    if parameters[0] == 'scene':
                        if parameters[1] == 'switch':
                            if obs_client is not None: obs_client.call(obswebsocket.requests.SetCurrentScene(parameters[2]))
                            supported = True
                    elif parameters[0] == 'source':
                        if parameters[1] == 'toggle-mute':
                            if obs_client is not None:
                                obs_client.call(obswebsocket.requests.ToggleMute(parameters[2]))
                                output = str(obs_client.call(obswebsocket.requests.GetMute(parameters[2])).getMuted())
                            supported = True
                    if not supported:
                        raise Exception(f'unsupported obs action {action}') #TODO avoid crashing here
                elif action_type == 'obs_websocket': #low level generic interface to OBS websocket API, fully implemented
                    if obs_client is None:
                        print('obs is not connected, skipping obs_websocket command')
                        #TODO try to reconnect when OBS is launched (need to detect launch somehow)
                    else:
                        #parameters: [['function', 'return', 'arg1', 'arg2', ...], ['function', 'return', 'arg1', 'arg2', ...]]
                        for params in parameters:
                            try:
                                if len(params) == 0:
                                    pass
                                elif len(params) == 1:
                                    eval(f'obs_client.call(obswebsocket.requests.{params[0]}())')
                                    #example: ['ToggleStudioMode'] -> obs_client.call(obswebsocket.requests.ToggleStudioMode())
                                elif len(params) == 2:
                                    output = str(eval(f'obs_client.call(obswebsocket.requests.{params[0]}()).{params[1]}()'))
                                    #example: ['GetStudioModeStatus', 'getStudioMode'] -> obs_client.call(obswebsocket.requests.GetStudioModeStatus()).getStudioMode()
                                elif len(params) >= 3:
                                    args = params[2:] #remove the first 2 (function and return)
                                    quoted_args = str(args)[1:-1] #convert list to string and remove the []
                                    if params[1] == '':
                                        eval(f'obs_client.call(obswebsocket.requests.{params[0]}({quoted_args}))')
                                        #example: ['ToggleMute', '', 'my mic'] -> obs_client.call(obswebsocket.requests.ToggleMute("my mic"))
                                    else:
                                        output = str(eval(f'obs_client.call(obswebsocket.requests.{params[0]}({quoted_args})).{params[1]}()'))
                                        #example: ['GetMute', 'getMuted', 'my mic'] -> obs_client.call(obswebsocket.requests.GetMute("my mic")).getMuted()
                            except: #errors from eval are unpredictable
                                print(traceback.format_exc())
                else:
                    raise Exception('unsupported action type {action_type}') #TODO avoid crashing here
                print('output:', output)
                pages[current_page]['keys'][key]['action']['last_output'] = output
                activate_page() #TODO dont update the whole page
    except bluetooth.btcommon.BluetoothError as e: #TODO windows cannot detect bluetooth disconnect
        #TODO decide what to do when bluetooth is off: [Errno 113] No route to host
        if e.args[0] == 110: #[Errno 110] Connection timed out
            print(traceback.format_exc())
            print('Attempting to reconnect...')
            send_init = True
        else:
            raise e



