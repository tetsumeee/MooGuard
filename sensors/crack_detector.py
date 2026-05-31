import cv2
import numpy as np
import os
import time
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────
REFERENCES_DIR   = Path("sensors/crack_references")
OUTPUT_DIR       = Path("crack_detections")
OUTPUT_DIR.mkdir(exist_ok=True)

CATEGORIES = ["critical", "warning", "watch", "normal"]  # Priority order

def load_references():
    """Load all reference images grouped by category."""
    refs = {}
    for cat in CATEGORIES:
        cat_dir = REFERENCES_DIR / cat
        images = []
        if cat_dir.exists():
            for img_path in cat_dir.glob("*.jpg"):
                img = cv2.imread(str(img_path))
                if img is not None:
                    img = cv2.resize(img, (640, 480))
                    images.append(img)
        refs[cat] = images
        print(f"[CRACK REF] Loaded {len(images)} '{cat}' references")
    return refs

def compare_images(img1, img2):
    """
    Compare two images using histogram correlation.
    Returns similarity score 0.0 - 1.0 (1.0 = identical)
    """
    img1_resized = cv2.resize(img1, (640, 480))
    img2_resized = cv2.resize(img2, (640, 480))

    score = 0.0
    for channel in range(3):
        hist1 = cv2.calcHist([img1_resized], [channel], None, [256], [0, 256])
        hist2 = cv2.calcHist([img2_resized], [channel], None, [256], [0, 256])
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)
        score += cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return score / 3.0  # Average across 3 channels

def classify_image(current_frame, references):
    """
    Compare current frame against all reference categories.
    Returns best matching category and confidence score.
    """
    if not any(references.values()):
        print("[CRACK] ⚠️ No reference images loaded! Using fallback.")
        return "normal", 0.0

    best_category = "normal"
    best_score    = -1.0
    scores        = {}

    for cat in CATEGORIES:
        cat_refs = references.get(cat, [])
        if not cat_refs:
            continue
        # Average similarity across all references in this category
        cat_score = np.mean([compare_images(current_frame, ref) for ref in cat_refs])
        scores[cat] = round(cat_score, 3)
        if cat_score > best_score:
            best_score    = cat_score
            best_category = cat

    print(f"[CRACK] Scores → {scores}")
    return best_category, round(best_score, 3)

def capture_and_detect(references=None):
    """
    Capture image via Picamera2, compare against references.
    Returns result dict.
    """
    tmp_path = None
    try:
        from picamera2 import Picamera2

        picam = Picamera2()
        config = picam.create_still_configuration(main={"size": (1280, 720)})
        picam.configure(config)
        picam.start()
        time.sleep(2)
        tmp_path = f"/tmp/mooguard_{int(time.time())}.jpg"
        picam.capture_file(tmp_path)
        picam.stop()
        picam.close()

        frame = cv2.imread(tmp_path)
        if frame is None:
            print("[CRACK] ❌ Failed to load captured image")
            return None

        # Load references if not passed in
        if references is None:
            references = load_references()

        severity, confidence = classify_image(frame, references)

        return {
            "crack_count":    0,  # Not applicable for reference matching
            "crack_area_pct": round(confidence * 100, 2),
            "severity":       severity,
            "confidence":     confidence,
            "annotated_frame": frame,
            "timestamp":      datetime.now().isoformat()
        }

    except Exception as e:
        print(f"[CRACK] ❌ Error: {e}")
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

def save_evidence(result):
    if result is None or result["severity"] == "normal":
        return
    ts = result["timestamp"].replace(":", "-")
    cv2.imwrite(str(OUTPUT_DIR / f"{ts}_capture.jpg"), result["annotated_frame"])
    import json
    with open(OUTPUT_DIR / f"{ts}_result.json", "w") as f:
        json.dump({
            "timestamp":      result["timestamp"],
            "severity":       result["severity"],
            "confidence":     result["confidence"],
            "crack_area_pct": result["crack_area_pct"]
        }, f, indent=2)
    print(f"  ↳ Evidence saved: {OUTPUT_DIR}/{ts}_*.jpg")
