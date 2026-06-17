from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models.outfit import Outfit, PlannedOutfit
from models.history import WearHistory

calendar_bp = Blueprint("calendar", __name__)


@calendar_bp.route("/")
@login_required
def index():
    today = datetime.now()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    outfits = Outfit.query.filter_by(user_id=current_user.id).all()
    planned = PlannedOutfit.query.filter_by(user_id=current_user.id).all()

    planned_by_date = {}
    for p in planned:
        date_str = p.planned_date.strftime("%Y-%m-%d")
        if date_str not in planned_by_date:
            planned_by_date[date_str] = []
        planned_by_date[date_str].append(p)

    return render_template(
        "calendar/index.html",
        year=year,
        month=month,
        today=today,
        datetime=datetime,
        outfits=outfits,
        planned_by_date=planned_by_date,
    )


@calendar_bp.route("/add", methods=["POST"])
@login_required
def add():
    outfit_id = request.form.get("outfit_id", type=int)
    date_str = request.form.get("date")

    if not outfit_id or not date_str:
        flash("Invalid request.", "danger")
        return redirect(url_for("calendar.index"))

    planned_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    existing = PlannedOutfit.query.filter_by(
        user_id=current_user.id, outfit_id=outfit_id, planned_date=planned_date
    ).first()
    if existing:
        flash("Outfit already planned for this date.", "warning")
    else:
        p = PlannedOutfit(user_id=current_user.id, outfit_id=outfit_id, planned_date=planned_date)
        db.session.add(p)
        db.session.commit()
        flash("Outfit planned.", "success")

    return redirect(url_for("calendar.index"))


@calendar_bp.route("/remove/<int:plan_id>", methods=["POST"])
@login_required
def remove(plan_id):
    plan = PlannedOutfit.query.filter_by(id=plan_id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    flash("Planned outfit removed.", "success")
    return redirect(url_for("calendar.index"))


@calendar_bp.route("/wear", methods=["POST"])
@login_required
def wear():
    outfit_id = request.form.get("outfit_id", type=int)
    date_str = request.form.get("date")

    if not outfit_id or not date_str:
        flash("Invalid request.", "danger")
        return redirect(url_for("calendar.index"))

    worn_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    wh = WearHistory(user_id=current_user.id, outfit_id=outfit_id, worn_date=worn_date)
    db.session.add(wh)

    plan = PlannedOutfit.query.filter_by(
        user_id=current_user.id, outfit_id=outfit_id, planned_date=worn_date
    ).first()
    if plan:
        db.session.delete(plan)

    db.session.commit()
    flash("Outfit marked as worn.", "success")
    return redirect(url_for("calendar.index"))


@calendar_bp.route("/history")
@login_required
def history():
    records = WearHistory.query.filter_by(user_id=current_user.id).order_by(WearHistory.worn_date.desc()).all()
    return render_template("calendar/history.html", records=records)
