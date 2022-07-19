#!/usr/bin/env python
import os
import subprocess
import bluetooth
import time
import traceback
from queue import Queue
from threading import Thread
from gnome_wayland_monitor_active_app import monitor_active_app
import json

with open(os.path.expanduser('~/.config/StreamPico.json'), 'r') as f:
    config = json.load(f)
    constants = config['constants']
    switch_on_active_app = config.get('switch_on_active_app') == True
    pages = config['pages']
    START_PAGE = config['start_page']
    current_page = START_PAGE

apps_to_page_mapping = {}
for page, v in pages.items():
    apps = v.get('apps')
    if apps is not None:
        for app in apps:
            apps_to_page_mapping[app] = page


#new thread to listen to gnome events and find when the active window changes
#so that the keypad can change context based on the active window
q = Queue()
if switch_on_active_app:
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
  return None


if 'bluetooth_addr' in config:
  BLUETOOTH_ADDR = config['bluetooth_addr']
else:
  BLUETOOTH_ADDR = find_device_by_name(config['bluetooth_name'])

def pln(s):
    print('SEND', s)
    sock.send(bytes(f'{s}\r\n', 'utf-8'))

RECV_DATA = b''
def gln():
    global RECV_DATA
    while b'\r\n' not in RECV_DATA:
      RECV_DATA += sock.recv(1024)
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
                pln(key+','+colors[0]) #TODO cycle thru when pressed
            elif type(colors) == dict:
                pln(key+','+colors[str(action.get('last_output'))])
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
            pln("?")
            send_init = False

        line = gln()

        if line[0] == '.':
            pln('.')
        elif line[0] == '@':
            pln("#,"+START_PAGE)
        elif line[0] == '?':
            current_page = line.split(',')[1]
            activate_page()
        elif line[0] == '+':
            key = line[1]
            if current_page in pages and key in pages[current_page]['keys']:
                action = pages[current_page]['keys'][key].get('action')
                if action is not None:
                    print('action', action, 'type', type(action))
                    if action['type'] == 'set_page':
                        pln('#'+',' + ','.join(action['parameters']))
                    elif action['type'] == 'command':
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
                        output = subprocess.Popen(parameters, stdout=subprocess.PIPE ).communicate()[0]
                        print('output', output)
                        pages[current_page]['keys'][key]['action']['last_output'] = output.decode('utf-8').strip()
                        activate_page() #TODO dont update the whole page
                    else:
                        raise Exception('unsupported action type ' + action['type'])
    except bluetooth.btcommon.BluetoothError as e:
        print(traceback.format_exc())
        send_init = True



