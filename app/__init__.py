# app/__init__.py
from flask import Blueprint, Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from celery import Celery
from config import config, Config
from dotenv import load_dotenv
from logging.config import dictConfig
import logger

# configure services
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

# flask login
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"

# load dotenv
load_dotenv(".env")

# logging
dictConfig(logger.LOGGING_CONFIG)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    celery.conf.update(app.config)

    if not app.debug and not app.testing and not app.config["SSL_DISABLE"]:
        from flask_sslify import SSLify
        sslify = SSLify(app)
    
    # register blueprints
    from app.frontend.views import frontend
    app.register_blueprint(frontend)

    from .faucet import faucet as faucet_bp
    app.register_blueprint(faucet_bp, url_prefix="/faucet")

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix="/api/v1.0")

    return app