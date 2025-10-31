from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from models import db, PokemonCard
import asyncio
import easyocr
from webscraper import webscrape
import base64
import cv2
import numpy as np
import re

main = Blueprint("main", __name__)

@main.route("/")
def home():
    cards = PokemonCard.query.order_by(PokemonCard.ungraded_price.desc()).all()
    for card in cards:
        if card.image:
            card.image_base64 = base64.b64encode(card.image).decode("utf-8")
        else:
            card.image_base64 = None
    return render_template("home.html", cards=cards)

@main.route("/add_card", methods=["POST"])
def add_card():
    name = request.form.get("name") or request.args.get("name")
    number = request.form.get("number") or request.args.get("number")

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

        import base64
        image_base64 = base64.b64encode(card.image).decode("utf-8")

        return redirect(url_for("main.home"))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@main.route("/cards", methods=["GET"])
def cards():
    cards = PokemonCard.query.order_by(PokemonCard.ungraded_price.desc()).all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "number": c.number,
            "ungraded_price": c.ungraded_price,
            "graded_price": c.graded_price,
            "created_at": c.created_at
        } for c in cards
    ])

@main.route("/ocr", methods=["POST"])
def ocr():
    img = request.files.get("image")
    img_bytes = img.read()

    reader = easyocr.Reader(['en', 'ja'])
    read_img = reader.readtext(img_bytes)

    print(read_img)

    return 200