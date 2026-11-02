import Jetson.GPIO as GPIO
import subprocess
import os
import time
 
PIN = 33
STABLE_TIME = 0.05    # new state must hold for 50 ms to count
DRY_RUN = False       # True = print instead of actually shutting down (for testing)
 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.IN)
 
 
def shutdown():
    print("Shutting down...")
    if DRY_RUN:
        print("(dry run, not shutting down)")
        return
    cmd = ["shutdown", "now"]
    if os.geteuid() != 0:             # not root, needs sudo
        cmd = ["sudo"] + cmd
    subprocess.run(cmd)
 
 
print("Power switch on pin 33. Ctrl+C to stop.")
 
try:
    state = GPIO.input(PIN)          # accepted (debounced) state
    candidate = state                # most recent raw reading
    since = time.monotonic()         # when candidate last changed
 
    # Report the starting state only. Never shut down on this initial
    # reading, otherwise booting with the switch OFF would cause a boot loop.
    print("Power ON (latched)" if state == GPIO.LOW else "Power OFF (waiting for switch ON)")
 
    while True:
        reading = GPIO.input(PIN)
        now = time.monotonic()
 
        if reading != candidate:
            candidate = reading      # raw value changed, restart the timer
            since = now
        elif candidate != state and now - since >= STABLE_TIME:
            state = candidate        # held long enough, accept it
            if state == GPIO.LOW:
                print("Power ON (latched)")
            else:
                print("Power OFF")
                shutdown()
 
        time.sleep(0.002)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()