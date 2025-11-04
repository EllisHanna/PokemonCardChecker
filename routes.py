from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models import db, PokemonCard, WishlistCard
import asyncio
from webscraper import webscrape
import base64
from decimal import Decimal

main = Blueprint("main", __name__)

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
        from decimal import Decimal
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
        from decimal import Decimal
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
        import numpy as np
        import cv2
        import re
        import asyncio
        from decimal import Decimal
        from webscraper import webscrape
        import easyocr
        import os
        from ultralytics import YOLO

        file = request.files.get("image")
        if not file:
            return jsonify({"error": "No image uploaded"}), 400

        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        h, w, _ = img.shape
        reader = easyocr.Reader(['en'], gpu=False)

        top_region = img[0:int(h * 0.25), 0:w]
        results_top = reader.readtext(top_region, detail=0)
        words = re.findall(r"[A-Za-z'-]+", " ".join(results_top))
        ignore_words = {"basic", "stage", "hp", "level", "lv", "evolves", "from", "pokémon"}
        filtered = [w for w in words if w.lower() not in ignore_words]
        card_name = max(filtered, key=len).capitalize() if filtered else None
        if card_name:
            card_name = re.sub(r"[^A-Za-z0-9' -]", "", card_name).strip(" '\"\n\t").capitalize()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            card_contour = contours[0]
            peri = cv2.arcLength(card_contour, True)
            approx = cv2.approxPolyDP(card_contour, 0.02 * peri, True)
            if len(approx) == 4:
                pts = approx.reshape(4, 2)
                rect = np.zeros((4, 2), dtype="float32")
                s = pts.sum(axis=1)
                rect[0] = pts[np.argmin(s)]
                rect[2] = pts[np.argmax(s)]
                diff = np.diff(pts, axis=1)
                rect[1] = pts[np.argmin(diff)]
                rect[3] = pts[np.argmax(diff)]
                (tl, tr, br, bl) = rect
                widthA = np.linalg.norm(br - bl)
                widthB = np.linalg.norm(tr - tl)
                maxWidth = max(int(widthA), int(widthB))
                heightA = np.linalg.norm(tr - br)
                heightB = np.linalg.norm(tl - bl)
                maxHeight = max(int(heightA), int(heightB))
                dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
                warp = cv2.warpPerspective(img, cv2.getPerspectiveTransform(rect, dst), (maxWidth, maxHeight))
            else:
                warp = img.copy()
        else:
            warp = img.copy()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "models", "yolov8n.pt")
        model = YOLO(MODEL_PATH)
        results = model.predict(warp, imgsz=640)
        card_number = None
        for r in results:
            for box in r.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = box
                card_number = str(int(class_id))
                break
            if card_number:
                break

        if not card_name or not card_number:
            return jsonify({"error": f"Detection failed. Found name={card_name}, number={card_number}"}), 400

        ungraded_price_raw, graded_price_raw, img_bytes = asyncio.run(webscrape(card_name, card_number))

        def parse_price(p):
            if not p:
                return None
            cleaned = re.sub(r"[^\d.]", "", str(p))
            return Decimal(cleaned) if cleaned else None

        card = PokemonCard(
            name=card_name,
            number=card_number,
            ungraded_price=parse_price(ungraded_price_raw),
            graded_price=parse_price(graded_price_raw),
            image=img_bytes
        )

        db.session.add(card)
        db.session.commit()
        return redirect(url_for("main.home"))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
