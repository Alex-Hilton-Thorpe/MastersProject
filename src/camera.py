import cv2
from pathlib import Path
from datetime import datetime
import time
import threading
import queue



def writer_worker(frame_queue, video_writer, stats):
    while True:
        frame = frame_queue.get()

        try:
            if frame is None:
                break

            video_writer.write(frame)
            stats["written"] += 1

        finally:
            frame_queue.task_done()

    video_writer.release()

pipeline_left = ("v4l2src device=/dev/video0 ! "
            "video/x-raw, width=1280, height=720, framerate=60/1 ! "
            "videoconvert ! "
            "video/x-raw, format=BGR ! "
            "appsink drop=true max-buffers=1")

pipeline_right = ("v4l2src device=/dev/video2 ! "
            "video/x-raw, width=1280, height=720, framerate=60/1 ! "
            "videoconvert ! "
            "video/x-raw, format=BGR ! "
            "appsink drop=true max-buffers=1")

camera_left = cv2.VideoCapture(pipeline_left, cv2.CAP_GSTREAMER)
camera_right = cv2.VideoCapture(pipeline_right, cv2.CAP_GSTREAMER)

SAVE_DIR_LEFT = Path.home() / "MastersProject" / "data" / "captured_frames" / "Left"
SAVE_DIR_LEFT.mkdir(parents=True, exist_ok=True)

SAVE_DIR_RIGHT = Path.home() / "MastersProject" / "data" / "captured_frames" / "Right"
SAVE_DIR_RIGHT.mkdir(parents=True, exist_ok=True)

if not camera_left.isOpened():
    print("Error: Could not open left camera.")
    exit()
    
if not camera_right.isOpened():
    print("Error: Could not open right camera.")
    exit()
    
print("Camera's opened successfully. Press Q to quit.")

print("Press R to start/stop recording.")
    
recording = False

video_writer_l = None
video_writer_r = None

queue_l = None
queue_r = None

thread_l = None
thread_r = None

stats_l = {"written": 0, "dropped": 0}
stats_r = {"written": 0, "dropped": 0}

def stop_recording():
    global recording
    global video_writer_l, video_writer_r
    global queue_l, queue_r
    global thread_l, thread_r

    if not recording:
        return

    recording = False

    # Send stop signals after the queued frames.
    queue_l.put(None)
    queue_r.put(None)

    # Wait for both writers to finish and close their files.
    thread_l.join()
    thread_r.join()

    print("Recording saved.")
    print(f"Left: {stats_l['written']} frames written, "
          f"{stats_l['dropped']} dropped")
    print(f"Right: {stats_r['written']} frames written, "
          f"{stats_r['dropped']} dropped")

    video_writer_l = None
    video_writer_r = None
    queue_l = None
    queue_r = None
    thread_l = None
    thread_r = None



test_start = time.perf_counter()
left_read_time = 0.0
right_read_time = 0.0
test_frames = 0

while True:
    #ret_l, frame_l = camera_left.read()
    #ret_r, frame_r = camera_right.read()
    
    start = time.perf_counter()
    ret_l, frame_l = camera_left.read()
    left_read_time += time.perf_counter() - start

    start = time.perf_counter()
    ret_r, frame_r = camera_right.read()
    right_read_time += time.perf_counter() - start

    test_frames += 1
    
    if not ret_l:
        print("Error: Could not read left frame.")
        break

    if not ret_r:
        print("Error: Could not read right frame.")
        break

    elapsed = time.perf_counter() - test_start

    if elapsed >= 10:
        print(f"\nLoop rate: {test_frames / elapsed:.1f} iterations/sec")
        print(f"Average left read: {1000 * left_read_time / test_frames:.1f} ms")
        print(f"Average right read: {1000 * right_read_time / test_frames:.1f} ms")

        test_start = time.perf_counter()
        left_read_time = 0.0
        right_read_time = 0.0
        test_frames = 0
    
    cv2.imshow("Left Camera Feed", frame_l)
    cv2.imshow("Right Camera Feed", frame_r)


    if recording:
        try:
            queue_l.put_nowait(frame_l.copy())
        except queue.Full:
            stats_l["dropped"] += 1

        try:
            queue_r.put_nowait(frame_r.copy())
        except queue.Full:
            stats_r["dropped"] += 1

    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break

    if key == ord('r'):
        if not recording:
            print("Recording started.")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_l = SAVE_DIR_LEFT / f"frame_{timestamp}_left.avi"
            filename_r = SAVE_DIR_RIGHT / f"frame_{timestamp}_right.avi"
        
            height_l, width_l = frame_l.shape[:2]
            height_r, width_r = frame_r.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*'MJPG') #Video codec for AVI files. Compresses individual frames as jpg
            video_writer_l = cv2.VideoWriter(str(filename_l), fourcc, 60.0, (width_l, height_l))
            video_writer_r = cv2.VideoWriter(str(filename_r), fourcc, 60.0, (width_r, height_r))
            #Creates video writer
            #fourcc = chosen codec
        
            #if video_writer_l.isOpened() and video_writer_r.isOpened():
            #    recording = True
            #else:
            #    video_writer_l.release()
            #    video_writer_r.release()
            #    video_writer_l = None
            #    video_writer_r = None
            
            
            if video_writer_l.isOpened() and video_writer_r.isOpened():
                queue_l = queue.Queue(maxsize=10)
                queue_r = queue.Queue(maxsize=10)

                stats_l = {"written": 0, "dropped": 0}
                stats_r = {"written": 0, "dropped": 0}

                thread_l = threading.Thread(
                    target=writer_worker,
                    args=(queue_l, video_writer_l, stats_l)
                )
                thread_r = threading.Thread(
                    target=writer_worker,
                    args=(queue_r, video_writer_r, stats_r)
                )

                thread_l.start()
                thread_r.start()

                recording = True
                print("Recording started.")

            else:
                video_writer_l.release()
                video_writer_r.release()

                video_writer_l = None
                video_writer_r = None

                print("Error: Could not open both video writers.")
        
        else:
            stop_recording()
            # recording = False
            # video_writer_l.release()
            # video_writer_r.release()
            # video_writer_l = None
            # video_writer_r = None
            # print("Recording saved.")
        
        
# if video_writer_l is not None and video_writer_r is not None:
#     video_writer_l.release()
#     video_writer_r.release()

if recording:
    stop_recording()

camera_left.release()
camera_right.release()
cv2.destroyAllWindows()

print("Camera closed.")
