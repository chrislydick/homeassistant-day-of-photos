#!/usr/bin/bash

rm -f /home/pi/images/*

python /home/pi/rotate_images.py

ssh -p 22222 root@192.168.1.146 'rm -f /media/*.jpg'

scp -P 22222 /home/pi/images/*.jpg root@192.168.1.146:/media/.
