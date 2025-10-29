from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db:SQLAlchemy = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def get_id(self):
        return str(self.id)
    
class PokemonCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    ungraded_price = db.Column(db.String(20))
    graded_price = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, server_default=db.func.now())