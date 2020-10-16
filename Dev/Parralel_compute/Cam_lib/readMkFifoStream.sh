#!/bin/bash
if [ -p /mnt/ramdisk/fifo ]
then
rm /mnt/ramdisk/fifo
fi
mkfifo /mnt/ramdisk/fifo
ffmpeg -y -i /mnt/ramdisk/fifo -f image2 -update 1 /mnt/ramdisk/out.bmp &
nc -u -n -k -l 5001 -v | cat  > /mnt/ramdisk/fifo && fg

