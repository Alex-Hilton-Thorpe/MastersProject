import Jetson.GPIO as GPIO
import subprocess
import signal
import sys
import time

PIN = 29
STABLE_TIME = 0.05
SCRIPT = "/home/alex/MastersProject/src/camera_records.py"   # full path to your script

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.IN)

proc = None

def start_recording():
    global proc
    if proc is None or proc.poll() is not None:      # not already running
        proc = subprocess.Popen([sys.executable, SCRIPT])
        print("Camera script started")

def stop_recording():
    global proc
    if proc is not None and proc.poll() is None:     # still running
        proc.send_signal(signal.SIGINT)              # same as pressing Ctrl+C
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()                              # force it if it won't stop
        print("Camera script stopped")
    proc = None

def apply(state):
    if state == GPIO.LOW:
        print("Record ON (latched)")
        start_recording()
    else:
        print("Record OFF")
        stop_recording()

print("Record switch on pin 29. Ctrl+C to stop.")

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