from app import db
from datetime import datetime


class Outfit(db.Model):
    __tablename__ = "outfits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OutfitItem", backref="outfit", lazy="dynamic", cascade="all, delete-orphan")
    planned = db.relationship("PlannedOutfit", backref="outfit", lazy="dynamic", cascade="all, delete-orphan")
    history = db.relationship("WearHistory", backref="outfit", lazy="dynamic", cascade="all, delete-orphan")


class OutfitItem(db.Model):
    __tablename__ = "outfit_items"

    id = db.Column(db.Integer, primary_key=True)
    outfit_id = db.Column(db.Integer, db.ForeignKey("outfits.id"), nullable=False)
    clothing_item_id = db.Column(db.Integer, db.ForeignKey("clothing_items.id"), nullable=False)
    slot = db.Column(db.String(20), nullable=False)


class PlannedOutfit(db.Model):
    __tablename__ = "planned_outfits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    outfit_id = db.Column(db.Integer, db.ForeignKey("outfits.id"), nullable=False)
    planned_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
