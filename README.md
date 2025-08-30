# Driver Awareness (Modern MediaPipe Version)

**Detects:** Drowsiness (EAR), Yawn (MAR), Head Tilt, Eyes-Off-Road. Plays an audible alert and logs events.

## Quick Start (Linux)
```bash
# In your existing env (example path shown):
source ~/drwsy_env/bin/activate     # or wherever your env is

# Place yourself inside this project folder:
cd driver_awareness_modern

# Install any missing deps (safe to re-run):
pip install -r requirements.txt

# Run
python main.py
```
Keys: `q` quit · `l` toggle landmarks · `m` mirror view

## Files
- `main.py` – app entry; webcam, HUD, alerts, logging
- `metrics.py` – EAR/MAR/head-tilt math (MediaPipe Face Mesh indices)
- `utils.py` – counters, smoothing buffer, CSV logger
- `alert.py` – non-blocking audio alert with cooldown
- `config.yaml` – thresholds & behavior
- `assets/alarm.wav` – bundled tone

## Tuning
Edit `config.yaml` thresholds to fit your face/lighting.
