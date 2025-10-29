from flask import Blueprint, request, jsonify, render_template
from models import db, PokemonCard
import asyncio
from webscraper import webscrape
import base64

main = Blueprint("main", __name__)

@main.route("/")
def home():
    cards = PokemonCard.query.order_by(PokemonCard.created_at.desc()).all()
    for card in cards:
        if card.image:
            card.image_base64 = base64.b64encode(card.image).decode("utf-8")
        else:
            card.image_base64 = None
    return render_template("home.html", cards=cards)

@main.route("/add_card", methods=["POST"])
def add_card():
    data = request.get_json()
    name = data.get("name")
    number = data.get("number")

    if not name or not number:
        return jsonify({"error": "Missing required fields: name and number"}), 400

    try:
        ungraded_price, graded_price, img_bytes = asyncio.run(webscrape(name,number))

        card = PokemonCard(name=name, number=number, ungraded_price=ungraded_price, graded_price=graded_price, image=img_bytes)
        db.session.add(card)
        db.session.commit()

        import base64
        image_base64 = base64.b64encode(card.image).decode("utf-8")

        return jsonify({
            "message": "Card added successfully",
            "card": {
                "name": name,
                "number": number,
                "ungraded_price": ungraded_price,
                "graded_price": graded_price,
                "image": image_base64
            }
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@main.route("/cards", methods=["GET"])
def cards():
    cards = PokemonCard.query.order_by(PokemonCard.created_at.desc()).all()
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