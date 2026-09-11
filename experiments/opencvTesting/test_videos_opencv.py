import cv2
import time

video_path = "data/testingOpenCV/testVideo.mp4"
video = cv2.VideoCapture(video_path)

actual_fps = video.get(cv2.CAP_PROP_FPS)
print("Actual FPS of the video: ", actual_fps)

frame_count = 0
frame_count_function = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
print("Total frames in the video: ", frame_count_function)

duration = frame_count_function / actual_fps
print("Duration of the video (in seconds): ", duration)

prev_time = 0

while True:
    ret, frame = video.read()

    if not ret:
        break

    current_time = time.time()

   

    """Rotate frame by 180 degrees"""
    frame = cv2.rotate(frame, cv2.ROTATE_180)
    #print("Frame shape:", frame.shape)

    frame_count += 1

    """Calculating FPS"""
    fps = 1/(current_time-prev_time + 1e-6)
    prev_time = current_time
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    """Option 1 for resizing by half"""
    #resize_frame = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))

    """Option 2 for resizing by half"""
    resize_frame = cv2.resize(frame, None, fx = 0.5, fy = 0.5)

    """Convert to grayscale"""
    #grey_frame = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)

    """Blurring"""
    #blur_frame = cv2.GaussianBlur(resize_frame, (11,11), 0)

    """Cropping Frames"""
    #cropped_frame = resize_frame[100:600,200:900]

    """Threshold the frames"""
    #_, threshold_frame = cv2.threshold(grey_frame, 50, 255, cv2.THRESH_BINARY)

    """Edge detection"""
    """Canny Edge Detection"""
    #canny_frame = cv2.Canny(grey_frame, 60, 200)

    """Sobel Edge Detection"""
    #sobel_frame_x = cv2.Sobel(grey_frame, cv2.CV_64F, 1, 0, ksize=3)
    #sobel_frame_y = cv2.Sobel(grey_frame, cv2.CV_64F, 0, 1, ksize=3)
    #sobel_frame = cv2.magnitude(sobel_frame_x, sobel_frame_y)
    #sobel_frame = cv2.convertScaleAbs(sobel_frame)

    """Displaying the frames"""
    cv2.imshow("Video", resize_frame)
    #cv2.imshow("Grey Video", grey_frame)
    #cv2.imshow("Blurred Video", blur_frame)
    #cv2.imshow("Cropped Video", cropped_frame)
    #cv2.imshow("Threshold Video", threshold_frame)
    #cv2.imshow("Canny Edge Video", canny_frame)
    #cv2.imshow("Sobel Edge Video", sobel_frame)

    if cv2.waitKey(int(1000/actual_fps)) & 0xFF == ord('q'):
        break

print("Total frames processed: ", frame_count)
video.release()
cv2.destroyAllWindows()