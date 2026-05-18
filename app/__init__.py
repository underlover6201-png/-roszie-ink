"""Application Factory - ROSZIE INK"""
import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app(config_name: str | None = None) -> Flask:
    """建立並回傳設定好的 Flask app"""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)

    from app.config import config

    app.config.from_object(config[config_name])

    _init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context_processors(app)
    _register_template_filters(app)
    _setup_logging(app)

    return app


def _init_extensions(app: Flask) -> None:
    from app.extensions import bcrypt, cache, csrf, db, limiter, login_manager, mail, migrate

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # 生產環境才啟用 Talisman（強制 HTTPS + 安全 header）
    if not app.debug and not app.testing:
        from flask_talisman import Talisman

        csp = app.config.get("TALISMAN_CONTENT_SECURITY_POLICY", False)
        Talisman(app, content_security_policy=csp, force_https=False)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "請先登入才能訪問此頁面。"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        from app.models.user import User

        return db.session.get(User, int(user_id))


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.payment import payment_bp
    from app.blueprints.public import public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(payment_bp, url_prefix="/pay")


def _register_error_handlers(app: Flask) -> None:
    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template("errors/429.html"), 429


def _register_context_processors(app: Flask) -> None:
    @app.context_processor
    def inject_globals():
        from app.utils.helpers import get_site_settings

        return {
            "site": get_site_settings(),
            "ga_id": app.config.get("GA_TRACKING_ID"),
        }


def _register_template_filters(app: Flask) -> None:
    from app.utils.filters import register_filters

    register_filters(app)


def _setup_logging(app: Flask) -> None:
    if app.testing:
        return

    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

    info_handler = RotatingFileHandler("logs/info.log", maxBytes=10_000_000, backupCount=5)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler("logs/error.log", maxBytes=10_000_000, backupCount=5)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    app.logger.addHandler(info_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("ROSZIE INK 啟動")
