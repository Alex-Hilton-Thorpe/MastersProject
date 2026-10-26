import Jetson.GPIO as GPIO
import time

PIN = 29

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.IN)

print("Record switch on pin 29. Ctrl+C to stop.")
last = None
try:
    while True:
        s = GPIO.input(PIN)
        if s != last:
            print("Record ON (latched)" if s == GPIO.LOW else "Record OFF")
            last = s
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
