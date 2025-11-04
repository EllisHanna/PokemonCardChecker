from ultralytics import YOLO
import cv2

model = YOLO(r"C:\Users\Billy\Documents\GitHub\PokemonCardChecker\runs\detect\pokemon_card_detector\weights\best.pt")

image_path = r"C:\Users\Billy\Documents\GitHub\PokemonCardChecker\dataset\images\train\test.jpg"
results = model(image_path, conf=0.05, imgsz=640)

class_colors = {"name": (0, 255, 0), "number": (0, 0, 255)}

for result in results:
    img = result.orig_img.copy()
    detected_classes = set()

    if hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
        for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
            cls_idx = int(cls)
            label = model.names[cls_idx]
            detected_classes.add(label)
            color = class_colors.get(label, (255, 255, 0))
            x1, y1, x2, y2 = map(int, box)

            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, f"{label} {conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            print(f"Detected {label}: ({x1}, {y1}, {x2}, {y2}) confidence: {conf:.2f}")
    else:
        print("No detections found in this image.")

    if "name" not in detected_classes:
        print("⚠️ Warning: No 'name' detected!")
    if "number" not in detected_classes:
        print("⚠️ Warning: No 'number' detected!")

    cv2.imshow("Detection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()