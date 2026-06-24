from gpiozero import Motor, PWMOutputDevice

# Steering motor (Motor A)
steering = Motor(forward=17, backward=27)
steering_pwm = PWMOutputDevice(18)

# Throttle motor (Motor B)
throttle = Motor(forward=24, backward=23)
throttle_pwm = PWMOutputDevice(12)

def set_throttle(speed):
    pwm = abs(speed) / 100

    if speed > 0:
        throttle.forward()
    elif speed < 0:
        throttle.backward()
    else:
        throttle.stop()

    throttle_pwm.value = pwm


def steer_left():
    steering_pwm.value = 1
    steering.forward()

def steer_right():
    steering_pwm.value = 1
    steering.backward()

def steer_stop():
    steering.stop()

steering_pwm.value = 0.4   # about 40%
throttle.forward()
