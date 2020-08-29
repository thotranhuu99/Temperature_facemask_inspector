import cv2

while True:
    img = cv2.imread('/mnt/ramdisk/out.bmp')
    try:
        cv2.imshow('Window 1', img)
    except:
        print('Frame skipped')
    finally:
        pass
    k = cv2.waitKey(50)
    if k == 27:  # wait for ESC key to exit
        break
cv2.destroyAllWindows()
