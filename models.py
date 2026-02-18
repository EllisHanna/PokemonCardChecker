from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db: SQLAlchemy = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return str(self.id)

class PokemonCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(50), nullable=False)
    ungraded_price = db.Column(db.Numeric(10,2))
    graded_price = db.Column(db.Numeric(10,2))
    my_grade = db.Column(db.String(10), default="Raw")
    my_price = db.Column(db.Numeric(10,2))
    image = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=db.func.now())

class WishlistCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    number = db.Column(db.String(50))
    ungraded_price = db.Column(db.Numeric(10,2))
    graded_price = db.Column(db.Numeric(10,2))
    image = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=db.func.now())