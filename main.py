"""
Driver Awareness (MediaPipe Face Mesh): Drowsiness, Yawn, Head Tilt, Eyes-Off-Road.

Run:
  source <your_env>/bin/activate
  pip install -r requirements.txt
  python main.py
Keys: q quit | l toggle landmarks | m mirror view
"""

import os, time, yaml, argparse, cv2, numpy as np
from utils import RollingCounter, EventLogger, ValueBuffer
from alert import AlertPlayer
from metrics import eye_aspect_ratio, mouth_aspect_ratio, eye_line_angle_degrees, gaze_direction

try:
    import mediapipe as mp
except Exception:
    print("Install mediapipe: pip install mediapipe")
    raise

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--camera", type=int, default=None)
    p.add_argument("--draw-landmarks", action="store_true")
    p.add_argument("--no-draw-landmarks", action="store_true")
    p.add_argument("--mirror", action="store_true")
    p.add_argument("--no-mirror", action="store_true")
    return p.parse_args()

def load_cfg(path):
    with open(path,"r") as f: 
        return yaml.safe_load(f)

def lm_to_xy(lms, w, h):
    pts = np.zeros((len(lms),2), dtype=np.float32)
    for i,lm in enumerate(lms):
        pts[i,0], pts[i,1] = lm.x*w, lm.y*h
    return pts

def bar(frame, text, color=(0,0,255)):
    h,w = frame.shape[:2]
    cv2.rectangle(frame, (0,0), (w,30), (0,0,0), -1)
    cv2.putText(frame, text, (10,22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

def get_camera(cam_idx: int, max_fallback: int = 3):
    # Trying the requested camera
    cap = cv2.VideoCapture(cam_idx)
    if cap.isOpened():
        print(f"Using camera {cam_idx}")
        return cap

    print(f"Camera {cam_idx} not available, trying fallback options...")

    # Trying the fallback cameras (0,1,2,...)
    for i in range(max_fallback):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Falling back to camera {i}")
            return cap

    # If none found, returning None
    print("❌ No camera available")
    return None

def main():
    args = parse_args()
    cfg = load_cfg(args.config)

    cam_idx = args.camera if args.camera is not None else cfg["video"]["camera_index"]
    draw_lm = cfg["video"]["draw_landmarks"]
    mirror = cfg["video"]["mirror_view"]
    if args.draw_landmarks: 
        draw_lm=True
    if args.no_draw_landmarks: 
        draw_lm=False
    if args.mirror: 
        mirror=True
    if args.no_mirror: 
        mirror=False

    T = cfg["thresholds"]
    EAR_TH, EAR_FR = float(T["EAR_THRESHOLD"]), int(T["EAR_CONSEC_FRAMES"])
    MAR_TH, MAR_FR = float(T["MAR_THRESHOLD"]), int(T["MAR_CONSEC_FRAMES"])
    TILT_DEG, TILT_FR = float(T["HEAD_TILT_DEG"]), int(T["TILT_CONSEC_FRAMES"])
    NO_FACE_S, COOLDOWN = float(T["NO_FACE_SECONDS"]), float(T["ALARM_COOLDOWN_SECONDS"])

    logger = EventLogger(cfg["logging"]["csv_path"], enabled=bool(cfg["logging"]["enable_csv"]))
    alerter = AlertPlayer(os.path.join("assets","alarm.wav"), cooldown_seconds=COOLDOWN)

    cap = get_camera(cam_idx)
    if cap is None:
        return
    
    mp_fm = mp.solutions.face_mesh
    draw = mp.solutions.drawing_utils
    draw_spec = draw.DrawingSpec(thickness=1, circle_radius=1)

    face_mesh = mp_fm.FaceMesh(
        static_image_mode=False,
        refine_landmarks=bool(cfg["mediapipe"]["refine_landmarks"]),
        min_detection_confidence=float(cfg["mediapipe"]["min_detection_confidence"]),
        min_tracking_confidence=float(cfg["mediapipe"]["min_tracking_confidence"])
    )

    ear_c = RollingCounter()
    mar_c = RollingCounter()
    tilt_c = RollingCounter()
    last_face = time.time()

    ear_b = ValueBuffer(5)
    mar_b = ValueBuffer(5)
    tilt_b = ValueBuffer(5)

    while True:
        ok, frame = cap.read()
        if not ok: 
            print("Frame capture failed, exiting...")
            time.sleep(0.05)
            continue
        if mirror: 
            frame = cv2.flip(frame, 1)

        h,w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = face_mesh.process(rgb)

        msgs = []
        states = []
        trigger=False

        if res.multi_face_landmarks:
            f = res.multi_face_landmarks[0].landmark
            last_face = time.time()
            pts = lm_to_xy(f, w, h)

            ear, _, _ = eye_aspect_ratio(pts)
            mar = mouth_aspect_ratio(pts)
            tilt = abs(eye_line_angle_degrees(pts))
                
            # Gaze distraction 
            gaze = gaze_direction(pts, w, h)
            if gaze in ["LEFT", "RIGHT"]:
                msgs.append("DISTRACTION")
                states.append("looking_away")
                trigger = True

            # smoothing using buffers
            ear_b.add(ear)
            mar_b.add(mar) 
            tilt_b.add(tilt)
            ear_sm, mar_sm, tilt_sm = ear_b.mean, mar_b.mean, tilt_b.mean

            # thresholds -> booleans
            drowsy = ear_sm < EAR_TH
            yawn = mar_sm > MAR_TH
            tilted = tilt_sm > TILT_DEG
            
            # rolling counters to ensure persistence
            if ear_c.update(drowsy) >= EAR_FR:
                msgs.append("DROWSY")
                states.append("drowsy") 
                trigger=True
            if mar_c.update(yawn) >= MAR_FR:
                msgs.append("YAWN")
                states.append("yawning")
                trigger=True
            if tilt_c.update(tilted) >= TILT_FR: 
                msgs.append("HEAD TILT")
                states.append("looking_away") 
                trigger=True

            hud = f"EAR:{ear_sm:.2f}  MAR:{mar_sm:.2f}  Tilt:{tilt_sm:.1f}° Gaze:{gaze}"
            cv2.putText(frame, hud, (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)

            if draw_lm:
                draw.draw_landmarks(frame, res.multi_face_landmarks[0], mp_fm.FACEMESH_TESSELATION, None, draw_spec)
        else:
            # no face seen recently -> eyes off road
            if time.time() - last_face > NO_FACE_S:
                msgs.append("No face detected — please keep your eyes on the road")
                states.append("looking_away")
                trigger=True
                ear_c.count = mar_c.count = tilt_c.count = 0
        
        # render status bar & log
        if msgs:
            bar(frame, " | ".join(msgs))
            logger.log("ALERT", " & ".join(msgs))
            
            # call the AlertPlayer with the detected normalized states (if any)
            if trigger and states:
                # dedupe states preserve order - small helper
                seen = set()
                dedup_states = [s for s in states if not (s in seen or seen.add(s))]
                alerter.alert(dedup_states)
        else:
            bar(frame, "OK", color=(0,200,0))

        cv2.imshow("Driver Awareness", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q') or k == 27: 
            break
        elif k == ord('l'): 
            draw_lm = not draw_lm
        elif k == ord('m'): 
            mirror = not mirror
    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
