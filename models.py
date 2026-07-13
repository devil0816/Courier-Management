from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

class Courier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100))
    receiver = db.Column(db.String(100))
    parcel_type = db.Column(db.String(50))
    weight = db.Column(db.Float)
    charges = db.Column(db.Float)
    address = db.Column(db.String(200))
    address_2 = db.Column(db.String(200))
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    image = db.Column(db.String(200))
