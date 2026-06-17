from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.history import WishlistItem

wishlist_bp = Blueprint("wishlist", __name__)


@wishlist_bp.route("/")
@login_required
def index():
    items = WishlistItem.query.filter_by(user_id=current_user.id).order_by(WishlistItem.created_at.desc()).all()
    return render_template("wishlist/index.html", items=items)


@wishlist_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Name is required.", "danger")
            return render_template("wishlist/form.html")

        item = WishlistItem(
            user_id=current_user.id,
            name=name,
            category=request.form.get("category"),
            color=request.form.get("color"),
            season=request.form.get("season"),
            price=request.form.get("price", type=float),
            url=request.form.get("url"),
            notes=request.form.get("notes"),
        )
        db.session.add(item)
        db.session.commit()
        flash("Item added to wishlist.", "success")
        return redirect(url_for("wishlist.index"))

    return render_template("wishlist/form.html")


@wishlist_bp.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        item.name = request.form.get("name")
        item.category = request.form.get("category")
        item.color = request.form.get("color")
        item.season = request.form.get("season")
        item.price = request.form.get("price", type=float)
        item.url = request.form.get("url")
        item.notes = request.form.get("notes")
        db.session.commit()
        flash("Wishlist item updated.", "success")
        return redirect(url_for("wishlist.index"))

    return render_template("wishlist/form.html", item=item)


@wishlist_bp.route("/delete/<int:item_id>", methods=["POST"])
@login_required
def delete(item_id):
    item = WishlistItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from wishlist.", "success")
    return redirect(url_for("wishlist.index"))
