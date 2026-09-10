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

    cv2.imshow("Video", resize_frame)

    if cv2.waitKey(int(1000/actual_fps)) & 0xFF == ord('q'):
        break

print("Total frames processed: ", frame_count)
video.release()
cv2.destroyAllWindows()