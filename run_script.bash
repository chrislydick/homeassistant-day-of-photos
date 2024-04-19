#!/usr/bin/bash

rm -f /home/pi/images/*

python /home/pi/rotate_images.py

ssh -p 22222 root@homeassistant.local 'rm -f /media/*.jpg'

scp -P 22222 /home/pi/images/*.jpg root@homeassistant.local:/media/.
