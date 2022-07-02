from flask import Blueprint, redirect, url_for

# create frontend blueprint
frontend = Blueprint("frontend", __name__)


@frontend.route("/", methods=["GET"])
def default_route():
    return redirect(url_for("faucet.index"))