# DeepEyes

**DeepEyes** is a real-time object detection web app designed to assist visually impaired users. It uses a pre-trained YOLO11x model to detect objects from your webcam every few seconds, draws bounding boxes on the live stream, and speaks out detected objects in a natural-language phrase (e.g. “Detected person, chair and cup”).

<p align="center">
  <img src="static/iut.png" alt="IUT Logo" width="100"/><br>
  <em>Isfahan University of Technology</em>
</p>

## Features

- **Real-time MJPEG video stream** via Flask
- **YOLO11x** model for object detection (runs every few seconds)
- **Natural-language TTS** (macOS `say`, fallback options for Ubuntu/Windows)
- **Clean web UI** showing live camera feed, bounding boxes, authors & repo link

---

## Project Structure

```bash
deepEyes/
├── main.py
├── requirements.txt
├── static/
│   ├── iut.png
│   └── style.css
├── templates/
│   └── index.html
├── yolo11x.pt              # YOLO11x weights file
└── venv/                   # (your virtual environment)
```

---

## Download Model Weights

Before running the app, you must download the YOLO11x checkpoint into the project root:

```bash
# using wget
wget https://huggingface.co/Ultralytics/YOLO11/resolve/main/yolo11x.pt
```

Or visit the model page and click “Download”:

> [https://huggingface.co/Ultralytics/YOLO11/blob/main/yolo11x.pt](https://huggingface.co/Ultralytics/YOLO11/blob/main/yolo11x.pt)

Make sure `yolo11x.pt` sits alongside `main.py`.

---

## Requirements

- Python 3.7+
- `pip install -r requirements.txt`

```text
Flask
ultralytics
opencv-python
pyttsx3
```

---

## Setup & Run

### macOS

1. **Install Python 3** (e.g. via Homebrew):

   ```bash
   brew install python
   ```

2. **Clone & enter** the repo:

   ```bash
   git clone https://github.com/Pooria4484/deepEyes.git
   cd deepEyes
   ```

3. **Download the model** as shown above.
4. **Create & activate** a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

6. **Run the app**:

   ```bash
   python main.py
   ```

7. **Open** your browser at `http://127.0.0.1:5000/`

> macOS will use its built-in `say` command for TTS.

---

### Ubuntu (Linux)

1. **Install system packages**:

   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip espeak
   ```

2. **Clone & enter** the repo:

   ```bash
   git clone https://github.com/Pooria4484/deepEyes.git
   cd deepEyes
   ```

3. **Download the model** as shown above.
4. **Create & activate** virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

6. **Adjust TTS** in `main.py` (replace `["say", …]` with `["espeak", …]`):

   ```diff
   - subprocess.Popen(["say", f"Detected {phrase}"])
   + subprocess.Popen(["espeak", f"Detected {phrase}"])
   ```

7. **Run the app**:

   ```bash
   python main.py
   ```

8. **Browse** to `http://127.0.0.1:5000/`

---

### Windows

1. **Install Python 3** from [python.org](https://python.org/) (include in PATH).
2. **Clone & enter** the repo:

   ```powershell
   git clone https://github.com/Pooria4484/deepEyes.git
   cd deepEyes
   ```

3. **Download the model** as shown above.
4. **Create & activate** a virtual environment:

   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Install dependencies**:

   ```powershell
   pip install -r requirements.txt
   ```

6. **Run the app**:

   ```powershell
   python main.py
   ```

7. **Visit** `http://127.0.0.1:5000/` in your browser

> On Windows, `pyttsx3` will use the built-in SAPI5 TTS engine.

---

## Authors

- **Pouria Alaeinezhad** ([pooria.alaei1994@gmail.com](mailto:pooria.alaei1994@gmail.com))
- **Maede Rahimi** ([maede739561@gmail.com](mailto:maede739561@gmail.com))
- **Fatemeh Sharifi** ([fateme.work.sh@gmail.com](mailto:fateme.work.sh@gmail.com))

---

## License

This project is released under the [MIT License](LICENSE).
© 2025 Pouria Alaeinezhad, Maede Rahimi, Fatemeh Sharifi.
