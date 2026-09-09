import cv2

print("OpenCV version:", cv2.__version__)

image = cv2.imread('data/testImage.jpg')

if image is None:
    print("Error: Could not read the image.")
else:
    cv2.imshow('Test Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
