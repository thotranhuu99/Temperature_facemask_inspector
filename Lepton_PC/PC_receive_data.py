import cv2
import socket
import numpy as np
import os
import time

class Connection:
    Server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    Client_address = ["", int()]
    Server_address = ("192.168.100.255", 5002)
    Received_data = bytearray()


class RawImg:
    Serialized_bytes_received = np.empty(4800, dtype=np.uint16)
    Img_received = np.empty([60, 80], dtype=np.uint16)
    High_threshold = 31000  # 40 degree Celsius


class ProcessedImg:
    Body_range = np.empty([60, 80], dtype=np.uint16)
    Normalized = np.empty([60, 80], dtype=np.uint8)

    Resize_size = (800, 600)
    Normalized_resized = np.empty([800, 600], dtype=np.uint8)
    Normalized_resized_colored = np.empty([800, 600, 3], dtype=np.uint8)



def nothing(x):
    pass


Connection.Server_sock.bind(Connection.Server_address)
cv2.namedWindow("Thermal window")
cv2.createTrackbar('Low', "Thermal window", 400, 2000, nothing)
cv2.createTrackbar('High', "Thermal window", 1000, 2000, nothing)
# Bash_convert_script_location = os.path.join(os.getcwd(), "Convert_to_normal.sh")

while True:
    start_time = time.time()
    Connection.Received_data, Connection.Client_address = Connection.Server_sock.recvfrom(10240)
    print(Connection.Client_address)
    RawImg.Serialized_bytes_received = np.frombuffer(Connection.Received_data, dtype=np.uint16)
    RawImg.Img_received = np.reshape(RawImg.Serialized_bytes_received, newshape=(60, 80))
    print(" Max_val = {}\n Raw temp = {}".format(np.amax(RawImg.Img_received), np.amax(RawImg.Img_received)/100-273.3))
    cv2.imwrite(os.path.join('/mnt/ramdisk', 'temp_image.png'), RawImg.Img_received)
    RawImg.Low_threshold = cv2.getTrackbarPos('Low', 'Thermal window') + 30000
    RawImg.High_threshold = cv2.getTrackbarPos('High', 'Thermal window') + 30000
    for i in range(RawImg.Img_received.shape[0]):
        for j in range(RawImg.Img_received.shape[1]):
            if RawImg.Img_received[i][j] >= RawImg.High_threshold:
                ProcessedImg.Body_range[i][j] = RawImg.High_threshold
            else:
                ProcessedImg.Body_range[i][j] = RawImg.Img_received[i][j]
    ProcessedImg.Normalized = (cv2.normalize(ProcessedImg.Body_range, None, 0, 255,
                                             cv2.NORM_MINMAX)).astype(np.uint8)
    ProcessedImg.Normalized_resized = cv2.resize(ProcessedImg.Normalized, ProcessedImg.Resize_size,
                                                 interpolation=cv2.INTER_AREA)
    ProcessedImg.Normalized_resized_colored = cv2.applyColorMap(ProcessedImg.Normalized_resized, cv2.COLORMAP_TURBO)
    cv2.imshow('Thermal window', ProcessedImg.Normalized_resized_colored)
    stop_time = time.time()
    print("{}".format(stop_time-start_time))
    k = cv2.waitKey(100) & 0xFF
    if k == 27:
        break
