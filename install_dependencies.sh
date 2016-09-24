#!/bin/sh

sudo apt-get install einstein
sudo apt-get install xautomation    # need xte command
sudo apt-get install x11-utils      # need xwininfo command
sudo apt-get install wmctrl
sudo apt-get install imagemagick

unalias cp
cp -f einsteinrc ~/.einstein/einsteinrc


