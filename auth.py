# -*- coding: utf-8 -*-
from flask import request, Blueprint
import random
import json
import time
import requests
import urllib
import logging
import base64
from datetime import datetime
from functools import wraps
from util import make_response
from model import code
from model import token
from model import user
from lib import sms
from authorization import create_token
from authorization import login_gobelieve
import config

app = Blueprint('auth', __name__)
rds = None


def OVERFLOW():
    e = {"error":"get verify code exceed the speed rate"}
    logging.warn("get verify code exceed the speed rate")
    return make_response(400, e)

def INVALID_PARAM():
    e = {"error":"非法输入"}
    logging.warn("非法输入")
    return make_response(400, e)

def INVALID_CODE():
    e = {"error":"验证码错误"}
    logging.warn("验证码错误")
    return make_response(400, e)

def SMS_FAIL():
    e = {"error":"发送短信失败"}
    logging.warn("发送短信失败")
    return make_response(400, e)
    
    
def INVALID_REFRESH_TOKEN():
    e = {"error":"非法的refresh token"}
    logging.warn("非法的refresh token")
    return make_response(400, e)
 
    
def CAN_NOT_GET_TOKEN():
    e = {"error":"获取imsdk token失败"}
    logging.warn("获取imsdk token失败")
    return make_response(400, e)
   
def create_verify_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def check_verify_rate(zone, number):
    now = int(time.time())
    _, ts, count = code.get_verify_code(rds, zone, number)
    if count > 10 and now - ts > 30*60:
        return True
    if now - ts > 50:
        return True

    return False


def send_sms(phone_number, code, app_name):
    accountSid = config.UC_ACCOUNT_SID
    accountToken = config.UC_ACCOUNT_TOKEN
    appId = config.UC_APPID
    templateId = config.UC_TEMPLATE_ID

    param = "%s,%s"%(code, app_name)
    try:
        resp = sms.RestAPI.templateSMS(accountSid,accountToken,appId,phone_number,templateId,param)
        obj = json.loads(resp)
        if obj['resp']['respCode'] == "000000":
            logging.info("send sms success phone:%s code:%s", phone_number, code)
            return True
        else:
            logging.warning("send sms err:%s", resp)
            return False
    except Exception, e:
        logging.warning("exception:%s", str(e))
        return False

def is_test_number(number):
    if number == "13800000000" or number == "13800000001" or \
       number == "13800000002" or number == "13800000003" or \
       number == "13800000004" or number == "13800000005" or \
       number == "13800000006" or number == "13800000007" or \
       number == "13800000008" or number == "13800000009" :
        return True
    else:
        return False
    
def is_super_number(number):
    return False

@app.route("/verify_code", methods=["GET", "POST"])
def verify_code():
    zone = request.args.get("zone", "")
    number = request.args.get("number", "")
    logging.info("zone:%s number:%s", zone, number)
    if not is_test_number(number) and not check_verify_rate(zone, number):
        return OVERFLOW()
        
    vc = create_verify_code()
    code.set_verify_code(rds, zone, number, vc)
    data = {}
    if True:#debug
        data["code"] = vc
        data["number"] = number
        data["zone"] = zone

    if is_test_number(number):
        return make_response(200, data = data)
    if is_super_number(number):
        return make_response(200, data = data)

    if not send_sms(number, vc, config.APP_NAME):
        return SMS_FAIL()

    return make_response(200, data = data)

    
@app.route("/auth/token", methods=["POST"])
def access_token():
    if not request.data:
        return INVALID_PARAM()

    obj = json.loads(request.data)
    c1 = obj["code"]
    number = obj["number"]
    zone = obj["zone"]
    if is_test_number(number):
        pass
    else:
        c2, timestamp, _ = code.get_verify_code(rds, zone, number)
        if c1 != c2:
            return INVALID_CODE()

    uid = user.make_uid(zone, number)

    access_token = login_gobelieve(uid, "", config.APP_ID, config.APP_SECRET)
        
    if not access_token:
        return CAN_NOT_GET_TOKEN()

    u0 = user.get_user(rds, uid)
    u = user.User()
    u.uid = uid
    if u0 is None:
        u.state = "Hey!"
    else:
        u.state = u0.state

    user.save_user(rds, u)

    tok = create_token(3600, True)
    tok['uid'] = uid
    tok['access_token'] = access_token

    t = token.AccessToken(**tok)
    t.save(rds)
    t = token.RefreshToken(**tok)
    t.save(rds)

    return make_response(200, tok)


@app.route("/auth/refresh_token", methods=["POST"])
def refresh_token():
    if not request.data:
        return INVALID_PARAM()

    obj = json.loads(request.data)
    refresh_token = obj["refresh_token"]
    rt = token.RefreshToken()
    if not rt.load(rds, refresh_token):
        return INVALID_REFRESH_TOKEN()

    access_token = login_gobelieve(int(rt.user_id), "", config.APP_ID, config.APP_SECRET)
        
    if not access_token:
        return CAN_NOT_GET_TOKEN()

    tok = create_token(3600, False)
    tok["refresh_token"] = obj["refresh_token"]
    tok["access_token"] = access_token
    tok['uid'] = rt.user_id

    t = token.AccessToken(**tok)
    t.user_id = rt.user_id
    t.save(rds)
    
    return make_response(200, tok)

