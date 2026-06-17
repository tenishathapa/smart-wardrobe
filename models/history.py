from app import db
from datetime import datetime


class WearHistory(db.Model):
    __tablename__ = "wear_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    outfit_id = db.Column(db.Integer, db.ForeignKey("outfits.id"), nullable=False)
    worn_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PackingList(db.Model):
    __tablename__ = "packing_lists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    days = db.Column(db.Integer, nullable=False)
    season = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("PackingListItem", backref="packing_list", lazy="dynamic", cascade="all, delete-orphan")


class PackingListItem(db.Model):
    __tablename__ = "packing_list_items"

    id = db.Column(db.Integer, primary_key=True)
    packing_list_id = db.Column(db.Integer, db.ForeignKey("packing_lists.id"), nullable=False)
    clothing_item_id = db.Column(db.Integer, db.ForeignKey("clothing_items.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)


class WishlistItem(db.Model):
    __tablename__ = "wishlist_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    season = db.Column(db.String(20), nullable=True)
    price = db.Column(db.Float, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
