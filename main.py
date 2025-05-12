from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO

# Load YOLO11x model (make sure the file exists at this path)
model = YOLO("yolo11x.pt")


app = Flask(__name__)

camera = cv2.VideoCapture(1)  # Use 0 for webcam


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Optional: Flip image for natural webcam feel
        frame = cv2.flip(frame, 1)

        # Run YOLO object detection
        results = model.predict(source=frame, stream=True, verbose=False)

        # Draw results on the frame
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

        # Encode frame for browser
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
    app.run(debug=True)
