from flask import Flask, Response
from picamera2 import Picamera2
import io
from PIL import Image

app = Flask(__name__)

# Initialize camera
cam = Picamera2()
cam.configure(cam.create_video_configuration(main={"size": (640, 480)}))
cam.start()

def gen():
    while True:
        # Capture frame as numpy array (RGBA)
        frame = cam.capture_array()

        # Convert RGBA → RGB (IMPORTANT FIX)
        img = Image.fromarray(frame).convert("RGB")

        # Encode to JPEG
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        jpg = buf.getvalue()

        # Stream MJPEG frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')

@app.route('/')
def home():
    return "Raspberry Pi Camera Stream running. Go to /video"

@app.route('/video')
def video():
    return Response(gen(),
        mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
