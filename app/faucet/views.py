# main/views/py
from asyncio.log import logger
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import faucet
from .forms import FaucetRequestForm
from .. import db
from app.auth.models import Permission, Role, User, Post, Comment
from ..decorators import admin_required, permission_required
from bitcoinlib.services.baseclient import BaseClient
from bitcoinlib.services.baseclient import ClientError as rpc_client_error
from datetime import datetime, timedelta


@faucet.route("/", methods=["GET", "POST"])
def index():
    user_addr = request.remote_addr
    form = FaucetRequestForm()
    current_app.logger.info("Loaded the faucet homepage for: {}".format(user_addr))
    return render_template(
        "faucet/index.html",
        form=form
    )


@faucet.route("/info", methods=["GET"])
def info():
    context = {}
    blockchaininfo = make_rpc_request('{"jsonrpc": "1.0","id": "curltext","method":"getblockchaininfo","params": []}')
    
    return render_template(
        "faucet/info.html",
        context=context,
        today=datetime.now().strftime("%c"),
        blockchaininfo=blockchaininfo
    )


@faucet.route("/netinfo", methods=["GET"])
def netinfo():
    context = {}
    netinfo = make_rpc_request('{"jsonrpc": "1.0","id": "curltext","method":"getnetworkinfo","params": []}')
    
    return render_template(
        "faucet/netinfo.html",
        context=context,
        today=datetime.now().strftime("%c"),
        netinfo=netinfo
    )


def create_base_rpc_client():
    PROVIDER_NAME = "bitcoin-testnet"
    RPC_BASE_URL = current_app.config["BITCOINLIB_RPC_SERVER"]
    NETWORK = "bitcoin"
    base_client = BaseClient(NETWORK, PROVIDER_NAME, RPC_BASE_URL, 1, api_key="")
    return base_client


def make_rpc_request(post_data):
    rpc = create_base_rpc_client()
    method = "post"
    url_path = ""
    variables = {}
    resp = None

    try:
        response = rpc.request(
            url_path, 
            variables=variables, 
            method=method, 
            secure=False, 
            post_data=post_data
        )

        if response:
            resp = response["result"]
        else:
            logger.info("The RPC Server responsed with an error status: {}".format(str(response.status_code)))
            
    except rpc_client_error as err:
        logger.warning("Unable to contact the RPC Server: {}".format(str(err)))
    
    return resp


@faucet.app_template_filter("unix_time")
def convert_unix_time(value):
    return datetime.fromtimestamp(int(value))