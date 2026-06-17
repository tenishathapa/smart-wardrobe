from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from models.clothing import ClothingItem
from models.outfit import Outfit, OutfitItem
from models.history import WearHistory

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/")
@login_required
def index():
    most_worn = (
        db.session.query(Outfit.name, db.func.count(WearHistory.id).label("count"))
        .join(Outfit, WearHistory.outfit_id == Outfit.id)
        .filter(WearHistory.user_id == current_user.id)
        .group_by(Outfit.id)
        .order_by(db.func.count(WearHistory.id).desc())
        .limit(10)
        .all()
    )

    colors = (
        db.session.query(ClothingItem.color, db.func.count(ClothingItem.id).label("count"))
        .filter(ClothingItem.user_id == current_user.id)
        .group_by(ClothingItem.color)
        .order_by(db.func.count(ClothingItem.id).desc())
        .all()
    )

    seasons = (
        db.session.query(ClothingItem.season, db.func.count(ClothingItem.id).label("count"))
        .filter(ClothingItem.user_id == current_user.id)
        .group_by(ClothingItem.season)
        .order_by(db.func.count(ClothingItem.id).desc())
        .all()
    )

    total_colors = sum(c[1] for c in colors)
    color_pcts = [(c[0], round(c[1] / total_colors * 100, 1)) for c in colors] if total_colors else []

    total_seasons = sum(s[1] for s in seasons)
    season_pcts = [(s[0], round(s[1] / total_seasons * 100, 1)) for s in seasons] if total_seasons else []

    return render_template(
        "analytics/index.html",
        most_worn=most_worn,
        color_pcts=color_pcts,
        season_pcts=season_pcts,
    )
