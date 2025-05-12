from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import subprocess
import time

app = Flask(__name__)

# ─── Model & Camera Setup ──────────────────────────────────────────────────────
model = YOLO("yolo11x.pt")        # path to your YOLO11x weights
cam = cv2.VideoCapture(1)       # change index if needed
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ─── Detection Scheduling ────────────────────────────────────────────────────────
DETECT_INTERVAL = 5.0
last_run = 0.0
latest_boxes = []


def generate_frames():
    global last_run, latest_boxes

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        now = time.time()

        # only run detection every DETECT_INTERVAL seconds
        if now - last_run >= DETECT_INTERVAL:
            last_run = now

            # 1) run YOLO
            results = model.predict(source=frame, verbose=False)
            labels = set()
            boxes = []

            for r in results:
                for b in r.boxes:
                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    cls = int(b.cls[0])
                    name = model.names[cls]
                    conf = float(b.conf[0])

                    labels.add(name)
                    boxes.append((x1, y1, x2, y2, name, conf))

            latest_boxes = boxes

            # 2) build and speak phrase
            if labels:
                items = list(labels)
                if len(items) == 1:
                    phrase = items[0]
                else:
                    phrase = ", ".join(items[:-1]) + " and " + items[-1]
                # non-blocking speak
                subprocess.Popen(["say", f"Detected {phrase}"])

        # 3) draw boxes on every frame
        for x1, y1, x2, y2, name, conf in latest_boxes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame,
                        f"{name} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2)

        # 4) encode & stream
        ret2, buf = cv2.imencode('.jpg', frame)
        if not ret2:
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            buf.tobytes() +
            b'\r\n'
        )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        cam.release()
