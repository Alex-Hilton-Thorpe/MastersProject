
import cv2
import time

# Camera pipelines: 1280x720 at 120 FPS.
# Keep frames in YUYV format to avoid colour-conversion overhead.

pipeline_left = (
    "v4l2src device=/dev/video0 ! "
    "video/x-raw, format=YUY2, width=1280, height=720, framerate=120/1 ! "
    "appsink drop=true max-buffers=1"
)

pipeline_right = (
    "v4l2src device=/dev/video2 ! "
    "video/x-raw, format=YUY2, width=1280, height=720, framerate=120/1 ! "
    "appsink drop=true max-buffers=1"
)

print("Opening left camera...")
camera_left = cv2.VideoCapture(
    pipeline_left, cv2.CAP_GSTREAMER
)

print("Opening right camera...")
camera_right = cv2.VideoCapture(
    pipeline_right, cv2.CAP_GSTREAMER
)

if not camera_left.isOpened():
    print("ERROR: Could not open left camera.")
    camera_right.release()
    raise SystemExit(1)

if not camera_right.isOpened():
    print("ERROR: Could not open right camera.")
    camera_left.release()
    raise SystemExit(1)

print("\nBoth cameras opened successfully.")
print("Warming up cameras...")

# Warm up both streams.
for _ in range(30):
    ret_l, frame_l = camera_left.read()
    ret_r, frame_r = camera_right.read()

    if not ret_l or not ret_r:
        print("ERROR: Failed to read warm-up frames.")
        camera_left.release()
        camera_right.release()
        raise SystemExit(1)

print("Warm-up complete.")
print("Testing for 30 seconds.")
print("No preview or recording is enabled.\n")

test_duration = 30
report_interval = 5

start_time = time.perf_counter()
last_report_time = start_time

interval_pairs = 0
left_read_time = 0.0
right_read_time = 0.0
left_failures = 0
right_failures = 0

try:
    while True:
        loop_start = time.perf_counter()

        # Read left camera.
        read_start = time.perf_counter()
        ret_l, frame_l = camera_left.read()
        left_read_time += time.perf_counter() - read_start

        # Read right camera.
        read_start = time.perf_counter()
        ret_r, frame_r = camera_right.read()
        right_read_time += time.perf_counter() - read_start

        if ret_l and ret_r:
            interval_pairs += 1

        if not ret_l:
            left_failures += 1

        if not ret_r:
            right_failures += 1

        now = time.perf_counter()
        elapsed = now - start_time
        interval_elapsed = now - last_report_time

        if interval_elapsed >= report_interval:
            print(
                f"Elapsed: {elapsed:.1f}s | "
                f"Loop rate: "
                f"{interval_pairs / interval_elapsed:.1f} pairs/sec | "
                f"Avg left read: "
                f"{1000 * left_read_time / max(interval_pairs, 1):.1f} ms | "
                f"Avg right read: "
                f"{1000 * right_read_time / max(interval_pairs, 1):.1f} ms"
            )

            last_report_time = now
            interval_pairs = 0
            left_read_time = 0.0
            right_read_time = 0.0

        if elapsed >= test_duration:
            break

except KeyboardInterrupt:
    print("\nTest stopped by user.")

finally:
    camera_left.release()
    camera_right.release()
    print("\nBoth cameras released.")

print("Test finished.")
print(f"Left camera read failures: {left_failures}")
print(f"Right camera read failures: {right_failures}")
