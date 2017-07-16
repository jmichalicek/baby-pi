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

mouse = mouse
mtdev_%(name)s = probesysfs,provider=mtdev
hid_%(name)s = probesysfs,provider=hidinput


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
