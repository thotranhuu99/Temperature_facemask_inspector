import cv2

def nothing(x):
    pass

img = cv2.imread("test.png", cv2.IMREAD_GRAYSCALE)
cv2.namedWindow("Window 1")
cv2.namedWindow('Window 2')
cv2.createTrackbar('Thresh', "Window 1", 0, 255, nothing)
cv2.createTrackbar('Thresh', "Window 2", 0, 255, nothing)
while True:
    _, img_1 = cv2.threshold(img, cv2.getTrackbarPos('Thresh', 'Window 1'), 255, cv2.THRESH_TOZERO)
    _, img_2 = cv2.threshold(img, cv2.getTrackbarPos('Thresh', 'Window 2'), 255, cv2.THRESH_TOZERO_INV)
    cv2.imshow("Window 1", img_1)
    cv2.imshow("Window 2", img_2)
    k = cv2.waitKey(100) & 0xFF
    if k == 27:
        break
