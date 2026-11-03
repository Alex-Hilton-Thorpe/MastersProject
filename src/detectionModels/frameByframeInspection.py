import cv2
from pathlib import Path

video_path = "C:/Masters/Captures/Left/LeftFrames_19700101_021134.mkv"
images_path = "C:/Masters/MastersProject/data/captured_data/left_Frames"
Path(images_path).mkdir(parents=True, exist_ok=True)

capture = cv2.VideoCapture(video_path)

if not capture.isOpened():
    print("Error opening video file")
    exit()
    
idx = 22880 # Resume from last saved frame
step = 10
total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
last_frame = None
existing = [int(p.stem.split("_")[1]) for p in Path(images_path).glob("capture_*.png")]
capNumber = max(existing, default=0) + 1
print(f"Starting at capture_{capNumber}")



while True:
    capture.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = capture.read()
    
    if ret:
        last_frame = frame
    elif last_frame is not None:
        print(f"Could not read frame {idx}, staying on last good frame")
        frame = last_frame
        idx = max(0, idx - step)
    else:
        print("Could not read frame 1, exiting")
        break
    
    cv2.imshow("Preview", frame)
    
    key = cv2.waitKey(0) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite(f"{images_path}/capture_{capNumber}.png", frame)
        print(f"Saved frame {idx}")
        idx = min(total_frames - 1, idx + step)
        capNumber += 1
    elif key == ord('a'):
        idx = max(0, idx - step)
    elif key == ord('d'):
        idx = min(total_frames - 1, idx + step)
    elif key == ord('1'):
        step = 1
    elif key == ord('2'):
        step = 10
    elif key == ord('+'):
        step += 10
    elif key == ord('-'):
        step = max(1, step - 10)
        
    
    
capture.release()
cv2.destroyAllWindows()
