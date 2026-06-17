from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.clothing import ClothingItem
from models.outfit import Outfit, OutfitItem, PlannedOutfit
from models.history import WearHistory
from utils.weather import get_weather
from utils.recommendations import get_recommendation
from random import shuffle

dashboard_bp = Blueprint("dashboard", __name__)


def get_current_season():
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    return "Fall"


def get_item_wear_count(item_id, user_id):
    return (
        db.session.query(db.func.count(WearHistory.id))
        .join(OutfitItem, WearHistory.outfit_id == OutfitItem.outfit_id)
        .filter(OutfitItem.clothing_item_id == item_id, WearHistory.user_id == user_id)
        .scalar()
        or 0
    )


def suggest_outfit_for_today(user_id):
    categories = ["Top", "Bottom", "Shoes", "Accessory"]
    suggestion = {}

    for cat in categories:
        items = ClothingItem.query.filter_by(user_id=user_id, category=cat).all()
        if not items:
            suggestion[cat] = None
            continue
        items.sort(key=lambda i: get_item_wear_count(i.id, user_id))
        shuffle(items[:max(2, len(items))])
        suggestion[cat] = items[0]

    return suggestion


@dashboard_bp.route("/")
@login_required
def index():
    total_clothes = ClothingItem.query.filter_by(user_id=current_user.id).count()
    total_outfits = Outfit.query.filter_by(user_id=current_user.id).count()
    planned_outfits = PlannedOutfit.query.filter_by(user_id=current_user.id).count()

    current_season = get_current_season()
    season_items = ClothingItem.query.filter_by(user_id=current_user.id, season=current_season).count()
    season_items += ClothingItem.query.filter_by(user_id=current_user.id, season="All Season").count()

    weather = get_weather()
    recommendations = []
    if weather:
        recommendations = get_recommendation(weather.get("condition"), weather.get("temp"))

    suggestion = suggest_outfit_for_today(current_user.id)

    today = date.today()
    worn_today = (
        WearHistory.query
        .filter_by(user_id=current_user.id, worn_date=today)
        .order_by(WearHistory.created_at.desc())
        .all()
    )
    all_outfits = Outfit.query.filter_by(user_id=current_user.id).order_by(Outfit.name).all()

    return render_template(
        "dashboard/index.html",
        total_clothes=total_clothes,
        total_outfits=total_outfits,
        planned_outfits=planned_outfits,
        weather=weather,
        recommendations=recommendations,
        suggestion=suggestion,
        current_season=current_season,
        season_items=season_items,
        worn_today=worn_today,
        all_outfits=all_outfits,
    )


@dashboard_bp.route("/wear-today", methods=["POST"])
@login_required
def wear_today():
    outfit_id = request.form.get("outfit_id")
    if not outfit_id:
        flash("Select an outfit.", "warning")
        return redirect(url_for("dashboard.index"))
    outfit = Outfit.query.filter_by(id=int(outfit_id), user_id=current_user.id).first()
    if not outfit:
        flash("Outfit not found.", "danger")
        return redirect(url_for("dashboard.index"))
    db.session.add(WearHistory(user_id=current_user.id, outfit_id=outfit.id, worn_date=date.today()))
    db.session.commit()
    flash(f"Logged '{outfit.name}' as worn today!", "success")
    return redirect(url_for("dashboard.index"))
