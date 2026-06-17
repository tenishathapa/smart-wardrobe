import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models.clothing import ClothingItem
wardrobe_bp = Blueprint("wardrobe", __name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        return filename
    return None


@wardrobe_bp.route("/")
@login_required
def index():
    category = request.args.get("category")
    color = request.args.get("color")
    season = request.args.get("season")
    occasion = request.args.get("occasion")
    search = request.args.get("search")

    query = ClothingItem.query.filter_by(user_id=current_user.id)

    if category:
        query = query.filter_by(category=category)
    if color:
        query = query.filter_by(color=color)
    if season:
        query = query.filter_by(season=season)
    if occasion:
        query = query.filter_by(occasion=occasion)
    if search:
        query = query.filter(ClothingItem.name.ilike(f"%{search}%"))

    items = query.order_by(ClothingItem.created_at.desc()).all()

    categories = db.session.query(ClothingItem.category).filter_by(user_id=current_user.id).distinct().all()
    colors = db.session.query(ClothingItem.color).filter_by(user_id=current_user.id).distinct().all()
    seasons = db.session.query(ClothingItem.season).filter_by(user_id=current_user.id).distinct().all()
    occasions = db.session.query(ClothingItem.occasion).filter_by(user_id=current_user.id).distinct().all()

    return render_template(
        "wardrobe/index.html",
        items=items,
        categories=[c[0] for c in categories],
        colors=[c[0] for c in colors],
        seasons=[s[0] for s in seasons],
        occasions=[o[0] for o in occasions],
    )


@wardrobe_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        color = request.form.get("color")
        season = request.form.get("season")
        occasion = request.form.get("occasion")
        image_file = request.files.get("image")

        if not all([name, category, color, season, occasion]):
            flash("Name, category, color, season, and occasion are required.", "danger")
            return render_template("wardrobe/form.html")

        image_path = None
        if image_file and image_file.filename:
            image_path = save_image(image_file)

        item = ClothingItem(
            user_id=current_user.id,
            name=name,
            category=category,
            color=color,
            season=season,
            occasion=occasion,
            image_path=image_path,
        )
        db.session.add(item)
        db.session.commit()
        flash("Clothing item added.", "success")
        return redirect(url_for("wardrobe.index"))

    return render_template("wardrobe/form.html")


@wardrobe_bp.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit(item_id):
    item = ClothingItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        item.name = request.form.get("name")
        item.category = request.form.get("category")
        item.color = request.form.get("color")
        item.season = request.form.get("season")
        item.occasion = request.form.get("occasion")

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            if item.image_path:
                old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], item.image_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
            item.image_path = save_image(image_file)

        db.session.commit()
        flash("Clothing item updated.", "success")
        return redirect(url_for("wardrobe.index"))

    return render_template("wardrobe/form.html", item=item)


@wardrobe_bp.route("/delete/<int:item_id>", methods=["POST"])
@login_required
def delete(item_id):
    item = ClothingItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()

    if item.image_path:
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], item.image_path)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(item)
    db.session.commit()
    flash("Clothing item deleted.", "success")
    return redirect(url_for("wardrobe.index"))
