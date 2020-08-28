import io
import time
import picamera
from PIL import Image
import cv2
import numpy

def outputs():
    stream = io.BytesIO()
    for i in range(40):
        # This returns the stream for the camera to capture to
        yield stream
        # Once the capture is complete, the loop continues here
        # (read up on generator functions in Python to understand
        # the yield statement). Here you could do some processing
        # on the image...
        stream.seek(0)
        pil_image = Image.open(stream)
        #cv2.imread(img)
        #img_bytes = stream.read()
        # Finally, reset the stream for the next capture
        #print("{}".format(img))
        open_cv_image = numpy.array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        cv2.imwrite('test.jpg', open_cv_image)
        stream.seek(0)
        stream.truncate()


with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 80
    time.sleep(2)
    start = time.time()
    camera.capture_sequence(outputs(), 'jpeg', use_video_port=True)
    finish = time.time()
    print('Captured 40 images at %.2ffps' % (40 / (finish - start)))

