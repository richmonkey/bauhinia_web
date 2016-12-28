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
    channel_id = req.get('channel_id', None)
    partipants = req.get('partipants', None)
    if not channel_id or not partipants:
        return INVALID_PARAM()
    
    uid = int(request.uid)
    now = int(time.time())

    c = {
        "channel_id":channel_id,
        "initiator":uid,
        "partipants":partipants,
        "timestamp":now
    }

    p = "你的朋友邀请你加入群视频通话"
    obj = {"conference":c,
           "push":p}
    content = json.dumps(obj)
    for pid in partipants:
        if pid == uid:
            continue
        r = gobelieve.send_system_message(pid, content)
        logging.debug("send system message:%s", r)

    return make_response(200, {"success":True})


@app.route("/calls", methods=["POST"])
@require_auth
def post_call():
    if not request.data:
        return INVALID_PARAM()
    
    req = json.loads(request.data)
    channel_id = req.get('channel_id', None)
    peer_uid = req.get('peer_uid', None)
    if not channel_id or not peer_uid:
        return INVALID_PARAM()

    
    uid = int(request.uid)
    now = int(time.time())

    c = {
        "channel_id":channel_id,
        "caller":uid,
        "callee":peer_uid,
        "timestamp":now
    }
    p = "你的朋友请求与你通话"
    obj = {"voip":c,
           "push":p}
    content = json.dumps(obj)

    r = gobelieve.send_system_message(peer_uid, content)
    logging.debug("send system message:%s", r)

    return make_response(200, {"success":True})

    
