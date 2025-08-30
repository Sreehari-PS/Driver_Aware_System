# Driver Awareness (Modern MediaPipe Version)

An **AI-powered driver monitoring system** using [MediaPipe Face Mesh](https://developers.google.com/mediapipe) and OpenCV,  
designed to improve **road safety** by detecting driver fatigue and distraction in real time.

---

**Detects:** 
- Drowsiness (EAR)
- Yawn (MAR)
- Head Tilt
- Gaze Tracking

---

## Features
- **Drowsiness Detection (EAR)** – Eye Aspect Ratio monitoring
- **Yawning Detection (MAR)** – Mouth Aspect Ratio monitoring
- **Head Tilt Detection** – Driver posture awareness
- **Eyes-Off-Road / Gaze Tracking** – Detects distraction
- **Non-blocking Alerts** – Audio beep + Text-to-Speech warnings
- **Event Logging** – Saves alerts for later review

---

## Quick Start (Linux / Mac / Windows)

### 1. Clone and enter the project
```bash
git clone https://github.com/Sreehari-PS/Driver_Aware_System.git
cd Driver_Aware_System
```

### 2. Setup virtual environment
```bash
python3 -m venv drowsy_env
source drowsy_env/bin/activate   # Linux/Mac
drowsy_env\Scripts\activate      # Windows (PowerShell)
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run
```bash
python main.py
```

**Controls:**  
- `q` → Quit  
- `l` → Toggle landmarks  
- `m` → Mirror view  

---

## Project Structure
```
Driver_Aware_System/
│── main.py          # Main loop: webcam, HUD, alerts, logging
│── metrics.py       # EAR/MAR/head tilt & gaze math
│── utils.py         # Rolling counters, smoothing buffer, CSV logger
│── alert.py         # Non-blocking audio alerts with cooldown
│── config.yaml      # Thresholds & behavior
│── assets/
│    └── alarm.wav   # Alert sound
```

---

## Configuration
You can adjust thresholds in `config.yaml` to better fit your **face shape**, **camera quality**, and **lighting conditions**.

Examples:
- `EAR_THRESHOLD`: Lower if false alarms trigger too often.
- `MAR_THRESHOLD`: Raise if yawns are detected incorrectly.
- `NO_FACE_SECONDS`: Time before *Eyes Off Road* is triggered.

---

## Requirements
- Python 3.8+
- OpenCV
- MediaPipe
- NumPy
- PyYAML
- simpleaudio
- pyttsx3

Install all at once:
```bash
pip install -r requirements.txt
```

---

## Contributing
Pull requests are welcome!  
For major changes, please open an issue first to discuss what you’d like to improve.

---

## License
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

*Built with passion to make driving safer.*
