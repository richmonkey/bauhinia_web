# -*- coding: utf-8 -*-

from flask import request, g
from functools import wraps
from model.token import Token
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

#webpy 框架使用
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

        uid, expires = Token.load_access_token(g.rds, tok)
        uid = int(uid) if uid else 0
        expires = int(expires) if expires else 0
        if not uid:
            return INVALID_ACCESS_TOKEN()
        if time.time() > expires:
            logging.debug("access token expire")
            return EXPIRE_ACCESS_TOKEN()
        request.uid = uid
        return f(*args, **kwargs)
    return wrapper
  
def web_requires_auth(f):
    @wraps(f)     
    def decorated(*args, **kwargs):        
        auth = web.ctx.env['HTTP_AUTHORIZATION'] if 'HTTP_AUTHORIZATION' in  web.ctx.env else None
        unauth = True
        uid = 0
        if len(auth) > 7 and auth[:7] == "Bearer ":
            tok = auth[7:]
            uid, expires = Token.load_access_token(rds, tok)
            uid = int(uid) if uid else 0
            expires = int(expires) if expires else 0
            if uid and time.time() < expires:
                unauth = False

        if unauth :
            web.ctx.status = '401 Unauthorized'
            return Unauthorized()

        web.ctx.uid = uid
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
