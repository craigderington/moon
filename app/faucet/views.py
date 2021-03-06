# main/views/py
from asyncio.log import logger
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import faucet
from .forms import FaucetRequestForm
from .. import db, redis_client
from app.auth.models import Permission, Role, User, Post, Comment
from ..decorators import admin_required, permission_required
from bitcoinlib.services.baseclient import BaseClient
from bitcoinlib.services.baseclient import ClientError as rpc_client_error
from datetime import datetime, timedelta
import json
import os
import time
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from config import basedir

@faucet.route("/", methods=["GET", "POST"])
def index():
    form = FaucetRequestForm(request.form)
    user_addr = request.remote_addr    
    current_app.logger.info("Loaded the faucet homepage for: {}".format(user_addr))
    time_now = time.time()
    last_time = redis_client.get(user_addr) or time.time()

    # lame spam control
    t = compare_unix_time(time_now, last_time)
    current_app.logger.info("Time Delta: {} minutes".format(str(t)))
    if t is not 0 and t < 60:
        delta = 60 - t
        flash("testnet requests throttled to 1 per hour. please try again in {} minutes...".format(str(delta)), "warning")
        return redirect(url_for("faucet.nobots"))

    # check the faucet request form and call rpc server
    if request.method == "POST" and form.validate_on_submit():
        if "send-to-address" in request.form.keys():
            redis_client.set(user_addr, time.mktime(datetime.now().timetuple()))
            send_to_addr = request.form("send_to_address")
            send_amount = request.form("send_amount")
    
    # list transactions
    transactions = rpc_server_command("listtransactions") or None
    if transactions is not None:
        transactions = sorted(transactions, key=lambda t: t["time"], reverse=True)
        balance = check_wallet_balance()

    return render_template(
        "faucet/index.html",
        form=form,
        transactions=transactions,
        today=datetime.now().strftime("%c"),
        balance=balance
    )


@faucet.route("/nobots", methods=["GET"])
def nobots():
    context = {}
    return render_template(
        "faucet/bots.html",
        context=context,
        today=datetime.now().strftime("%c")
    )

@faucet.route("/<path:path>", methods=["GET"])
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
    resp = None
    rpc_commands = {
        1: "getblockcount",
        2: "getbestblockhash",
        3: "getblockchaininfo",
        4: "getmempoolinfo",
        5: "getpeerinfo",
        6: "getnetworkinfo",
        7: "listtransactions",
        8: "getdifficulty",
        9: "getnettotals",
        10: "getmininginfo",
        11: "getbalance",
        12: "getbalances",
        13: "getconnectioncount"
    }

    if command in rpc_commands.values():
        try:
            cmd = command or "getblockcount"
            cmd = '{"jsonrpc": "1.0","id": "curltext","method":' + '"' + cmd + '"' + ', "params": []}'
            resp = make_rpc_request(cmd)
        except KeyError as err:
            flash("Sorry, there are no RPC commands matching the path:{}".format(str(err)), "danger")
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
            logger.info("The RPC Server responded with an error status: {}".format(str(response.status_code)))
            
    except rpc_client_error as err:
        logger.warning("Unable to contact the RPC Server: {}".format(str(err)))
    
    return resp


def compare_unix_time(a, b):
    t = (float(a) - float(b)) / 60
    return int(t)

def check_wallet_balance():
    cmd = '{"jsonrpc": "1.0","id": "curltext","method": "getbalance", "params": []}'
    current_balance =  make_rpc_request(cmd)
    return current_balance

@faucet.app_template_filter("unix_time")
def convert_unix_time(value):
    return datetime.fromtimestamp(int(value))
