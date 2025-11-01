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
