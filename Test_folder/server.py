import subprocess
import cv2
import socket
import numpy as np
import os

Bash_convert_script_location = os.path.join(os.getcwd(), "Convert_to_normal.sh")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.100.6", 5002)
sock.bind(server_address)
while True:
    data, client_address = sock.recvfrom(10240)
    # print(data)
    print(client_address)
    serialized_bytes = np.frombuffer(data, dtype=np.uint16)
    raw_image_received = np.reshape(serialized_bytes, newshape=(60, 80))
    cv2.imwrite(os.path.join('/mnt/ramdisk', 'temp_image.png'), raw_image_received)
    rc = subprocess.call(Bash_convert_script_location, shell=True)
    img_converted = cv2.imread("y.png")
    cv2.imshow('Window 1', img_converted)
    k = cv2.waitKey(100) & 0xFF
    if k == 27:
        break
