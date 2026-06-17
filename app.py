from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.wardrobe import wardrobe_bp
    from routes.outfits import outfits_bp
    from routes.calendar import calendar_bp
    from routes.analytics import analytics_bp
    from routes.packing import packing_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(wardrobe_bp, url_prefix="/wardrobe")
    app.register_blueprint(outfits_bp, url_prefix="/outfits")
    app.register_blueprint(calendar_bp, url_prefix="/calendar")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")
    app.register_blueprint(packing_bp, url_prefix="/packing")

    return app
