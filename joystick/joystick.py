import time
import pygame
import RPi.GPIO as GPIO
from gpiozero import Motor, PWMOutputDevice

# =====================================================
# MOTOR SETUP
# =====================================================

# Throttle motor
throttle = Motor(forward=17, backward=27)
throttle_pwm = PWMOutputDevice(18)

# Steering motor
steering = Motor(forward=23, backward=24)
steering_pwm = PWMOutputDevice(12)

# =====================================================
# CONTROLLER SETUP
# =====================================================

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Connected Controller:", joystick.get_name())

# =====================================================
# FUNCTIONS
# =====================================================

def stop():
    throttle.stop()
    steering.stop()

    throttle_pwm.value = 0
    steering_pwm.value = 0


def drive(speed):
    """
    speed range: -1.0 to 1.0
    +ve -> forward
    -ve -> reverse
    """

    # deadzone
    if abs(speed) < 0.15:
        throttle.stop()
        throttle_pwm.value = 0
        return

    pwm = min(abs(speed), 0.5)  # limit max speed

    if speed > 0:
        throttle.forward()
    else:
        throttle.backward()

    throttle_pwm.value = pwm


def steer(value):
    """
    value range: -1.0 to 1.0
    -ve -> left
    +ve -> right
    """

    # deadzone
    if abs(value) < 0.20:
        steering.stop()
        steering_pwm.value = 0
        return

    steering_pwm.value = min(abs(value), 1.0)

    if value < 0:
        steering.forward()     # LEFT
    else:
        steering.backward()    # RIGHT


# =====================================================
# MAIN LOOP
# =====================================================

print("RC Car Ready")
print("Left Stick Y -> Throttle")
print("Left Stick X -> Steering")
print("Circle Button -> STOP")

try:

    while True:

        pygame.event.pump()

        # Left stick
        # throttle_axis = -joystick.get_axis(1)
        # steering_axis = joystick.get_axis(0)

        # Left stick vertical for throttle
        throttle_axis = -joystick.get_axis(1)

        # Right stick horizontal for steering
        steering_axis = joystick.get_axis(3)

        # Circle button (may vary)
        stop_button = joystick.get_button(1)

        # Emergency stop
        if stop_button:
            print("EMERGENCY STOP")
            stop()
            continue

        drive(throttle_axis)
        steer(steering_axis)

        print(
            f"Throttle: {throttle_axis:.2f} | "
            f"Steering: {steering_axis:.2f}",
            end="\r"
        )

        time.sleep(0.02)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    stop()
    pygame.quit()
    GPIO.cleanup()
