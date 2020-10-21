import socket
import os
import time
import numpy as np


class Connection:
    Server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    Client_address = ["", int()]
    Server_address = ("127.0.0.1", 6000)
    Received_data = bytearray()


Connection.Server_sock.bind(Connection.Server_address)
while True:
    start_time = time.time()
    Connection.Received_data, Connection.Client_address = Connection.Server_sock.recvfrom(10240)
    stop_time = time.time()
    Serialized_bytes_received = np.frombuffer(Connection.Received_data, dtype=np.float)
    print(stop_time-start_time)
    #print(Serialized_bytes_received)
