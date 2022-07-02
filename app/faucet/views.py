# main/views/py
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import faucet
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm
from .. import db
from app.auth.models import Permission, Role, User, Post, Comment
from ..decorators import admin_required, permission_required


@faucet.route('/', methods=["GET", "POST"])
def index():
    form = PostForm()
    return render_template(
        "faucet/index.html",
        form=form
    )


