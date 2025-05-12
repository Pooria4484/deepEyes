# MIT License
#
# Copyright (c) 2025 Pouria Alaeinezhad <pooria.alaei1994@gmail.com>, Maede Rahimi, Fatemeh Sharifi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
import subprocess
from ultralytics import YOLO
import cv2
from flask import Flask, render_template, Response


__author__ = [
    "Pouria Alaeinezhad <pooria.alaei1994@gmail.com>",
    "Maede Rahimi",
    "Fatemeh Sharifi"
]

app = Flask(__name__)

# ─── Model & Camera Setup ──────────────────────────────────────────────────────
model = YOLO("yolo11x.pt")        # Load the pre-trained YOLO11x model weights
cam = cv2.VideoCapture(1)       # Open webcam (change index to 0 if needed)
# Set desired resolution
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ─── Detection Scheduling ────────────────────────────────────────────────────────
DETECT_INTERVAL = 5.0             # Seconds between object detection runs
last_run = 0.0                    # Timestamp of last detection
latest_boxes = []                 # Store latest bounding boxes and labels


def generate_frames():
    """
    Generator function that captures frames from the webcam,
    runs YOLO detection every DETECT_INTERVAL seconds,
    speaks detected labels via macOS 'say', and streams
    the MJPEG response to the client.
    """
    global last_run, latest_boxes

    while True:
        ret, frame = cam.read()
        if not ret:
            break               # Stop if frame not read

        # Flip frame horizontally for a mirror view
        frame = cv2.flip(frame, 1)
        now = time.time()

        # Only run detection every DETECT_INTERVAL seconds
        if now - last_run >= DETECT_INTERVAL:
            last_run = now

            # 1) Run YOLO detection on current frame
            results = model.predict(source=frame, verbose=False)
            labels = set()
            boxes = []

            # Parse detection results
            for r in results:
                for b in r.boxes:
                    # Extract box coordinates
                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    cls = int(b.cls[0])          # Class index
                    name = model.names[cls]      # Class name
                    conf = float(b.conf[0])      # Confidence score

                    labels.add(name)
                    boxes.append((x1, y1, x2, y2, name, conf))

            latest_boxes = boxes       # Save boxes for drawing

            # 2) Build a natural-language phrase and speak it
            if labels:
                items = list(labels)
                if len(items) == 1:
                    phrase = items[0]
                else:
                    # Join with commas and "and" before the last item
                    phrase = ", ".join(items[:-1]) + " and " + items[-1]
                # Non-blocking macOS TTS
                subprocess.Popen(["say", f"Detected {phrase}"])

        # 3) Draw the most recent detection boxes on every frame
        for x1, y1, x2, y2, name, conf in latest_boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"{name} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        # 4) Encode frame to JPEG and yield in MJPEG format
        ret2, buf = cv2.imencode('.jpg', frame)
        if not ret2:
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            buf.tobytes() +
            b'\r\n'
        )

# ─── Flask Routes ───────────────────────────────────────────────────────────────


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/video')
def video():
    """Stream the MJPEG response to the client."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# ─── Entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    try:
        # Run Flask development server; use a production WSGI in deployment
        app.run(debug=True)
    finally:
        # Release the webcam on exit
        cam.release()
