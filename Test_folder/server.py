import cv2
import socket
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("192.168.100.6", 5002)
sock.bind(server_address)
i = 0
while True:
    data, client_address = sock.recvfrom(10240)
    print(data)
    print(client_address)
    deserialized_bytes = np.frombuffer(data, dtype=np.uint16)
    image_data = np.reshape(deserialized_bytes, newshape=(60, 80))
    cv2.imwrite('Test.png', image_data)
    img = cv2.imread('Test.png', -1)
    i = i + 1
