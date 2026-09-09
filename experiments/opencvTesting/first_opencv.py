import cv2

print("OpenCV version:", cv2.__version__)

image = cv2.imread('data/testingOpenCV/testImage.jpg')

if image is None:
    print("Error: Could not read the image.")
else:
    """Resizing Image to fit screen"""
    resize_image = cv2.resize(image, (600, 600))

    """Open BGR image in a window"""
    #cv2.imshow('Test Image', image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    """Getting the height, width, number of colour channels and data type of the image"""
    print("Image height: ", image.shape[0])
    print("Image width: ", image.shape[1])
    print("Colour channels: ", image.shape[2])
    print("Image data type: ", image.dtype)

    """Greyscale conversion"""
    grey_image = cv2.cvtColor(resize_image, cv2.COLOR_BGR2GRAY)
    # print("Grey image height: ", grey_image.shape[0])
    # print("Grey image width: ", grey_image.shape[1])
    # print("Grey image data type: ", grey_image.dtype)

    """Cropping the image"""
    # cropped_image = image[250:1000, 100:700]
    # print("Cropped image height: ", cropped_image.shape[0])
    # print("Cropped image width: ", cropped_image.shape[1])

    """Blurring the image"""
    # blurred_image = cv2.GaussianBlur(resize_image, (21,21), 0)
    # print("Blurred image height: ", blurred_image.shape[0])
    # print("Blurred image width: ", blurred_image.shape[1])

    """Thresholding the image"""
    # _, threshold_image = cv2.threshold(grey_image, 80, 255, cv2.THRESH_BINARY)
    # print("Threshold image height: ", threshold_image.shape[0])
    # print("Threshold image width: ", threshold_image.shape[1])

    """Edge detection using Canny algorithm"""
    cannyEdge_image = cv2.Canny(grey_image, 100, 200)

    """Edge detection using Sobel algorithm"""
    sobel_image_x = cv2.Sobel(grey_image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_image_y = cv2.Sobel(grey_image, cv2.CV_64F, 0, 1, ksize=3)
    sobel_image = cv2.magnitude(sobel_image_x, sobel_image_y)
    sobel_image = cv2.convertScaleAbs(sobel_image)

    while True:
        #cv2.imshow('Grey Image', grey_image)
        #cv2.imshow('Cropped Image', cropped_image)
        #cv2.imshow('Blurred Image', blurred_image)
        #cv2.imshow('Threshold Image', threshold_image)
        cv2.imshow('Canny Edge Image', cannyEdge_image)
        cv2.imshow('Sobel Image', sobel_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
