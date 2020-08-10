import socket
import cv2
import time
while True:
    img = cv2.imread("x.png", -1)
    b = bytearray(img)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b, ("192.168.100.6", 5002))
    print("Frame sent")
    time.sleep(0.1)
