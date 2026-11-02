import Jetson.GPIO as GPIO
import subprocess
import signal
import sys
import os
import time

PIN = 29
STABLE_TIME = 0.05
STOP_TIMEOUT = 600     # seconds to let camera_records.py finish (finalize + remux)
SCRIPT = "/home/alex/MastersProject/src/camera_records.py"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.IN)

proc = None


def start_recording():
    global proc
    if proc is None or proc.poll() is not None:
        # Own process group so we can signal the camera script and its children
        proc = subprocess.Popen([sys.executable, "-u", SCRIPT],
                                start_new_session=True)
        print("Camera script started", flush=True)


def stop_recording():
    global proc
    if proc is not None and proc.poll() is None:
        print("Stopping camera script, waiting for files to finalize...", flush=True)
        pgid = os.getpgid(proc.pid)
        os.killpg(pgid, signal.SIGINT)
        try:
            proc.wait(timeout=STOP_TIMEOUT)
        except subprocess.TimeoutExpired:
            print("Did not exit in time, sending SIGTERM", flush=True)
            os.killpg(pgid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(pgid, signal.SIGKILL)
                proc.wait()
        print("Camera script stopped", flush=True)
    proc = None


def apply(state):
    if state == GPIO.LOW:
        print("Record ON (latched)", flush=True)
        start_recording()
    else:
        print("Record OFF", flush=True)
        stop_recording()


def handle_sigterm(signum, frame):
    raise KeyboardInterrupt      # lets systemd stop run the finally block


signal.signal(signal.SIGTERM, handle_sigterm)

print("Record switch on pin 29. Ctrl+C to stop.", flush=True)

try:
    state = GPIO.input(PIN)
    candidate = state
    since = time.monotonic()
    apply(state)

    while True:
        reading = GPIO.input(PIN)
        now = time.monotonic()

        if reading != candidate:
            candidate = reading
            since = now
        elif candidate != state and now - since >= STABLE_TIME:
            state = candidate
            apply(state)

        time.sleep(0.002)
except KeyboardInterrupt:
    pass
finally:
    stop_recording()
    GPIO.cleanup()