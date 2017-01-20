# -*- coding: utf-8 -*-

from authorization import require_auth
from functools import wraps
from flask import request, Blueprint, g
from werkzeug.security import generate_password_hash, check_password_hash
import json
import logging

import umysql
from model import user
from model.user import DBUser
from model import code
from model.token import Token

from util import make_response
from lib import gobelieve
from authorization import random_token_generator

app = Blueprint('user', __name__)

def INVALID_PARAM():
    e = {"error":"非法输入"}
    logging.warn(e['error'])
    return make_response(400, e)

def INVALID_PASSWORD():
    e = {"error":"密码错误"}
    logging.warn(e['error'])
    return make_response(400, e)


def INVALID_USERNAME():
    e = {"error":"用户名不存在"}
    logging.warn(e['error'])
    return make_response(400, e)

def INVALID_CODE():
    e = {"error":"验证码错误"}
    logging.warn("验证码错误")
    return make_response(400, e)
    
def CAN_NOT_GET_TOKEN():
    e = {"error":"获取imsdk token失败"}
    logging.warn("获取imsdk token失败")
    return make_response(400, e)


def is_test_number(number):
    if number == "13800000000" or number == "13800000001" or \
       number == "13800000002" or number == "13800000003" or \
       number == "13800000004" or number == "13800000005" or \
       number == "13800000006" or number == "13800000007" or \
       number == "13800000008" or number == "13800000009" :
        return True
    else:
        return False
    
@app.route("/users", methods=["POST", "GET"])
@require_auth
def user_contact():
    if request.method == "POST":
        return get_phone_number_users(g.rds)
    else:
        return get_user_contact(g.rds)

def get_user_contact(rds):
    uid = request.uid
    contacts = user.get_user_contact_list(rds, uid)
    resp = []
    for contact in contacts:
        u = user.get_user(rds, contact.uid)
        if u is None:
            continue
        obj = {}
        if u.avatar:
            obj["avatar"] = u.avatar
        obj["uid"] = int(contact.uid)
        obj["name"] = contact.name
        resp.append(obj)
    return json.dumps(resp)

def get_phone_number_users(rds):
    if not request.data:
        return INVALID_PARAM()
    req = json.loads(request.data)
    resp = []
    contacts = []
    for o in req:
        uid = user.make_uid(o["zone"], o["number"])
        u = user.get_user(rds, uid)
        obj = {}
        obj["zone"] = o["zone"]
        obj["number"] = o["number"]

        if u is None:
            obj["uid"] = 0
        else:
            contact = user.Contact()
            contact.name = o["name"] if o.has_key("name") else ""
            contact.uid = uid
            contacts.append(contact)
            obj["uid"] = uid
            if u.state:
                obj["state"] = u.state
            if u.avatar:
                obj["avatar"] = u.avatar
            if u.up_timestamp:
                obj["up_timestamp"] = u.up_timestamp
        resp.append(obj)
            
    user.set_user_contact_list(rds, request.uid, contacts)
    return make_response(200, resp)

@app.route("/users/me", methods=['PATCH'])
@require_auth
def set_user_property():
    rds = g.rds
    if not request.data:
        return INVALID_PARAM()
    req = json.loads(request.data)
    if req.has_key('state'):
        state = req['state']
        uid = request.uid
        user.set_user_state(rds, uid, state)
        return ""
    elif req.has_key('avatar'):
        avatar = req['avatar']
        uid = request.uid
        user.set_user_avatar(rds, uid, avatar)
        return ""
    elif req.has_key("name"):
        name = req['name']
        uid = request.uid
        user.set_user_name(rds, uid, name)
        return ""
    else:
        return INVALID_PARAM()


@app.route("/users/register", methods=["POST"])
def register_user():
    if not request.data:
        return INVALID_PARAM()
    
    req = json.loads(request.data)
    name = req.get('nickname')
    password = req.get('password')
    #短信验证码
    code = req.get("code")
    number = req.get("number")
    country_code = req.get("country_code")

    if not name or not password or not code \
       or not number or not country_code:
        return INVALID_PARAM()
    
    #check sms code
    if is_test_number(number):
        pass
    else:
        c2, timestamp, _ = code.get_verify_code(g.rds, country_code, number)
        if c1 != c2:
            return INVALID_CODE()
    password = generate_password_hash(password)
    phone_number = "+%s-%s"%(country_code, number)
    u = DBUser.get_user(g._db, phone_number)
    if u:
        uid = u['id']
        DBUser.save_user(g._db, uid, name, password)
    else:
        uid = DBUser.add_user(g._db, name, password, phone_number)

    #登录动作
    access_token = gobelieve.login_gobelieve(uid, name)
    if not access_token:
        return CAN_NOT_GET_TOKEN()

    tok = {
        'expires_in': 3600,
        "access_token":access_token,
        "refresh_token":random_token_generator(),
        'uid':uid
    }


    Token.save_access_token(g.rds, access_token, uid, 3600)
    Token.save_refresh_token(g.rds, tok['refresh_token'], uid)

    return make_response(200, tok)


@app.route("/users/login", methods=["POST"])
def login():
    if not request.data:
        return INVALID_PARAM()
    
    req = json.loads(request.data)

    password = req.get('password')
    number = req.get("number")
    country_code = req.get("country_code")

    phone_number = "+%s-%s"%(country_code, number)
    u = DBUser.get_user(g._db, phone_number)
    if not u:
        return INVALID_USERNAME()
    if not check_password_hash(u['password'], password):
        return INVALID_PASSWORD()

    uid = u['id']
    nickname = u.get('nickname')
    avatar = u.get('avatar')
    state = u.get('state')
    nickname = nickname if nickname else ""
    avatar = avatar if avatar else ""
    state = state if state else ""
    
    access_token = gobelieve.login_gobelieve(uid, nickname)
        
    if not access_token:
        return CAN_NOT_GET_TOKEN()

    tok = {
        'expires_in': 3600,
        "access_token":access_token,
        "refresh_token":random_token_generator(),
        'uid':u['id'],
        'avatar':avatar,
        'state':state
    }

    Token.save_access_token(g.rds, access_token, u['id'], 3600)
    Token.save_refresh_token(g.rds, tok['refresh_token'], u['id'])
    
    return make_response(200, tok)
