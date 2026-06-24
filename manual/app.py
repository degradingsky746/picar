from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from gpiozero import Motor, PWMOutputDevice

app = FastAPI()

# THROTTLE (Motor A)
throttle = Motor(forward=17, backward=27)
throttle_pwm = PWMOutputDevice(18)

# STEERING (Motor B)
steering = Motor(forward=23, backward=24)
steering_pwm = PWMOutputDevice(12)


class Control(BaseModel):
    throttle: int = 0
    steering: int = 0


def set_throttle(speed):
    speed = max(-100, min(100, speed))

    pwm = abs(speed) / 100

    if speed > 0:
        throttle.forward()
    elif speed < 0:
        throttle.backward()
    else:
        throttle.stop()

    throttle_pwm.value = pwm


def set_steering(value):
    value = max(-100, min(100, value))

    if abs(value) < 10:
        steering.stop()
        return

    steering_pwm.value = 1

    if value < 0:
        steering.forward()
    else:
        steering.backward()


@app.get("/", response_class=HTMLResponse)
def home():
    return FileResponse("index.html")


@app.post("/control")
def control(data: Control):
    set_throttle(data.throttle)
    set_steering(data.steering)

    return {"ok": True}


@app.post("/stop")
def stop():
    throttle.stop()
    steering.stop()

    throttle_pwm.value = 0
    steering_pwm.value = 0

    return {"status": "stopped"}

@app.get("/test/{direction}")
def test(direction: str):
    if direction == "left":
        steering_pwm.value = 1
        steering.forward()

    elif direction == "right":
        steering_pwm.value = 1
        steering.backward()

    elif direction == "stop":
        steering.stop()

    return {"direction": direction}
