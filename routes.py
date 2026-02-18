from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models import db, PokemonCard, WishlistCard
import asyncio
from webscraper import webscrape
import base64
from decimal import Decimal
import re
from PIL import Image, ImageFilter
import imagehash
import io
import json
import cv2
import numpy as np

main = Blueprint("main", __name__)

with open("card_hashes.json", "r") as f:
    HASH_DB = json.load(f)

CONFIDENT_MAX = 8
UNCERTAIN_MAX = 20
TOP_K = 5

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def extract_card_candidates(image_bytes):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    cards = []

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            rect = order_points(pts)
            w, h = 512, 712
            dst = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (w, h))
            cards.append(warped)

    if not cards:
        cards.append(cv2.resize(img, (512, 712)))

    return cards

def phash_image(np_img):
    img = Image.fromarray(cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB))
    img = img.resize((512, 712))
    img = img.filter(ImageFilter.GaussianBlur(1))
    return imagehash.phash(img)

def find_top_matches(image_bytes):
    candidates = extract_card_candidates(image_bytes)
    results = []

    for candidate in candidates:
        target_hash = phash_image(candidate)
        for card in HASH_DB:
            h = imagehash.hex_to_hash(card["hash"])
            dist = target_hash - h
            results.append({
                "name": card["name"],
                "number": card["number"],
                "set": card.get("set"),
                "distance": dist
            })

    results.sort(key=lambda x: x["distance"])
    return results[:TOP_K]

@main.route("/")
def home():
    cards = PokemonCard.query.order_by(PokemonCard.my_price.desc()).all()
    wishlist = WishlistCard.query.order_by(WishlistCard.ungraded_price.desc()).all()
    for c in cards + wishlist:
        c.image_base64 = base64.b64encode(c.image).decode("utf-8") if c.image else None
    my_total = sum(c.my_price or Decimal(0) for c in cards)
    return render_template("home.html", cards=cards, wishlist=wishlist, my_total=my_total)

def parse_price(price_str):
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d.]", "", str(price_str))
    return Decimal(cleaned) if cleaned else None

@main.route("/add_card", methods=["POST"])
def add_card():
    name = request.form.get("name")
    number = request.form.get("number")
    grade = request.form.get("grade", "Raw")
    name = name.capitalize()
    if not name or not number:
        return jsonify({"error": "Missing required fields: name and number"}), 400
    try:
        ungraded_price_raw, graded_price_raw, img_bytes = asyncio.run(webscrape(name, number))
        ungraded_price = parse_price(ungraded_price_raw)
        graded_price = parse_price(graded_price_raw)
        my_price = ungraded_price if grade == "Raw" else graded_price
        card = PokemonCard(name=name, number=number, ungraded_price=ungraded_price, graded_price=graded_price, my_grade=grade, my_price=my_price, image=img_bytes)
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
        ungraded_price_raw, graded_price_raw, img_bytes = asyncio.run(webscrape(name, number))
        ungraded_price = parse_price(ungraded_price_raw)
        graded_price = parse_price(graded_price_raw)
        card = WishlistCard(name=name, number=number, ungraded_price=ungraded_price, graded_price=graded_price, image=img_bytes)
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("main.home"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/delete_card/card/<int:card_id>", methods=["DELETE"])
def delete_card(card_id):
    card = PokemonCard.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return "", 204

@main.route("/delete_card/wishlist/<int:card_id>", methods=["DELETE"])
def delete_wishlist(card_id):
    card = WishlistCard.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return "", 204

@main.route("/scan_card", methods=["POST"])
def scan_card():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    grade = request.form.get("grade", "Raw")
    image_bytes = request.files["image"].read()
    matches = find_top_matches(image_bytes)

    if not best or dist > 12:
        return jsonify({
            "error": "Card not confidently recognised",
            "distance": dist
        }), 400

    try:
        ungraded_price_raw, graded_price_raw, img_bytes = asyncio.run(webscrape(name, number))
        ungraded_price = parse_price(ungraded_price_raw)
        graded_price = parse_price(graded_price_raw)
        my_price = ungraded_price if grade == "Raw" else graded_price

        card = PokemonCard(name=name, number=number, ungraded_price=ungraded_price, graded_price=graded_price, my_grade=grade, my_price=my_price, image=img_bytes)
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("main.home"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

