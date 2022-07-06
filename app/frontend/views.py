from flask import Blueprint, redirect, render_template, url_for
from datetime import datetime


# create frontend blueprint
frontend = Blueprint("frontend", __name__, template_folder="templates")


@frontend.route("/", methods=["GET"])
def default_route():
    return redirect(url_for("faucet.index"))


@frontend.route("/about", methods=["GET"])
def about():
    context = {}
    return render_template(
        "frontend/about.html",
        context=context,
        today=get_date()
    )


@frontend.route("/donate", methods=["GET"])
def donate():
    context = {}
    return render_template(
        "frontend/donate.html",
        context=context,
        today=get_date()
    )


@frontend.route("/help", methods=["GET"])
def help():
    context = {}
    return render_template(
        "frontend/help.html",
        context=context,
        today=get_date()
    )


def get_date():
    return datetime.now().strftime("%c")