import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
CAMERA_INDEX    = 0
OUTPUT_DIR      = Path("crack_detections")
CRACK_THRESHOLD = 0.15       # % of frame area for "watch" severity

# Crack classifier: aspect ratio
MIN_ASPECT_RATIO = 3.0       # long & thin = crack
MIN_CONTOUR_AREA = 200       # pixels² — filters noise

OUTPUT_DIR.mkdir(exist_ok=True)


# ── Core Detection Pipeline ────────────────────────────────────────────────
def preprocess(frame):
    """Enhance contrast locally to make cracks pop."""
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # CLAHE: adaptive histogram equalization
    clahe   = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    return enhanced


def detect_cracks(enhanced, orig_frame):
    """Run Canny edge detection + morphology + contour filtering."""
    edges = cv2.Canny(enhanced, threshold1=50, threshold2=150)

    # Morphological close: bridges gaps in crack edges
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
        
        if aspect >= MIN_ASPECT_RATIO:
            crack_contours.append(cnt)

    # Coverage metric
    frame_area    = orig_frame.shape[0] * orig_frame.shape[1]
    crack_px      = sum(cv2.contourArea(c) for c in crack_contours)
    crack_ratio   = crack_px / frame_area

    # Draw detections on a copy
    annotated = orig_frame.copy()
    cv2.drawContours(annotated, crack_contours, -1, (0, 0, 255), 2)

    return crack_contours, crack_ratio, annotated, edges


def classify_severity(ratio):
    """Map crack coverage % to risk level."""
    if ratio >= 0.30:
        return "critical"
    elif ratio >= 0.15:
        return "warning"
    elif ratio >= 0.05:
        return "watch"
    else:
        return "normal"


def capture_and_detect():
    """
    Single frame capture and detect.
    Returns: {crack_count, crack_area_pct, severity, annotated_frame}
    """
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None

    enhanced = preprocess(frame)
    cracks, ratio, annotated, edges = detect_cracks(enhanced, frame)
    severity = classify_severity(ratio)

    return {
        "crack_count": len(cracks),
        "crack_area_pct": round(ratio * 100, 2),
        "severity": severity,
        "annotated_frame": annotated,
        "edges_frame": edges,
        "timestamp": datetime.now().isoformat()
    }


def save_evidence(result):
    """Save annotated image + JSON when alert-worthy."""
    if result is None:
        return

    severity = result["severity"]
    if severity == "normal":
        return

    ts = result["timestamp"].replace(":", "-")
    
    cv2.imwrite(str(OUTPUT_DIR / f"{ts}_annotated.jpg"), result["annotated_frame"])
    cv2.imwrite(str(OUTPUT_DIR / f"{ts}_edges.jpg"), result["edges_frame"])
    
    import json
    with open(OUTPUT_DIR / f"{ts}_result.json", "w") as f:
        json.dump({
            "timestamp": result["timestamp"],
            "crack_count": result["crack_count"],
            "crack_area_pct": result["crack_area_pct"],
            "severity": result["severity"]
        }, f, indent=2)
    
    print(f"  ↳ Evidence saved to {OUTPUT_DIR}/{ts}_*.jpg")
