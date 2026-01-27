import io
import numpy as np
from PIL import Image
import torch
from torchvision import models, transforms

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model = torch.nn.Sequential(*list(model.children())[:-1])
model.eval()

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def get_embedding(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    tensor = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        embedding = model(tensor).squeeze().numpy()
    embedding /= np.linalg.norm(embedding)
    return embedding

def find_closest_card(upload_bytes, db_cards):
    upload_emb = get_embedding(upload_bytes)
    best_card = None
    best_score = -1
    for card in db_cards:
        if not hasattr(card, "embedding") or card.embedding is None:
            continue
        score = np.dot(upload_emb, card.embedding)
        if score > best_score:
            best_score = score
            best_card = card
    return best_card, best_score
