import cv2
from pathlib import Path
from datetime import datetime

pipeline = ("v4l2src device=/dev/video0 ! "
            "video/x-raw, width=1280, height=720, framerate=30/1 ! "
            "videoconvert ! "
            "video/x-raw, format=BGR ! "
            "appsink drop=true max-buffers=1")

camera = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

SAVE_DIR = Path.home() / "MastersProject" / "data" / "captured_frames"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

if not camera.isOpened():
    print("Error: Could not open camera.")
    exit()
    
print("Camera opened successfully. Press Q to quit.")

print("Press R to start/stop recording.")

recording = False
video_writer = None

while True:
    ret, frame = camera.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    cv2.imshow("Camera Feed", frame)

    if recording and video_writer is not None:
        video_writer.write(frame)

    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break

    if key == ord('r'):
        if not recording:
            print("Recording started.")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = SAVE_DIR / f"frame_{timestamp}.avi"
        
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'MJPG') #Video codec for AVI files. Compresses individual frames as jpg
            video_writer = cv2.VideoWriter(str(filename), fourcc, 30.0, (width, height))
            #Creates video writer
            #fourcc = chosen codec
        
            if video_writer.isOpened():
                recording = True
            else:
                video_writer.release()
                video_writer = None
        
        else:
            recording = False
            video_writer.release()
            video_writer = None
            print("Recording saved.")
        
        
if video_writer is not None:
    video_writer.release()

camera.release()
cv2.destroyAllWindows()

print("Camera closed.")
