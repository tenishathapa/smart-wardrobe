from app import db
from datetime import datetime


class ClothingItem(db.Model):
    __tablename__ = "clothing_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    occasion = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    outfit_items = db.relationship("OutfitItem", backref="clothing_item", lazy="dynamic")
