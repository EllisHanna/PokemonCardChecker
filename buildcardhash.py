import os
import json
import cv2
import numpy as np

IMAGE_DIR = "card_images"
OUT_FILE = "card_features.json"

orb = cv2.ORB_create(nfeatures=1000)

db = []

print("[START] Building ORB feature database")

for root, _, files in os.walk(IMAGE_DIR):
    if root == IMAGE_DIR:
        continue

    set_id = os.path.basename(root)

    for file in files:
        if not file.lower().endswith(".png"):
            continue

        path = os.path.join(root, file)

        try:
            img_array = np.fromfile(path, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if img is None:
                print(f"[ERROR] Could not decode: {path}")
                continue

            img = cv2.resize(img, (512, 712))

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            kp, des = orb.detectAndCompute(gray, None)

            if des is None:
                print(f"[SKIP] No features: {file}")
                continue

            base = os.path.splitext(file)[0]

            if "_" not in base:
                print(f"[SKIP] Bad filename format: {file}")
                continue

            name, number = base.rsplit("_", 1)

            db.append({
                "name": name,
                "number": number,
                "set": set_id,
                "descriptors": des.tolist()
            })

        except Exception as e:
            print(f"[ERROR] {file}: {e}")

with open(OUT_FILE, "w") as f:
    json.dump(db, f)

print(f"[DONE] {len(db)} cards saved → {OUT_FILE}")