import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path

DEVICES = {"left": "/dev/video0", "right": "/dev/video2"}

save_dir = Path.home() / "MastersProject" / "data" / "captured_frames"
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

def make_cmd(dev, path):
    return [
        "gst-launch-1.0", "-e",
        "v4l2src", f"device={dev}", "!",
        "image/jpeg,width=1280,height=720,framerate=60/1", "!",
        # ~5 s of buffering so a disk hiccup doesn't drop frames
        "queue", "max-size-buffers=0", "max-size-bytes=0",
        "max-size-time=5000000000", "!",
        "matroskamux", "!",
        "filesink", f"location={path}",
    ]

procs = {}
for side, dev in DEVICES.items():
    out_dir = save_dir / side.capitalize()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ts}_{side}.mkv"
    # Separate session so the terminal's Ctrl+C doesn't hit gst directly;
    # we send the interrupt ourselves so it is delivered exactly once.
    procs[side] = subprocess.Popen(make_cmd(dev, path), start_new_session=True)

time.sleep(2)
for side, p in procs.items():
    if p.poll() is not None:
        print(f"{side} pipeline exited early (code {p.returncode}). "
              "Check the caps with: v4l2-ctl -d <dev> --list-formats-ext")
        for q in procs.values():
            if q.poll() is None:
                q.send_signal(signal.SIGINT)
        raise SystemExit(1)

print("Recording both cameras. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(0.5)
        if any(p.poll() is not None for p in procs.values()):
            print("A pipeline stopped unexpectedly.")
            break
except KeyboardInterrupt:
    pass

print("Stopping, finalizing files...")
for p in procs.values():
    if p.poll() is None:
        p.send_signal(signal.SIGINT)   # with -e this sends EOS, so the mkv gets finalized
for p in procs.values():
    p.wait()
print("Done.")