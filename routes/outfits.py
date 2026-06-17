import json
import secrets
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from models.clothing import ClothingItem
from models.outfit import Outfit, OutfitItem, ShareLink
from models.history import WearHistory
from utils.color_match import get_compatible_colors, COLOR_RULES

outfits_bp = Blueprint("outfits", __name__)


@outfits_bp.route("/")
@login_required
def index():
    search = request.args.get("search")
    fav = request.args.get("favorite")
    query = Outfit.query.filter_by(user_id=current_user.id)
    if search:
        query = query.filter(Outfit.name.ilike(f"%{search}%"))
    if fav:
        query = query.filter_by(is_favorite=True)
    outfits = query.order_by(Outfit.created_at.desc()).all()
    return render_template("outfits/index.html", outfits=outfits, search_term=search or "", fav_filter=fav)


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


@outfits_bp.route("/collage", methods=["GET", "POST"])
@login_required
def collage():
    if request.method == "POST":
        name = request.form.get("name")
        notes = request.form.get("notes")
        collage_raw = request.form.get("collage_data")
        outfit_id = request.form.get("outfit_id")
        if not name:
            flash("Outfit name is required.", "danger")
            return redirect(url_for("outfits.collage"))
        try:
            placed = json.loads(collage_raw) if collage_raw else []
        except (json.JSONDecodeError, TypeError):
            placed = []

        if outfit_id:
            outfit = Outfit.query.filter_by(id=int(outfit_id), user_id=current_user.id).first_or_404()
            outfit.name = name
            outfit.notes = notes
            outfit.collage_data = json.dumps(placed)
            OutfitItem.query.filter_by(outfit_id=outfit.id).delete()
            flash("Collage outfit updated!", "success")
        else:
            outfit = Outfit(user_id=current_user.id, name=name, notes=notes, collage_data=json.dumps(placed))
            db.session.add(outfit)
            db.session.flush()
            flash("Collage outfit created!", "success")

        for entry in placed:
            db.session.add(OutfitItem(outfit_id=outfit.id, clothing_item_id=int(entry["item_id"]), slot=entry.get("slot", "other")))

        db.session.commit()
        return redirect(url_for("outfits.view", outfit_id=outfit.id))

    items = ClothingItem.query.filter_by(user_id=current_user.id).order_by(ClothingItem.category, ClothingItem.name).all()
    return render_template("outfits/collage.html", items=items)


@outfits_bp.route("/collage/<int:outfit_id>")
@login_required
def collage_edit(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()
    items = ClothingItem.query.filter_by(user_id=current_user.id).order_by(ClothingItem.category, ClothingItem.name).all()
    return render_template("outfits/collage.html", items=items, edit_outfit=outfit)


@outfits_bp.route("/wear/<int:outfit_id>", methods=["POST"])
@login_required
def wear(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()
    entry = WearHistory(user_id=current_user.id, outfit_id=outfit.id, worn_date=date.today())
    db.session.add(entry)
    db.session.commit()
    flash(f"Logged '{outfit.name}' as worn today!", "success")
    return redirect(request.referrer or url_for("outfits.index"))


@outfits_bp.route("/bulk-delete", methods=["POST"])
@login_required
def bulk_delete():
    ids = request.form.getlist("outfit_ids")
    if not ids:
        flash("No outfits selected.", "warning")
        return redirect(request.referrer or url_for("outfits.index"))
    count = 0
    for oid in ids:
        outfit = Outfit.query.filter_by(id=int(oid), user_id=current_user.id).first()
        if outfit:
            db.session.delete(outfit)
            count += 1
    db.session.commit()
    flash(f"Deleted {count} outfit(s).", "success")
    return redirect(request.referrer or url_for("outfits.index"))


@outfits_bp.route("/bulk-favorite", methods=["POST"])
@login_required
def bulk_favorite():
    ids = request.form.getlist("outfit_ids")
    if not ids:
        flash("No outfits selected.", "warning")
        return redirect(request.referrer or url_for("outfits.index"))
    count = 0
    for oid in ids:
        outfit = Outfit.query.filter_by(id=int(oid), user_id=current_user.id).first()
        if outfit:
            outfit.is_favorite = True
            count += 1
    db.session.commit()
    flash(f"Favorited {count} outfit(s).", "success")
    return redirect(request.referrer or url_for("outfits.index"))


@outfits_bp.route("/bulk-wear", methods=["POST"])
@login_required
def bulk_wear():
    ids = request.form.getlist("outfit_ids")
    if not ids:
        flash("No outfits selected.", "warning")
        return redirect(request.referrer or url_for("outfits.index"))
    today = date.today()
    count = 0
    for oid in ids:
        outfit = Outfit.query.filter_by(id=int(oid), user_id=current_user.id).first()
        if outfit:
            db.session.add(WearHistory(user_id=current_user.id, outfit_id=outfit.id, worn_date=today))
            count += 1
    db.session.commit()
    flash(f"Logged {count} outfit(s) as worn today!", "success")
    return redirect(request.referrer or url_for("outfits.index"))


@outfits_bp.route("/share/<int:outfit_id>", methods=["POST"])
@login_required
def share(outfit_id):
    outfit = Outfit.query.filter_by(id=outfit_id, user_id=current_user.id).first_or_404()
    link = ShareLink.query.filter_by(outfit_id=outfit.id, user_id=current_user.id).first()
    if not link:
        token = secrets.token_urlsafe(16)
        link = ShareLink(token=token, outfit_id=outfit.id, user_id=current_user.id)
        db.session.add(link)
        db.session.commit()
    share_url = url_for("outfits.public_view", token=link.token, _external=True)
    return jsonify({"url": share_url})


@outfits_bp.route("/shared/<token>")
def public_view(token):
    link = ShareLink.query.filter_by(token=token).first_or_404()
    return render_template("outfits/public.html", outfit=link.outfit)


@outfits_bp.route("/favorites")
@login_required
def favorites():
    outfits = Outfit.query.filter_by(user_id=current_user.id, is_favorite=True).order_by(Outfit.created_at.desc()).all()
    return render_template("outfits/index.html", outfits=outfits, favorites_page=True)
