import cv2
import numpy as np

pipe = '"rtspsrc location=\"rtsp://admin:password@192.168.1.65:554/Streaming/Channels/400" latency=10 ! appsink'

cap = cv2.VideoCapture(pipe)

if not cap.isOpened():
    print('VideoCapture not opened')
    exit(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print('empty frame')
        break

    cv2.imshow('display', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cap.release()

cv2.destroyAllWindows()