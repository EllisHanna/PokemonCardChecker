import os
import json
from PIL import Image
import imagehash

IMAGE_DIR = "card_images"
OUT_FILE = "card_hashes.json"

cards = []

print("[START] Building card hash database")

for root, _, files in os.walk(IMAGE_DIR):
    if root == IMAGE_DIR:
        continue

    set_id = os.path.basename(root)

    for file in files:
        if not file.lower().endswith(".png"):
            continue

        path = os.path.join(root, file)

        try:
            img = Image.open(path).convert("RGB")
            img = img.resize((256, 356))

            h = imagehash.phash(img)

            base = os.path.splitext(file)[0]
            if "_" not in base:
                print(f"[SKIP] Bad filename {file}")
                continue

            name, number = base.rsplit("_", 1)

            cards.append({
                "hash": h.__str__(),
                "name": name,
                "number": number,
                "set": set_id
            })

        except Exception as e:
            print(f"[SKIP] {file}: {e}")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(cards, f, indent=2)

print(f"[DONE] {len(cards)} cards hashed → {OUT_FILE}")