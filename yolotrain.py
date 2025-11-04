from ultralytics import YOLO

model = YOLO(r"C:\Users\Billy\Documents\GitHub\PokemonCardChecker\yolov8n.pt")

model.train(
    data=r"C:\Users\Billy\Documents\GitHub\PokemonCardChecker\dataset.yaml",
    imgsz=640,
    epochs=50,
    batch=4,
    project=r"C:\Users\Billy\Documents\GitHub\PokemonCardChecker\runs\detect",
    name="pokemon_card_detector",
    exist_ok=True
)