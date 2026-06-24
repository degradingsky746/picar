import RPi.GPIO as GPIO
import time
from gpiozero import Motor, PWMOutputDevice

# =====================================================
# GPIO SETUP
# =====================================================

GPIO.setmode(GPIO.BCM)

# =====================================================
# MOTOR SETUP
# =====================================================

# Throttle Motor
throttle = Motor(forward=17, backward=27)
throttle_pwm = PWMOutputDevice(18)

# Steering Motor
steering = Motor(forward=23, backward=24)
steering_pwm = PWMOutputDevice(12)

# =====================================================
# SERVO SETUP
# =====================================================

SERVO_PIN = 13

GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)

# =====================================================
# HC-SR04 SETUP
# =====================================================

TRIG = 5
ECHO = 6

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

GPIO.output(TRIG, False)

# =====================================================
# CONFIG
# =====================================================

SAFE_DISTANCE = 30      # start avoidance
TURN_DISTANCE = 50     # require this much free space to choose a route
CRITICAL_DISTANCE = 20  # emergency stop

LEFT_ANGLE = 0
CENTER_ANGLE = 90
RIGHT_ANGLE = 180

# =====================================================
# SERVO FUNCTIONS
# =====================================================

def set_angle(angle):

    duty = 2.5 + (angle / 18)

    servo.ChangeDutyCycle(duty)

    time.sleep(0.15)

    servo.ChangeDutyCycle(0)

# =====================================================
# ULTRASONIC FUNCTIONS
# =====================================================

def get_distance():

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start = time.time()
    stop = time.time()

    timeout = time.time() + 0.05

    while GPIO.input(ECHO) == 0:

        start = time.time()

        if time.time() > timeout:
            return 999

    timeout = time.time() + 0.05

    while GPIO.input(ECHO) == 1:

        stop = time.time()

        if time.time() > timeout:
            return 999

    elapsed = stop - start

    distance = elapsed * 17150

    return round(distance, 2)

def get_average_distance():

    values = []

    for _ in range(5):

        d = get_distance()

        if d > 0 and d < 500:
            values.append(d)

        time.sleep(0.03)

    if not values:
        return 999

    return round(sum(values) / len(values), 2)


# =====================================================
# MOTOR FUNCTIONS
# =====================================================

def stop():

    throttle.stop()
    steering.stop()

    throttle_pwm.value = 0
    steering_pwm.value = 0

def forward(speed=0.75):

    if speed > 0.4:
        speed = 0.4

    throttle.forward()

    # kick-start motor
    throttle_pwm.value = 0.5
    time.sleep(0.1)

    throttle_pwm.value = speed

def reverse(speed=0.7):

    if speed > 0.4:
        speed = 0.4

    throttle.backward()

    throttle_pwm.value = 0.5
    time.sleep(0.1)

    throttle_pwm.value = speed

def turn_left(duration=1.0):

    steering_pwm.value = 1

    steering.forward()

    time.sleep(duration)

    steering.stop()

    steering_pwm.value = 0

def turn_right(duration=1.0):

    steering_pwm.value = 1

    steering.backward()

    time.sleep(duration)

    steering.stop()

    steering_pwm.value = 0

# =====================================================
# SCAN ENVIRONMENT
# =====================================================

def scan_environment():

    set_angle(LEFT_ANGLE)
    left = get_average_distance()

    set_angle(CENTER_ANGLE)
    center = get_average_distance()

    set_angle(RIGHT_ANGLE)
    right = get_average_distance()

    set_angle(CENTER_ANGLE)

    print(
        f"LEFT={left}cm "
        f"CENTER={center}cm "
        f"RIGHT={right}cm"
    )

    return left, center, right

# =====================================================
# STARTUP
# =====================================================

print("Initializing...")

time.sleep(2)

set_angle(CENTER_ANGLE)

print("Autonomous Mode Started")

# =====================================================
# MAIN LOOP
# =====================================================

try:
    while True:

        front = get_average_distance()

        print(f"\nFront Distance: {front:.1f} cm")

        # =====================================
        # EMERGENCY STOP
        # =====================================

        if front < CRITICAL_DISTANCE:

            print("EMERGENCY STOP"+str(front))

            stop()

            reverse(0.4)
            time.sleep(1.0)

            stop()

            left, center, right = scan_environment()

            if left > right:
                print("Emergency Left")
                turn_left(1.3)
            else:
                print("Emergency Right")
                turn_right(1.3)

            continue

        # =====================================
        # FAST DRIVE
        # =====================================

        if front > 150:

            forward(0.75)

            time.sleep(0.1)

            continue

        # =====================================
        # MEDIUM DRIVE
        # =====================================

        elif front > 100:

            forward(0.55)

            time.sleep(0.1)

            continue

        # =====================================
        # SLOW DRIVE
        # =====================================

        elif front > SAFE_DISTANCE:

            forward(0.35)

            time.sleep(0.1)

            continue

        # =====================================
        # OBSTACLE DETECTED
        # =====================================

        print("Obstacle Detected")

        stop()

        reverse(0.3)
        time.sleep(0.8)

        stop()

        left, center, right = scan_environment()

        print(
            f"LEFT={left:.1f} "
            f"CENTER={center:.1f} "
            f"RIGHT={right:.1f}"
        )

        # CENTER PATH AVAILABLE

        if center > TURN_DISTANCE:

            print("Center Route")

            forward(0.25)
            time.sleep(1)

            stop()

        # LEFT PATH

        elif left > TURN_DISTANCE and right < TURN_DISTANCE:

            print("Taking Left")

            turn_left(1.2)

            forward(0.1)
            time.sleep(1.5)

            stop()

        # RIGHT PATH

        elif right > TURN_DISTANCE and left < TURN_DISTANCE:

            print("Taking Right")

            turn_right(1.2)

            forward(0.25)
            time.sleep(1.5)

            stop()

        # BOTH AVAILABLE

        elif left > TURN_DISTANCE and right > TURN_DISTANCE:

            if left > right:

                print("Choosing Left")

                turn_left(1.2)

            else:

                print("Choosing Right")

                turn_right(1.2)

            forward(0.25)
            time.sleep(1.5)

            stop()

        # DEAD END

        else:

            print("Dead End")

            reverse(0.4)
            time.sleep(2.0)

            stop()

            if left > right:

                turn_left(1.5)

            else:

                turn_right(1.5)

            forward(0.25)
            time.sleep(1.5)

            stop()
except KeyboardInterrupt:

    print("\nStopping...")

    stop()

    servo.stop()

    GPIO.cleanup()
