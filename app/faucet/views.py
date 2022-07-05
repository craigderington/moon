# main/views/py
from asyncio.log import logger
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
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
import json
import os
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from config import basedir

@faucet.route("/", methods=["GET", "POST"])
def index():
    user_addr = request.remote_addr
    form = FaucetRequestForm()
    current_app.logger.info("Loaded the faucet homepage for: {}".format(user_addr))
    transactions = rpc_server_command("listtransactions") or None
    if transactions:
        transactions = sorted(transactions, key=lambda t: t["time"], reverse=True)

    return render_template(
        "faucet/index.html",
        form=form,
        transactions=transactions,
        today=datetime.now().strftime("%c"),
    )


@faucet.route("/<path:path>")
def rpc_server(path):
    user_addr = request.remote_addr
    result = {}
    resp = rpc_server_command(path) or None
    code = json.dumps(resp, indent=4, sort_keys=True)
    lexer = get_lexer_by_name("json", stripall=True)
    formatter = HtmlFormatter(full=True, linenos=True, style="monokai", cssclass="codeblock")
    
    with open(os.path.join(basedir, "app/templates/faucet/outfile.html"), "w") as f1:
        result = highlight(code, lexer, formatter, outfile=f1)


    return render_template(
        "faucet/server.html",
        result=result,
        addr=user_addr,
        path=path,
        today=datetime.now().strftime("%c")
    )


def rpc_server_command(command):
    rpc_commands = {
        "getblockcount": "getblockcount",
        "getbestblockhash": "getbestblockhash",
        "getblockchaininfo": "getblockchaininfo",
        "getmempoolinfo": "getmempoolinfo",
        "getpeerinfo": "getpeerinfo",
        "getnetworkinfo": "getnetworkinfo",
        "listtransactions": "listtransactions",
        "getdifficulty": "getdifficulty",
        "getnettotals": "getnettotals",
        "getmininginfo": "getmininginfo",
        "getbalance": "getbalance",
        "getbalances": "getbalances",
        "getconnectioncount": "getconnectioncount"
    }

    try:
        cmd = rpc_commands[command] or "getblockcount"
        cmd = '{"jsonrpc": "1.0","id": "curltext","method":' + '"' + cmd + '"' + ', "params": []}'
        resp = make_rpc_request(cmd)
    except KeyError as err:
        flash("Sorry, there are no RPC commands mathcing the path:{}".format(str(err)), "danger")
        cmd = "getblockcount"
        cmd = '{"jsonrpc": "1.0","id": "curltext","method":' + '"' + cmd + '"' + ', "params": []}'
        resp = make_rpc_request(cmd)
    return resp


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
