import cv2
import socket
import numpy as np
import os

Bash_convert_script_location = os.path.join(os.getcwd(), "Convert_to_normal.sh")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.100.255", 5002)
sock.bind(server_address)
while True:
    data, client_address = sock.recvfrom(10240)
    # print(data)
    # print(client_address)
    serialized_bytes = np.frombuffer(data, dtype=np.uint16)
    raw_image_received = np.reshape(serialized_bytes, newshape=(60, 80))
    print(" Max_val = {}\n Raw temp = {}".format(np.amax(raw_image_received), np.amax(raw_image_received)/100-273.3))
    cv2.imwrite(os.path.join('/mnt/ramdisk', 'temp_image.png'), raw_image_received)
    # rc = subprocess.call(Bash_convert_script_location, shell=True)
    # img_converted = cv2.imread("y.png")
    norm_img = np.zeros((60, 80))
    img_normalized = (cv2.normalize(raw_image_received, norm_img, 0, 255, cv2.NORM_MINMAX)).astype(np.uint8)
    img_normalized_resized = cv2.resize(img_normalized, (800, 600), interpolation=cv2.INTER_AREA)
    # img_normalized_colored = cv2.applyColorMap(img_normalized, cv2.COLORMAP_TURBO)
    # img_normalized_colored_resized = cv2.resize(img_normalized_colored, (800, 600), interpolation=cv2.INTER_AREA)
    cv2.imshow('Window 1', img_normalized_resized)
    k = cv2.waitKey(100) & 0xFF
    if k == 27:
        break
