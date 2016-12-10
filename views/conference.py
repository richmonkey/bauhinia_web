# -*- coding: utf-8 -*-

from authorization import require_auth
from functools import wraps
from flask import request, Blueprint, g
import json
import logging
import time
from util import make_response
from lib import gobelieve

app = Blueprint('conference', __name__)


def INVALID_PARAM():
    e = {"error":"非法输入"}
    logging.warn("非法输入")
    return make_response(400, e)

@app.route("/conferences", methods=["POST"])
@require_auth
def post_conferences():
    if not request.data:
        return INVALID_PARAM()
    
    req = json.loads(request.data)
    partipants = req
    if not partipants:
        return INVALID_PARAM()

    rds = g.rds
    cid = rds.incr("conferences_id")

    now = int(time.time())
    obj = {"conference":{"id":cid, "partipants":partipants, "timestamp":now}}
    content = json.dumps(obj)
    for uid in partipants:
        r = gobelieve.send_system_message(uid, content)
        logging.debug("send system message:%s", r)

    return make_response(200, {"id":cid})
