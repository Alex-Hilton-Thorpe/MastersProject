import argparse
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

DEVICES = {"left": "/dev/video0", "right": "/dev/video2"}
BASE_DIR = Path("/home/alex/MastersProject/data/captured_frames")

parser = argparse.ArgumentParser()
parser.add_argument("--duration", type=float, default=None,
                    help="stop automatically after this many seconds (default: run until Ctrl+C)")
parser.add_argument("--verify", action="store_true",
                    help="count frames in each file with ffprobe after recording")
parser.add_argument("--codec", choices=["h264", "jpeg"], default="h264",
                    help="h264 = small files with a predictable size (default); jpeg = every frame independent")
parser.add_argument("--bitrate", type=int, default=15000,
                    help="h264 target bitrate per camera in kbit/s (default 15000, about 6.75 GB/hour/camera)")
parser.add_argument("--jpeg-quality", type=int, default=85,
                    help="jpeg quality 1-100 (only used with --codec jpeg)")
args = parser.parse_args()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


def encoder_elements():
    if args.codec == "jpeg":
        return ["jpegenc", f"quality={args.jpeg_quality}", "!"]
    return ["x264enc", "speed-preset=veryfast", f"bitrate={args.bitrate}",
            "key-int-max=30", "!", "h264parse", "!"]


def make_cmd(dev, path):
    return [
        "gst-launch-1.0", "-e",
        "v4l2src", f"device={dev}", "!",
        "video/x-raw,format=YUY2,width=1280,height=720,framerate=30/1", "!",
        "queue", "max-size-buffers=0", "max-size-bytes=0",
        "max-size-time=3000000000", "!",
        "videoconvert", "!",
        *encoder_elements(),
        # streamable=true keeps the file playable even after a power cut
        "matroskamux", "streamable=true", "!",
        "filesink", f"location={path}",
    ]


def stop_all(procs):
    # With -e, SIGINT makes gst-launch send EOS so the file gets finalized.
    for p in procs.values():
        if p.poll() is None:
            p.send_signal(signal.SIGINT)
    for p in procs.values():
        try:
            p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()


def remux_all(paths):
    """Add duration + seek index (stream copy, no re-encode). Both files in parallel."""
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found: files will play but can't be seeked. "
              "Install with: sudo apt install ffmpeg")
        return
    print("Adding seek index...", flush=True)
    jobs = {}
    for side, path in paths.items():
        if path.exists() and path.stat().st_size > 0:
            tmp = path.with_name(path.stem + "_tmp.mkv")
            jobs[side] = (path, tmp, subprocess.Popen(
                ["ffmpeg", "-v", "error", "-y", "-i", str(path),
                 "-c", "copy", str(tmp)]))
    for side, (path, tmp, p) in jobs.items():
        p.wait()
        if p.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
            tmp.replace(path)          # atomic: original is only replaced on success
        else:
            print(f"{side}: remux failed, keeping the original (plays, but can't seek)")
            tmp.unlink(missing_ok=True)


def on_sigterm(signum, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, on_sigterm)

# Clean up leftovers from a previous run that was killed mid-remux
for leftover in BASE_DIR.glob("*/*_tmp.mkv"):
    leftover.unlink(missing_ok=True)

paths = {}
for side in DEVICES:
    out_dir = BASE_DIR / side.capitalize()
    out_dir.mkdir(parents=True, exist_ok=True)
    paths[side] = out_dir / f"{side}Frames_{timestamp}.mkv"

procs = {}
failed = False

# Everything from launching gst onwards is inside the try, so a stop request
# at ANY point (even in the first 2 seconds) still shuts the pipelines down.
try:
    for side, dev in DEVICES.items():
        procs[side] = subprocess.Popen(make_cmd(dev, paths[side]),
                                       start_new_session=True)

    time.sleep(2)
    for side, p in procs.items():
        if p.poll() is not None:
            print(f"{side} pipeline exited early (code {p.returncode}). "
                  "Check the caps with: v4l2-ctl -d <dev> --list-formats-ext")
            failed = True
    if not failed:
        print(f"Recording to {BASE_DIR} (timestamp {timestamp})", flush=True)
        if args.codec == "h264":
            gb_hr = args.bitrate * 3600 * 1000 / 8 / 1e9
            print(f"H.264 at {args.bitrate} kbit/s: about {gb_hr:.1f} GB/hour/camera, "
                  f"{2 * gb_hr:.1f} GB/hour for both")
        print("Press Ctrl+C to stop." if args.duration is None
              else f"Will stop automatically after {args.duration:.0f} s (or Ctrl+C).",
              flush=True)

        start = time.monotonic()
        while True:
            time.sleep(0.5)
            if any(p.poll() is not None for p in procs.values()):
                print("A pipeline stopped unexpectedly.")
                break
            if args.duration is not None and time.monotonic() - start >= args.duration:
                break
except KeyboardInterrupt:
    pass

# From here on, ignore further stop requests so a second Ctrl+C / SIGTERM
# can't interrupt finalizing and leave a half-written file behind.
signal.signal(signal.SIGINT, signal.SIG_IGN)
signal.signal(signal.SIGTERM, signal.SIG_IGN)

print("Stopping, finalizing files...", flush=True)
stop_all(procs)

if failed:
    sys.exit(1)

remux_all(paths)

for side, path in paths.items():
    size_mb = path.stat().st_size / 1e6 if path.exists() else 0
    print(f"{side}: {size_mb:.1f} MB  ({path})")
    if args.verify and shutil.which("ffprobe") and path.exists():
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True)
        print(f"{side}: {out.stdout.strip()} frames")

subprocess.run(["chown", "-R", "alex:alex", str(BASE_DIR)])
print("Done.", flush=True)