import json
import os
import cv2

images_dir = "dataset/images/train"
labels_dir = "dataset/labels/train"
os.makedirs(labels_dir, exist_ok=True)

class_map = {"number": 0, "name": 1}

def polygon_to_bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    return [x_min, y_min, x_max - x_min, y_max - y_min]

def convert_bbox(bbox, img_w, img_h):
    x, y, w, h = bbox
    x_center = (x + w / 2) / img_w
    y_center = (y + h / 2) / img_h
    w /= img_w
    h /= img_h
    return x_center, y_center, w, h

for json_file in os.listdir(images_dir):
    if not json_file.endswith(".json"):
        continue

    json_path = os.path.join(images_dir, json_file)
    with open(json_path, "r") as f:
        data = json.load(f)

    img_filename = data["imagePath"]
    img_path = os.path.join(images_dir, img_filename)
    if not os.path.exists(img_path):
        print(f"Image not found: {img_filename}")
        continue

    img = cv2.imread(img_path)
    if img is None:
        continue
    h, w, _ = img.shape

    yolo_lines = []
    for shape in data.get("shapes", []):
        cls_name = shape["label"].lower()
        if cls_name not in class_map:
            continue
        cls_id = class_map[cls_name]
        bbox = polygon_to_bbox(shape["points"])
        x_center, y_center, bbox_w, bbox_h = convert_bbox(bbox, w, h)
        yolo_lines.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {bbox_w:.6f} {bbox_h:.6f}")

    if yolo_lines:
        label_file = os.path.join(labels_dir, os.path.splitext(img_filename)[0] + ".txt")
        with open(label_file, "w") as f:
            f.write("\n".join(yolo_lines))