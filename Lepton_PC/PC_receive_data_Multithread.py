import cv2
import socket
import numpy as np
import os
import time


def default_temp(pixel_value):
    temperature = pixel_value / 100 - 273.3
    return temperature


class Connection:
    Server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    Client_address = ["", int()]
    Server_address = ("192.168.100.255", 5002)
    Received_data = bytearray()


class ThermRawImg:
    Serialized_bytes_received = np.empty(4800, dtype=np.uint16)
    Img_received = np.empty([60, 80], dtype=np.uint16)
    High_threshold = 31000  # 36.7 degree Celsius default formula
    Low_threshold = 30000  # 26.7 degree Celsius default formula


class ThermProImg:
    Body_range = np.empty([60, 80], dtype=np.uint16)
    Norm = np.empty([60, 80], dtype=np.uint8)
    Size = (800, 600)
    Norm_resize = np.empty([800, 600], dtype=np.uint8)
    Norm_resize_color = np.empty([800, 600, 3], dtype=np.uint8)


def nothing():
    pass


Connection.Server_sock.bind(Connection.Server_address)
cv2.namedWindow("Thermal window")
cv2.createTrackbar('Low', "Thermal window", 400, 2000, nothing)
cv2.createTrackbar('High', "Thermal window", 1000, 2000, nothing)
while True:
    start_time = time.time()
    Connection.Received_data, Connection.Client_address = Connection.Server_sock.recvfrom(10240)
    print(Connection.Client_address)
    ThermRawImg.Serialized_bytes_received = np.frombuffer(Connection.Received_data, dtype=np.uint16)
    ThermRawImg.Img_received = np.reshape(ThermRawImg.Serialized_bytes_received, newshape=(60, 80))
    print(" Max_val = %d" % (np.amax(ThermRawImg.Img_received)))
    print("Raw temp = %.2f" % (default_temp(np.amax(ThermRawImg.Img_received))))
    cv2.imwrite(os.path.join('/mnt/ramdisk', 'temp_image.png'), ThermRawImg.Img_received)
    ThermRawImg.Low_threshold = cv2.getTrackbarPos('Low', 'Thermal window') + 30000
    ThermRawImg.High_threshold = cv2.getTrackbarPos('High', 'Thermal window') + 30000
    ThermProImg.Body_range = np.clip(ThermRawImg.Img_received, a_min=ThermRawImg.Low_threshold,
                                     a_max=ThermRawImg.High_threshold)
    ThermProImg.Norm = ((ThermProImg.Body_range - ThermRawImg.Low_threshold) /
                        (ThermRawImg.High_threshold - ThermRawImg.Low_threshold)*255).astype(np.uint8)
    ThermProImg.Norm_resize = cv2.resize(ThermProImg.Norm, ThermProImg.Size,
                                         interpolation=cv2.INTER_AREA)
    ThermProImg.Norm_resize_color = cv2.applyColorMap(ThermProImg.Norm_resize, cv2.COLORMAP_TURBO)
    cv2.imshow('Thermal window', ThermProImg.Norm_resize_color)
    stop_time = time.time()
    print("{}".format(stop_time-start_time))
    k = cv2.waitKey(100) & 0xFF
    if k == 27:
        break
