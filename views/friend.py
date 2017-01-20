# -*- coding: utf-8 -*-

from authorization import require_auth
from functools import wraps
from flask import request, Blueprint, g
from werkzeug.security import generate_password_hash, check_password_hash
import json
import logging

from model import user
from model.user import DBUser
from model.friend import Friend

from util import make_response
from lib import gobelieve

app = Blueprint('friend', __name__)

def INVALID_PARAM():
    e = {"error":"非法输入"}
    logging.warn(e['error'])
    return make_response(400, e)


#好友请求
@app.route("/friends/request", methods=["POST"])
@require_auth
def request_friend():
    uid = request.uid
    if not request.data:
        return INVALID_PARAM()
    
    req = json.loads(request.data)
    friend_uid = req.get('friend_uid')
    
    req_id = Friend.add_friend_request(g._db, uid, friend_uid)

    sys_msg = {"friend":{"request_id":req_id, "uid":uid, "type":"request"}}
    gobelieve.send_system_message(friend_uid, json.dumps(sys_msg))
    
    resp = {"request_id":req_id}
    return make_response(200, resp)

#解除好友关系
@app.route("/friends/<int:friend_uid>", methods=["DELETE"])
@require_auth
def delete_friend(friend_uid):
    uid = request.uid
    Friend.delete_friend_relation(g._db, uid, friend_uid)

    sys_msg = {"friend":{"type":"delete", "uid":uid}}
    gobelieve.send_system_message(friend_uid, json.dumps(sys_msg))
    
    return make_response(200, {"success":True})    


@app.route("/friends/accept", methods=["POST"])
@require_auth
def accept_friend():
    if not request.data:
        return INVALID_PARAM()
    
    req = json.loads(request.data)
    request_id = req.get('request_id')
    friend_uid = req.get('uid')
    if not request_id or not friend_uid:
        return INVALID_PARAM()
    
    friend_req = Friend.get_friend_request(g._db, request_id)
    if not friend_req:
        return INVALID_PARAM()

    if friend_req['uid'] != friend_uid or \
       friend_req['friend_uid'] != request.uid:
        return INVALID_PARAM()
    
    #添加双向的好友关系
    Friend.add_friend_relation(g._db, friend_req['uid'], friend_req['friend_uid'])
    
    sys_msg = {"friend":{"type":"accept", "uid":request.uid}}
    gobelieve.send_system_message(friend_req['uid'], json.dumps(sys_msg))
    
    return make_response(200, {"success":True})

@app.route("/friends/reject", methods=["POST"])
@require_auth
def reject_friend():
    if not request.data:
        return INVALID_PARAM()
    
    req = json.loads(request.data)
    request_id = req.get('request_id')
    friend_uid = req.get('uid')
    if not request_id or not friend_uid:
        return INVALID_PARAM()
    
    friend_req = Friend.get_friend_request(g._db, request_id)
    if not friend_req:
        return INVALID_PARAM()

    if friend_req['uid'] != friend_uid or \
       friend_req['friend_uid'] != request.uid:
        return INVALID_PARAM()
    
    sys_msg = {"friend":{"type":"reject", "uid":request.uid}}
    gobelieve.send_system_message(friend_req['uid'], json.dumps(sys_msg))
    
    return make_response(200, {"success":True})    


