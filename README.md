# Baby Pi

This is a simple app to use to control my Amcrest IP cameras being used
as baby monitors.  Technically, there is nothing baby monitor specific here.

This is intended to run on a Raspberry Pi with touchscreen
to work as a portable monitor.

It is being built and tested on Raspbian Jessie on a Pi 3.


# Raspbian package dependencies:


# Setup

## Apt packages
apt-get update
sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
   pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   python-setuptools libgstreamer1.0-dev git-core \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} python-dev libmtdev-dev \
   xclip omxplayer


## Python packages

pip install -r requirements.txt


## Configure kivy to use the official Raspberry Pi touch display:

Add the following to ~/.kivy/config.ini

[mouse]  
mouse = mouse  
mtdev_%(name)s = probesysfs,provider=mtdev  
hid_%(name)s = probesysfs,provider=hidinput  

## LXDE config, Screen blanking, etc.

### screen blanking and touchscreen backlight power
Depending on window manager (or lack thereof), etc. screen blanking is different
and can seem inconsistent.  Currently I prefer to load into pixel/lxde as I have found
this to be the most consistent.

Currently I am allowing dpms in X to turn the display off.  This appears to be
cutting power to the touchscreen backlight even though /sys/class/backlight/rpi_backlight/bl_power
says the power is still on.  If I find I am wrong, I will just turn off dpms and let the babymonitor
app manage the bl_power file itself.

@lxpanel --profile LXDE  
@pcmanfm --desktop --profile LXDE  
#@xscreensaver -no-splash  
@xset s off  
@xset dpms 0 0 300  
@xset s noblank  


### LXDE desktop icon
I added a desktop icon to LXDE by creating the file ~/Desktop/baby-pi.desktop with the following:

[Desktop Entry]  
Name=BabyPi  
Type=Application  
Comment=Run BabyPi  
Categories=Application  
Path=/home/pi/dev/babymonitor/baby_pi  
Exec=/home/pi/.pyenv/versions/babymonitor/bin/python main.py  
Terminal=false  
StartupNotify=false  



## Development configuration

Add the following to ~/.kivy/config.ini

[graphics]  
show_cursor = 1  

[modules]  
touchring = show_cursor=true  
cursor =  


The blank after the = in the modules section is correct.  Kivy appears
to be undergoing some internal changes and there is some voodoo at work
to make the mouse cursor show up for easy use with keyboard and mouse for dev.

# TODO

* Give this a better name?
* Try some slide out menus and multiple screens using dispmanx to layer
  kivy over omxplayer:
  http://codedesigner.de/articles/omxplayer-kivy-overlay/index.html
  https://github.com/kivy/kivy/pull/4984
* Possibly control omxplayer with dbus using python-omxplayer-wrapper.  There is a pull request
  with work towards making use of the --dbus_name flag to allow control of multiple
  omxplayer instances.  https://github.com/willprice/python-omxplayer-wrapper/pull/89
