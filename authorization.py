# -*- coding: utf-8 -*-

from flask import request
from functools import wraps
from model import token
from util import make_response
import logging
import random
import time
import web
import json
import base64
import md5
import requests
import config

rds = None

def INVALID_ACCESS_TOKEN():
    e = {"error":"非法的access token"}
    logging.warn("非法的access token")
    return make_response(400, e)
def EXPIRE_ACCESS_TOKEN():
    e = {"error":"过期的access token"}
    logging.warn("过期的access token")
    return make_response(400, e)

def require_auth(f):
    """Protect resource with specified scopes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' in request.headers:
            tok = request.headers.get('Authorization')[7:]
        else:
            return INVALID_ACCESS_TOKEN()
        t = token.AccessToken()
        if not t.load(rds, tok):
            return INVALID_ACCESS_TOKEN()
        if time.time() > t.expires:
            print t.expires, time.time()
            return EXPIRE_ACCESS_TOKEN()
        request.uid = t.user_id
        return f(*args, **kwargs)
    return wrapper
  
def web_requires_auth(f):
    @wraps(f)     
    def decorated(*args, **kwargs):        
        auth = web.ctx.env['HTTP_AUTHORIZATION'] if 'HTTP_AUTHORIZATION' in  web.ctx.env else None
        unauth = True
        if len(auth) > 7 and auth[:7] == "Bearer ":
            tok = auth[7:]
            t = token.AccessToken()
            if t.load(rds, tok) and time.time() < t.expires:
                unauth = False

        if unauth :
            web.ctx.status = '401 Unauthorized'
            return Unauthorized()

        web.ctx.uid = t.user_id
        return f(*args, **kwargs)
    
    return decorated
    
class Unauthorized():
    def GET(self):
        e = {"error":"401 Unauthorized"}
        web.header("Content-Type", "application/json")
        return json.dumps(e)

    def POST(self):
        e = {"error":"401 Unauthorized"}
        web.header("Content-Type", "application/json")
        return json.dumps(e)
      
UNICODE_ASCII_CHARACTER_SET = ('abcdefghijklmnopqrstuvwxyz'
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                               '0123456789')

def random_token_generator(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))

def create_token(expires_in, refresh_token=False):
    """Create a BearerToken, by default without refresh token."""

    token = {
        'access_token': random_token_generator(),
        'expires_in': expires_in,
        'token_type': 'Bearer',
    }
    if refresh_token:
        token['refresh_token'] = random_token_generator()

    return token


def login_gobelieve(uid, uname, appid, appsecret):
    url = config.GOBELIEVE_URL + "/auth/grant"
    obj = {"uid":uid, "user_name":uname}

    m = md5.new(appsecret)
    secret = m.hexdigest()
    basic = base64.b64encode(str(appid) + ":" + secret)

    headers = {'Content-Type': 'application/json; charset=UTF-8',
               'Authorization': 'Basic ' + basic}
     
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    if res.status_code != 200:
        logging.warning("login error:%s %s", res.status_code, res.text)
        return None

    obj = json.loads(res.text)
    return obj["data"]["token"]
