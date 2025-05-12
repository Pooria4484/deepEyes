from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import pyttsx3
import threading
import time

app = Flask(__name__)

# Load YOLO11x model
model = YOLO("yolo11x.pt")

# Webcam setup
camera = cv2.VideoCapture(1)  # Change to 1 if needed
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Text-to-speech setup
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Thread-safe sets and lock
detected_labels = set()
previously_seen = set()
lock = threading.Lock()


# Threaded speech worker
def tts_worker():
    while True:
        time.sleep(3)  # Speak every 3 seconds

        with lock:
            if detected_labels:
                for label in detected_labels:
                    print(f"[SPEAKING] Detected {label}")
                    engine.say(f"Detected {label}")
                engine.runAndWait()
                detected_labels.clear()


# Start TTS thread
tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()


def generate_frames():
    global previously_seen

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)

        results = model.predict(source=frame, stream=True, verbose=False)

        current_seen = set()

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                conf = box.conf[0].item()

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                current_seen.add(label)

        # Only speak newly detected labels
        with lock:
            new_labels = current_seen - previously_seen
            previously_seen = current_seen

            for label in new_labels:
                detected_labels.add(label)

        # Encode and yield frame
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        camera.release()
