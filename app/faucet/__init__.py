# main/__init__.py
from flask import Blueprint
from bitcoinlib.services.baseclient import BaseClient

# faucet blueprint
faucet = Blueprint("faucet", __name__)
from . import views, errors
from app.auth.models import Permission


@faucet.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
