# crack_detector.py — runs on Raspberry Pi
import cv2
import numpy as np
import time
import json
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
CAMERA_INDEX    = 0
CAPTURE_INTERVAL = 30        # seconds between captures
OUTPUT_DIR      = Path("crack_detections")
CRACK_THRESHOLD = 0.15       # % of frame area; tune for your soil conditions

# Crack classifier: aspect ratio (long & thin = crack, not a pebble)
MIN_ASPECT_RATIO = 3.0       # contour bounding box: width/height or height/width
MIN_CONTOUR_AREA = 200       # pixels² — filters noise

OUTPUT_DIR.mkdir(exist_ok=True)

# ── Detection pipeline ───────────────────────────────────────────────────────
def preprocess(frame):
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # CLAHE: boosts local contrast so cracks in uneven lighting still pop
    clahe   = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    return enhanced

def detect_cracks(enhanced, orig_frame):
    edges = cv2.Canny(enhanced, threshold1=50, threshold2=150)

    # Morphological close: bridges tiny gaps in crack edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    crack_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_CONTOUR_AREA:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = max(w, h) / (min(w, h) + 1e-5)
        if aspect >= MIN_ASPECT_RATIO:          # elongated = crack-like
            crack_contours.append(cnt)

    # Coverage metric
    frame_area    = orig_frame.shape[0] * orig_frame.shape[1]
    crack_px      = sum(cv2.contourArea(c) for c in crack_contours)
    crack_ratio   = crack_px / frame_area

    annotated = orig_frame.copy()
    cv2.drawContours(annotated, crack_contours, -1, (0, 0, 255), 2)

    return crack_contours, crack_ratio, annotated, edges

def classify_severity(ratio):
    if ratio >= 0.30:   return "critical"
    elif ratio >= 0.15: return "warning"
    elif ratio >= 0.05: return "watch"
    else:               return "normal"

def run():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("MooGuard crack detector running. Ctrl+C to stop.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Frame capture failed, retrying…")
                time.sleep(2)
                continue

            enhanced = preprocess(frame)
            cracks, ratio, annotated, edges = detect_cracks(enhanced, frame)
            severity = classify_severity(ratio)
            ts = datetime.now().isoformat()

            result = {
                "timestamp":       ts,
                "crack_count":     len(cracks),
                "crack_area_pct":  round(ratio * 100, 2),
                "severity":        severity,
            }
            print(json.dumps(result))

            # Save evidence image + JSON when alert-worthy
            if severity != "normal":
                slug = ts.replace(":", "-")
                cv2.imwrite(str(OUTPUT_DIR / f"{slug}_annotated.jpg"), annotated)
                cv2.imwrite(str(OUTPUT_DIR / f"{slug}_edges.jpg"),     edges)
                with open(OUTPUT_DIR / f"{slug}_result.json", "w") as f:
                    json.dump(result, f, indent=2)
                print(f"  ↳ Saved evidence to {OUTPUT_DIR}/{slug}_*.jpg")

            time.sleep(CAPTURE_INTERVAL)
    finally:
        cap.release()
        print("Camera released.")

if __name__ == "__main__":
    run()
