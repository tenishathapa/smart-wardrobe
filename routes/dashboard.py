from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.clothing import ClothingItem
from models.outfit import Outfit, PlannedOutfit
from utils.weather import get_weather
from utils.recommendations import get_recommendation

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    total_clothes = ClothingItem.query.filter_by(user_id=current_user.id).count()
    total_outfits = Outfit.query.filter_by(user_id=current_user.id).count()
    planned_outfits = PlannedOutfit.query.filter_by(user_id=current_user.id).count()

    weather = get_weather()
    recommendations = []
    if weather:
        recommendations = get_recommendation(
            weather.get("condition"), weather.get("temp")
        )

    return render_template(
        "dashboard/index.html",
        total_clothes=total_clothes,
        total_outfits=total_outfits,
        planned_outfits=planned_outfits,
        weather=weather,
        recommendations=recommendations,
    )
