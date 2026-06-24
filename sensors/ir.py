import RPi.GPIO as GPIO
import time

IR_PIN = 23  # BCM GPIO 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN, GPIO.IN)

try:
    print("IR Obstacle Detection Started")

    while True:
        if GPIO.input(IR_PIN) == GPIO.LOW:
            print("Obstacle Detected!")
        else:
            print("No Obstacle")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
