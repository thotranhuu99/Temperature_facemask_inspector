import cv2
import os
Working_dir = os.getcwd()
Image_location = os.path.join(Working_dir, "flirpi", "y.png")
img = cv2.imread(Image_location, cv2.IMREAD_GRAYSCALE)
cv2.imshow('image', img)
cv2.waitKey(0)

