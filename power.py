import Jetson.GPIO as GPIO
import time

PIN = 31

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN, GPIO.IN)

print("Power switch on pin 31. Ctrl+C to stop.")
last = None
try:
    while True:
        s = GPIO.input(PIN)
        if s != last:
            print("Power ON (latched)" if s == GPIO.LOW else "Power OFF")
            last = s
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
