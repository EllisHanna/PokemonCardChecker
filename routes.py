from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models import db, PokemonCard, WishlistCard
import asyncio
from webscraper import webscrape
import base64
from decimal import Decimal
import re
from PIL import Image
import imagehash
import io
import json

main = Blueprint("main", __name__)
with open("card_hashes.json", "r") as f:
    HASH_DB = json.load(f)

def find_best_card(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    target_hash = imagehash.phash(img)

    best = None
    best_dist = 999

    for card in HASH_DB:
        h = imagehash.hex_to_hash(card["hash"])
        dist = target_hash - h
        if dist < best_dist:
            best_dist = dist
            best = card

    return best, best_dist

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

    best, dist = find_best_card(image_bytes)

    if not best or dist > 12:
        return jsonify({"error": "Card not confidently recognised", "distance": dist}), 400

    name = best["name"].capitalize()
    number = best["number"]

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
    
@main.route("/set_grade/<int:card_id>", methods=["POST"])
def set_grade(card_id):
    card = PokemonCard.query.get_or_404(card_id)
    grade = request.form.get("grade", "Raw")
    card.my_grade = grade
    card.my_price = card.ungraded_price if grade == "Raw" else card.graded_price
    db.session.commit()
    return redirect(url_for("main.home"))
