import socket
import numpy as np
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
while True:
    temp_array = np.load('/mnt/ramdisk/temperature_array.npy')
    b = bytearray(temp_array)
    start_time = time.time()
    sock.sendto(b, ("127.0.0.1", 6000))
    end_time = time.time()
    print(end_time - start_time)
