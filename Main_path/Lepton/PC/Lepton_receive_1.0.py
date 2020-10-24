import cv2
import socket
import numpy as np
import time


class RaspberryLeptonConnection:
    Server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    Client_address = ["", int()]
    Server_address = ("192.168.31.255", 5002)
    Received_data = bytearray()


class CameraThreadConnection:
    Server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    Loopback_address = ("127.0.0.1", 6000)


class ThermImg:
    Serialized_bytes_received = np.empty(4800, dtype=np.uint16)
    Img_received = np.empty([60, 80], dtype=np.uint16)
    Calculated_temp = np.empty([60, 80], dtype=np.float)
    High_threshold = 31000  # 36.7 degree Celsius default formula
    Low_threshold = 30000  # 26.7 degree Celsius default formula


class ThermVisualizeImg:
    Body_range = np.empty([60, 80], dtype=np.uint16)
    Norm = np.empty([60, 80], dtype=np.uint8)
    Size = (400, 300)
    Norm_resize = np.empty([400, 300], dtype=np.uint8)
    Norm_resize_color = np.empty([400, 300, 3], dtype=np.uint8)


def nothing():
    pass


def default_temp(pixel_value):
    temperature = pixel_value / 100 - 273.3
    return temperature


def send_data_camera_thread(send_data, loopback_addr):
    CameraThreadConnection.Server_sock.sendto(send_data, loopback_addr)


def lepton_receive():
    RaspberryLeptonConnection.Server_sock.bind(RaspberryLeptonConnection.Server_address)
    cv2.namedWindow("Thermal window")
    cv2.createTrackbar('Low', "Thermal window", 400, 2000, nothing)
    cv2.createTrackbar('High', "Thermal window", 1000, 2000, nothing)
    while True:
        start_time = time.time()
        RaspberryLeptonConnection.Received_data, RaspberryLeptonConnection.Client_address \
            = RaspberryLeptonConnection.Server_sock.recvfrom(10240)
        send_data_camera_thread(RaspberryLeptonConnection.Received_data, CameraThreadConnection.Loopback_address)
        print(RaspberryLeptonConnection.Client_address)
        ThermImg.Serialized_bytes_received = np.frombuffer(RaspberryLeptonConnection.Received_data, dtype=np.uint16)
        ThermImg.Img_received = np.reshape(ThermImg.Serialized_bytes_received, newshape=(60, 80))
        ThermImg.Calculated_temp = default_temp(ThermImg.Img_received.astype(float))
        print("Max temp = {}".format(np.amax(ThermImg.Calculated_temp)))
        print("Min temp = {}".format(np.amin(ThermImg.Calculated_temp)))
        ThermImg.Low_threshold = cv2.getTrackbarPos('Low', 'Thermal window') + 30000
        ThermImg.High_threshold = cv2.getTrackbarPos('High', 'Thermal window') + 30000
        ThermVisualizeImg.Body_range = np.clip(ThermImg.Img_received, a_min=ThermImg.Low_threshold,
                                               a_max=ThermImg.High_threshold)
        ThermVisualizeImg.Norm = ((ThermVisualizeImg.Body_range - ThermImg.Low_threshold) /
                                  (ThermImg.High_threshold - ThermImg.Low_threshold) * 255).astype(np.uint8)
        ThermVisualizeImg.Norm_resize = cv2.resize(ThermVisualizeImg.Norm, ThermVisualizeImg.Size,
                                                   interpolation=cv2.INTER_AREA)
        ThermVisualizeImg.Norm_resize_color = cv2.applyColorMap(ThermVisualizeImg.Norm_resize, cv2.COLORMAP_INFERNO)
        cv2.imshow('Thermal window', ThermVisualizeImg.Norm_resize_color)
        stop_time = time.time()
        print("Loop time: {} (s)".format(stop_time-start_time))
        k = cv2.waitKey(100) & 0xFF
        if k == 27:
            break


if __name__ == "__main__":
    lepton_receive()
