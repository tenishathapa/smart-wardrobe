from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.clothing import ClothingItem
from models.history import PackingList, PackingListItem

packing_bp = Blueprint("packing", __name__)

SEASONAL_RULES = {
    "Summer": {"Top": 3, "Bottom": 2, "Shoes": 1},
    "Winter": {"Top": 3, "Bottom": 2, "Shoes": 1, "Accessory": 1},
    "Spring": {"Top": 3, "Bottom": 2, "Shoes": 1},
    "Fall": {"Top": 3, "Bottom": 2, "Shoes": 1, "Accessory": 1},
}


@packing_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        destination = request.form.get("destination")
        days = request.form.get("days", type=int)
        season = request.form.get("season")

        if not all([destination, days, season]):
            flash("All fields are required.", "danger")
            return redirect(url_for("packing.index"))

        p_list = PackingList(user_id=current_user.id, destination=destination, days=days, season=season)
        db.session.add(p_list)
        db.session.flush()

        rules = SEASONAL_RULES.get(season, SEASONAL_RULES["Summer"])

        suggestions = {}
        for category, base_qty in rules.items():
            qty = base_qty * (max(days, 1))
            items = (
                ClothingItem.query.filter_by(user_id=current_user.id, category=category, season=season)
                .order_by(ClothingItem.created_at.desc())
                .limit(qty)
                .all()
            )
            for item in items:
                pli = PackingListItem(packing_list_id=p_list.id, clothing_item_id=item.id, quantity=1)
                db.session.add(pli)
                suggestions.setdefault(category, []).append(item)

        db.session.commit()
        return redirect(url_for("packing.view", list_id=p_list.id))

    lists = PackingList.query.filter_by(user_id=current_user.id).order_by(PackingList.created_at.desc()).all()
    return render_template("packing/index.html", lists=lists)


@packing_bp.route("/view/<int:list_id>")
@login_required
def view(list_id):
    p_list = PackingList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    return render_template("packing/view.html", p_list=p_list)


@packing_bp.route("/delete/<int:list_id>", methods=["POST"])
@login_required
def delete(list_id):
    p_list = PackingList.query.filter_by(id=list_id, user_id=current_user.id).first_or_404()
    db.session.delete(p_list)
    db.session.commit()
    flash("Packing list deleted.", "success")
    return redirect(url_for("packing.index"))
