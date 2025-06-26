 DriverAware – Real-Time Drowsiness and Distraction Detection

"DriverAware" is a real-time computer vision-based system that monitors a driver's alertness using a webcam. It detects signs of drowsiness such as prolonged eye closure and can trigger alerts to prevent accidents.

![screenshot](./sample_demo.jpg) <!-- Optional if you add a screenshot -->

## Features

-  Real-time eye aspect ratio (EAR) calculation
-  Drowsiness detection with alert system
-  Simple, clean Python script using webcam
-  Easily extendable to include yawning and head pose analysis
-  Built using Dlib, OpenCV, and Scipy

##  How It Works

-  Uses **facial landmark detection** via `dlib`'s 68-point face model
-  Calculates **Eye Aspect Ratio (EAR)** for both eyes
-  If EAR drops below a threshold for several frames, a drowsiness alert is triggered
-  (Future work) Integrate yawn detection and head orientation monitoring

##  Getting Started

###  Install Requirements
```bash
pip install -r requirements.txt
