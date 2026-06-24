import RPi.GPIO as GPIO
import time

TRIG = 5
ECHO = 6

GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)
print("Waiting for sensor to settle...")
time.sleep(2)

def get_distance():
    # Send 10us trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    pulse_end = time.time()

    # Wait for echo to go HIGH
    timeout = time.time() + 0.05
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None

    # Wait for echo to go LOW
    timeout = time.time() + 0.05
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    pulse_duration = pulse_end - pulse_start

    # Speed of sound = 34300 cm/s
    distance = pulse_duration * 17150

    return round(distance, 2)

try:
    while True:
        distance = get_distance()

        if distance is not None:
            print(f"Distance: {distance} cm")
        else:
            print("No echo received")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()
