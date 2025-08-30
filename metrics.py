import math
import numpy as np

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

MOUTH_TOP = 13
MOUTH_BOTTOM = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308

def _euclid(p1, p2):
    return float(np.linalg.norm(p1 - p2))

def eye_aspect_ratio(pts):
    def ear_for(idx):
        p1, p2, p3, p4, p5, p6 = [pts[i] for i in idx]
        num = _euclid(p2, p6) + _euclid(p3, p5)
        den = 2.0 * _euclid(p1, p4)
        return 0.0 if den == 0 else num/den
    l = ear_for(LEFT_EYE)
    r = ear_for(RIGHT_EYE)
    return (l + r)/2.0, l, r

def mouth_aspect_ratio(pts):
    top, bottom = pts[MOUTH_TOP], pts[MOUTH_BOTTOM]
    left, right = pts[MOUTH_LEFT], pts[MOUTH_RIGHT]
    horiz = _euclid(left, right)
    return 0.0 if horiz == 0 else _euclid(top, bottom)/horiz

def eye_line_angle_degrees(pts):
    left_c = (pts[33] + pts[133]) / 2.0
    right_c = (pts[362] + pts[263]) / 2.0
    dy = right_c[1] - left_c[1]
    dx = right_c[0] - left_c[0]
    return math.degrees(math.atan2(dy, dx))

def gaze_direction(pts, w, h, tolerance=0.25):
    """
    Estimate gaze direction using iris landmarks relative to eye corners.
    pts = landmarks (numpy array [468+,2])
    w,h = frame width, height
    tolerance = fraction of eye width/height
    """
    # Landmarks
    LEFT_EYE = [33, 133]   # left eye corners
    RIGHT_EYE = [362, 263] # right eye corners
    LEFT_IRIS = [468, 469, 470, 471]
    RIGHT_IRIS = [473, 474, 475, 476]

    # Compute iris centers
    left_iris_center = np.mean(pts[LEFT_IRIS], axis=0)
    right_iris_center = np.mean(pts[RIGHT_IRIS], axis=0)

    # Eye widths/heights (for normalization)
    left_eye_width = abs(pts[LEFT_EYE[1]][0] - pts[LEFT_EYE[0]][0])
    right_eye_width = abs(pts[RIGHT_EYE[1]][0] - pts[RIGHT_EYE[0]][0])

    # Left eye relative position
    lx = (left_iris_center[0] - pts[LEFT_EYE[0]][0]) / left_eye_width
    # Right eye relative position
    rx = (right_iris_center[0] - pts[RIGHT_EYE[0]][0]) / right_eye_width

    # Average for robustness
    gaze_x = (lx + rx) / 2.0

    # Thresholding
    if gaze_x < 0.5 - tolerance:
        return "LEFT"
    elif gaze_x > 0.5 + tolerance:
        return "RIGHT"
    else:
        return "CENTER"