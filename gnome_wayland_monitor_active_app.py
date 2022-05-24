#!/usr/bin/python3
import subprocess

def readln(p):
    return p.stdout.readline().decode('utf-8')

def monitor_active_app(q=None):
    proc = subprocess.Popen(['dbus-monitor'],stdout=subprocess.PIPE)
    while True:
        #if the right function calls are on 2 consecutive lines
        if 'member=RunningApplicationsChanged' in readln(proc) and 'member=GetRunningApplications' in readln(proc):

            #search for the active window string, recording the previous string which is the window name
            last_line = None
            while not 'string "active-on-seats"' in (line := readln(proc)):
                if 'string "' in line:
                    last_line = line

            if last_line is not None:
                app = last_line.split('"')[1] #get the stuff between the quotes
                if q is not None:
                    q.put(app) #add it to the queue
                else:
                    print(app) #or print it if no queue provided

if __name__ == '__main__':
    monitor_active_app()

"""
Example event from dbus-monitor

$ dbus-monitor | grep 'member=RunningApplicationsChanged' -A 30
    ...
signal time=1653308837.299322 sender=:1.14 -> destination=(null destination) serial=629 path=/org/gnome/Shell/Introspect; interface=org.gnome.Shell.Introspect; member=RunningApplicationsChanged
method call time=1653308837.300012 sender=:1.65 -> destination=:1.14 serial=144 path=/org/gnome/Shell/Introspect; interface=org.gnome.Shell.Introspect; member=GetRunningApplications
method return time=1653308837.305183 sender=:1.14 -> destination=:1.65 serial=630 reply_serial=144
   array [
      dict entry(
         string "org.wezfurlong.wezterm.desktop"
         array [
         ]
      )
      dict entry(
         string "org.thonny.Thonny.desktop"
         array [
            dict entry(
               string "active-on-seats"
               variant                   array [
                     string "seat0"
                  ]
            )
         ]
      )
      dict entry(
         string "librewolf.desktop"
         array [
         ]
      )
      dict entry(
         string "rambox.desktop"
         array [
         ]
      )
      dict entry(
    ...
"""

