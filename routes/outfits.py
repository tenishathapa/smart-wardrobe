from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models.clothing import ClothingItem
from models.outfit import Outfit, OutfitItem
from models.history import WearHistory
from utils.color_match import get_compatible_colors, COLOR_RULES

outfits_bp = Blueprint("outfits", __name__)


@outfits_bp.route("/")
@login_required
def index():
    outfits = Outfit.query.filter_by(user_id=current_user.id).order_by(Outfit.created_at.desc()).all()
    return render_template("outfits/index.html", outfits=outfits)


@outfits_bp.route("/builder", methods=["GET", "POST"])
@login_required
def builder():
    if request.method == "POST":
        name = request.form.get("name")
        notes = request.form.get("notes")
        if not name:
            flash("Outfit name is required.", "danger")
            return redirect(url_for("outfits.builder"))

        outfit = Outfit(user_id=current_user.id, name=name, notes=notes)
        db.session.add(outfit)
        db.session.flush()

        for slot in ["top", "bottom", "shoes", "accessory"]:
            item_id = request.form.get(f"item_{slot}")
            if item_id:
                item = OutfitItem(outfit_id=outfit.id, clothing_item_id=int(item_id), slot=slot)
                db.session.add(item)

        db.session.commit()
        flash("Outfit created.", "success")
        return redirect(url_for("outfits.index"))

    tops = ClothingItem.query.filter_by(user_id=current_user.id, category="Top").all()
    bottoms = ClothingItem.query.filter_by(user_id=current_user.id, category="Bottom").all()
    shoes = ClothingItem.query.filter_by(user_id=current_user.id, category="Shoes").all()
    accessories = ClothingItem.query.filter_by(user_id=current_user.id, category="Accessory").all()

    return render_template("outfits/builder.html", tops=tops, bottoms=bottoms, shoes=shoes, accessories=accessories, color_rules=COLOR_RULES)


@outfits_bp.route("/view/<int:outfit_id>")
@login_required
def view(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()
    return render_template("outfits/view.html", outfit=outfit)


@outfits_bp.route("/edit/<int:outfit_id>", methods=["GET", "POST"])
@login_required
def edit(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        outfit.name = request.form.get("name")
        outfit.notes = request.form.get("notes")

        OutfitItem.query.filter_by(outfit_id=outfit.id).delete()

        for slot in ["top", "bottom", "shoes", "accessory"]:
            item_id = request.form.get(f"item_{slot}")
            if item_id:
                item = OutfitItem(outfit_id=outfit.id, clothing_item_id=int(item_id), slot=slot)
                db.session.add(item)

        db.session.commit()
        flash("Outfit updated.", "success")
        return redirect(url_for("outfits.index"))

    tops = ClothingItem.query.filter_by(user_id=current_user.id, category="Top").all()
    bottoms = ClothingItem.query.filter_by(user_id=current_user.id, category="Bottom").all()
    shoes = ClothingItem.query.filter_by(user_id=current_user.id, category="Shoes").all()
    accessories = ClothingItem.query.filter_by(user_id=current_user.id, category="Accessory").all()

    return render_template("outfits/builder.html", outfit=outfit, tops=tops, bottoms=bottoms, shoes=shoes, accessories=accessories, color_rules=COLOR_RULES)


@outfits_bp.route("/delete/<int:outfit_id>", methods=["POST"])
@login_required
def delete(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()
    db.session.delete(outfit)
    db.session.commit()
    flash("Outfit deleted.", "success")
    return redirect(url_for("outfits.index"))


@outfits_bp.route("/duplicate/<int:outfit_id>", methods=["POST"])
@login_required
def duplicate(outfit_id):
    original = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()

    clone = Outfit(user_id=current_user.id, name=original.name + " (Copy)", notes=original.notes)
    db.session.add(clone)
    db.session.flush()

    for oi in original.items.all():
        db.session.add(OutfitItem(outfit_id=clone.id, clothing_item_id=oi.clothing_item_id, slot=oi.slot))

    db.session.commit()
    flash("Outfit duplicated.", "success")
    return redirect(url_for("outfits.view", outfit_id=clone.id))


@outfits_bp.route("/favorite/<int:outfit_id>", methods=["POST"])
@login_required
def favorite(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()
    outfit.is_favorite = not outfit.is_favorite
    db.session.commit()
    return redirect(request.referrer or url_for("outfits.index"))


@outfits_bp.route("/generate", methods=["POST"])
@login_required
def generate():
    from random import shuffle

    def item_wear_count(item_id):
        return (
            db.session.query(db.func.count(WearHistory.id))
            .join(OutfitItem, WearHistory.outfit_id == OutfitItem.outfit_id)
            .filter(OutfitItem.clothing_item_id == item_id, WearHistory.user_id == current_user.id)
            .scalar()
            or 0
        )

    slots = {"top": "Top", "bottom": "Bottom", "shoes": "Shoes", "accessory": "Accessory"}
    selected = []
    name_parts = []

    for slot_key, category in slots.items():
        items = ClothingItem.query.filter_by(user_id=current_user.id, category=category).all()
        if not items:
            continue
        items.sort(key=lambda i: item_wear_count(i.id))
        shuffle(items[:max(2, len(items))])
        chosen = items[0]
        selected.append((slot_key, chosen))
        name_parts.append(chosen.name)

    if len(selected) < 2:
        flash("Add more clothing items to generate outfits.", "warning")
        return redirect(url_for("outfits.builder"))

    outfit = Outfit(user_id=current_user.id, name="Auto-Generated Outfit")
    db.session.add(outfit)
    db.session.flush()

    for slot_key, item in selected:
        oi = OutfitItem(outfit_id=outfit.id, clothing_item_id=item.id, slot=slot_key)
        db.session.add(oi)

    db.session.commit()
    flash("Outfit generated from your least-worn items!", "success")
    return redirect(url_for("outfits.view", outfit_id=outfit.id))


@outfits_bp.route("/favorites")
@login_required
def favorites():
    outfits = Outfit.query.filter_by(user_id=current_user.id, is_favorite=True).order_by(Outfit.created_at.desc()).all()
    return render_template("outfits/index.html", outfits=outfits, favorites_page=True)
