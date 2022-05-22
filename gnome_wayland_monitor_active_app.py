import subprocess

proc = subprocess.Popen(['dbus-monitor'],stdout=subprocess.PIPE)
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
        print(app)
        break
