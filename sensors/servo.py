import RPi.GPIO as GPIO
import time

SERVO_PIN = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz
pwm.start(0)

def set_angle(angle):
    duty = 2.5 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        print("0°")
        set_angle(0)
        time.sleep(1)

        print("90°")
        set_angle(90)
        time.sleep(1)

        print("180°")
        set_angle(180)
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
