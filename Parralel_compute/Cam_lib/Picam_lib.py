import cv2
import subprocess
import concurrent.futures
import os


def receive_camera():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        f1 = executor.submit(read_fifo)
        f2 = executor.submit(img_processing)


def read_fifo():
    path = os.path.abspath(__file__)
    command_location = os.path.join(os.path.dirname(path), "readMkFifoStream.sh")
    print(command_location)
    subprocess.call(command_location)


def img_processing():
    print('test_3')
    while True:
        img = cv2.imread('/mnt/ramdisk/out.bmp')
        try:
            cv2.imshow('Window 1', img)
        except Exception:
            print('Frame skipped')
        finally:
            pass
        k = cv2.waitKey(50)
        if k == 27:  # wait for ESC key to exit
            break
    cv2.destroyAllWindows()
