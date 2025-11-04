from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models import db, PokemonCard, WishlistCard
import asyncio
from webscraper import webscrape
import base64
from decimal import Decimal
from ultralytics import YOLO
import cv2
import easyocr
import os
import tempfile

main = Blueprint("main", __name__)

MODEL_PATH = r"C:\Users\Ellis Hanna\Documents\GitHub\PokemonCardChecker\runs\detect\pokemon_card_detector\weights\best.pt"
yolo_model = YOLO(MODEL_PATH)
reader = easyocr.Reader(["en"])

@main.route("/")
def home():
    cards = PokemonCard.query.order_by(PokemonCard.ungraded_price.desc()).all()
    wishlist = WishlistCard.query.order_by(WishlistCard.ungraded_price.desc()).all()
    for c in cards + wishlist:
        c.image_base64 = base64.b64encode(c.image).decode("utf-8") if c.image else None
    ungraded_total = sum(c.ungraded_price or Decimal(0) for c in cards)
    graded_total = sum(c.graded_price or Decimal(0) for c in cards)
    return render_template("home.html", cards=cards, wishlist=wishlist, ungraded_total=ungraded_total, graded_total=graded_total)

@main.route("/add_card", methods=["POST"])
def add_card():
    name = request.form.get("name")
    number = request.form.get("number")
    name = name.capitalize()
    if not name or not number:
        return jsonify({"error": "Missing required fields: name and number"}), 400
    try:
        import re
        def parse_price(price_str):
            if not price_str:
                return None
            cleaned = re.sub(r"[^\d.]", "", str(price_str))
            return Decimal(cleaned) if cleaned else None
        ungraded_price_raw, graded_price_raw, img_bytes = asyncio.run(webscrape(name, number))
        ungraded_price = parse_price(ungraded_price_raw)
        graded_price = parse_price(graded_price_raw)
        card = PokemonCard(name=name, number=number, ungraded_price=ungraded_price, graded_price=graded_price, image=img_bytes)
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("main.home"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/add_wishlist", methods=["POST"])
def add_wishlist():
    name = request.form.get("name")
    number = request.form.get("number")
    name = name.capitalize()
    if not name or not number:
        return jsonify({"error": "Missing fields"}), 400
    try:
        import re
        def parse_price(p):
            if not p:
                return None
            cleaned = re.sub(r"[^\d.]", "", str(p))
            return Decimal(cleaned) if cleaned else None
        ungraded_price_raw, graded_price_raw, img_bytes = asyncio.run(webscrape(name, number))
        ungraded_price = parse_price(ungraded_price_raw)
        graded_price = parse_price(graded_price_raw)
        card = WishlistCard(name=name, number=number, ungraded_price=ungraded_price, graded_price=graded_price, image=img_bytes)
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("main.home"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/scan_card", methods=["POST"])
def scan_card():
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        image_file = request.files["image"]
        temp_dir = tempfile.mkdtemp()
        image_path = os.path.join(temp_dir, image_file.filename)
        image_file.save(image_path)
        results = yolo_model(image_path, conf=0.2, imgsz=640)
        result = results[0]
        img = result.orig_img
        card_name, card_number = None, None
        if hasattr(result, "boxes") and result.boxes is not None:
            for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
                x1, y1, x2, y2 = map(int, box)
                cls_label = yolo_model.names[int(cls)]
                roi = img[y1:y2, x1:x2]
                if roi.size == 0:
                    continue
                ocr_results = reader.readtext(roi)
                ocr_text = " ".join([res[1] for res in ocr_results]).strip()
                if cls_label == "name":
                    card_name = ocr_text
                elif cls_label == "number":
                    card_number = ocr_text
        if not card_name or not card_number:
            return jsonify({"error": "Could not detect both name and number", "detected_name": card_name, "detected_number": card_number}), 400
        card_name = card_name.replace("\n", " ").strip().capitalize()
        card_number = "".join(c for c in card_number if c.isalnum() or c == "/")
        import re
        def parse_price(price_str):
            if not price_str:
                return None
            cleaned = re.sub(r"[^\d.]", "", str(price_str))
            return Decimal(cleaned) if cleaned else None
        ungraded_price_raw, graded_price_raw, img_bytes = asyncio.run(webscrape(card_name, card_number))
        ungraded_price = parse_price(ungraded_price_raw)
        graded_price = parse_price(graded_price_raw)
        card = PokemonCard(name=card_name, number=card_number, ungraded_price=ungraded_price, graded_price=graded_price, image=img_bytes)
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("main.home"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500