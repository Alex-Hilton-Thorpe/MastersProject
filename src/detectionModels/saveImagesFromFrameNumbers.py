import re
import cv2
from pathlib import Path

video_path = "C:/Masters/Captures/Left/LeftFrames_19700101_021134.mkv"
images_path = Path("C:/Masters/MastersProject/data/captured_data/left_Frames")
log_path = Path(__file__).parent / "savedFramesLog.txt"
start_number = 1546   # capture number the first frame in the log should get

images_path.mkdir(parents=True, exist_ok=True)

# Pull every frame number out of the log, keeping order and dropping duplicates
text = log_path.read_text()
frames_to_save = list(dict.fromkeys(int(n) for n in re.findall(r"Saved frame (\d+)", text)))
print(f"Found {len(frames_to_save)} frames in the log")

# Safety check: refuse to run if any target file already exists
targets = [images_path / f"capture_{start_number + i}.png" for i in range(len(frames_to_save))]
clashes = [t.name for t in targets if t.exists()]
if clashes:
    print(f"{len(clashes)} target files already exist (e.g. {clashes[0]}). Nothing written.")
    print("Move them out of the folder or change start_number, then rerun.")
    exit()

capture = cv2.VideoCapture(video_path)
if not capture.isOpened():
    print("Error opening video file")
    exit()

failed = []
for frame_idx, out_file in zip(frames_to_save, targets):
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = capture.read()

    if not ret:
        print(f"Could not read frame {frame_idx}")
        failed.append(frame_idx)
        continue

    cv2.imwrite(str(out_file), frame)
    print(f"Saved {out_file.name} (frame {frame_idx})")

capture.release()
print(f"Done. {len(frames_to_save) - len(failed)} saved, {len(failed)} failed.")
if failed:
    print("Failed frames:", failed)