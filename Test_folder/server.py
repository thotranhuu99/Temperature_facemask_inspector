import cv2
import socket
import numpy as np
import os

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.100.6", 5002)
sock.bind(server_address)
i = 0
while True:
    data, client_address = sock.recvfrom(10240)
    # print(data)
    print(client_address)
    serialized_bytes = np.frombuffer(data, dtype=np.uint16)
    image_received = np.reshape(serialized_bytes, newshape=(60, 80))
    cv2.imwrite(os.path.join('/mnt/ramdisk', 'temp_image.png'), image_received)
    # img = cv2.imread('Test.png', -1)
    # cv2.imshow('Window 1', img)
    k = cv2.waitKey(100) & 0xFF
    if k == 27:
        break
