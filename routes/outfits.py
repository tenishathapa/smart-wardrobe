from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models.clothing import ClothingItem
from models.outfit import Outfit, OutfitItem
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
        if not name:
            flash("Outfit name is required.", "danger")
            return redirect(url_for("outfits.builder"))

        outfit = Outfit(user_id=current_user.id, name=name)
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


@outfits_bp.route("/favorite/<int:outfit_id>", methods=["POST"])
@login_required
def favorite(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()
    outfit.is_favorite = not outfit.is_favorite
    db.session.commit()
    return redirect(request.referrer or url_for("outfits.index"))


@outfits_bp.route("/favorites")
@login_required
def favorites():
    outfits = Outfit.query.filter_by(user_id=current_user.id, is_favorite=True).order_by(Outfit.created_at.desc()).all()
    return render_template("outfits/index.html", outfits=outfits, favorites_page=True)
