# StreamPico
Use your [Raspberry Pi Pico RGB Keypad](https://shop.pimoroni.com/products/pico-rgb-keypad-base) to control [OBS](https://obsproject.com/) (or anything!) over bluetooth.

## Linux Setup
Install Python 3 and Git:
```bash
sudo apt install python3 git #debian/ubuntu based systems
sudo pacman -Syy python3 git #arch based systems
```

Set up bluetooth (skip if bluetooth already works):
```bash
yay -S bluez-utils-compat #only needed on Manjaro
rfkill unblock bluetooth
sudo systemctl restart bluetooth
```

## Windows Setup
 - install python from [python.org](https://www.python.org/downloads/windows/)
 - install git from [git-scm.com](https://git-scm.com/download/win)
 - install C++ from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (needed for compiling a python package)

## Common Setup
Go to bluetooth settings and pair the device. It should show up as `HC-06`, and the PIN is `1234`. (You can change the device name and PIN by sending serial commands to the HC-06 bluetooth module, but that is not needed for now.)

Open a terminal in Linux, or open "Git Bash" in Windows and run these commands:
```bash
git clone https://codeberg.org/johanvandegriff/StreamPico
cd StreamPico
pip install virtualenv
python -m virtualenv .venv
source .venv/*/activate
pip install -r requirements.txt

python talk_to_pico.py
```

On Windows, if you don't have Git Bash, you can use cmd, and instead of `source .venv/*/activate`, you can do: `.\.venv\Scripts\activate`
