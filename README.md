# StreamPico
Use your Raspberry Pi Pico RGB Keypad to control OBS (or anything!) over bluetooth

## Bluetooth Serial on Arch

https://wiki.archlinux.org/title/Bluetooth#Bluetooth_serial

pip install git+https://github.com/pybluez/pybluez
rfkill unblock bluetooth
yay -S bluez-utils-compat
sudo systemctl restart bluetooth
bluetoothctl
```
[bluetooth] power on
[bluetooth] agent on
[bluetooth] scan on
[bluetooth] scan off
[bluetooth] pair 98:D3:31:FD:5D:34
```
sudo rfcomm bind 0 98:D3:31:FD:5D:34

./talk_to_pico.py



to remove:
sudo rfcomm unbind 0
bluetoothctl
```
[bluetooth] remove 98:D3:31:FD:5D:34
```
