#!/usr/bin/env zsh

m=$(mount | grep /Volumes/CIRCUITPY | grep synchronous)

if [ ! "$m" ]; then
  devname=$(df | grep CIRCUITPY | cut -d" " -f1)
  sudo umount /Volumes/CIRCUITPY
  sudo mkdir /Volumes/CIRCUITPY
  sleep 2
  sudo mount -v -o sync -t msdos $devname /Volumes/CIRCUITPY
fi