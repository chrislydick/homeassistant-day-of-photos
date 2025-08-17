#!/usr/bin/bash

mkdir images/

python rotate_images.py

ssh -p 22222 root@192.168.1.146 'rm -f /media/*.jpg'

scp -P 22222 images/*.jpg root@192.168.1.146:/media/.
