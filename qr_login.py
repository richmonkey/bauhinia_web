# -*- coding: utf-8 -*-

import qrcode
from gevent import monkey
monkey.patch_socket()
import web
import json
import redis
from lib import gobelieve
from model.token import Token
from authorization import random_token_generator
import config
import logging
import sys
from error import Error


TOKEN_EXPIRE = 3600*12

urls = (
  '/qrcode/login', 'QRLogin',
)

app = web.application(urls, globals())

class Session:
    def __init__(self):
        self.sid = None
        self.uid = None
        self.is_valid = False

    def save(self, rds):
        key = "session_" + self.sid
        pipe = rds.pipeline()
        pipe.set(key, self.uid)
        pipe.expire(key, 30*60)
        pipe.execute()

    def load(self, rds):
        key = "session_" + self.sid
        self.is_valid = rds.exists(key)
        if self.is_valid:
            self.uid = rds.get(key)
    def expire(self, rds, time):
        key = "session_" + self.sid
        rds.expire(key, time)
        

def wait_sweep(sid):
    key = "session_queue_" + sid
    rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD, db=config.REDIS_DB)
    e = rds.brpop(key, timeout=55)
    return e

class QRLogin:
    def loginSession(self, session, rds):
        access_token = gobelieve.login_gobelieve(int(session.uid), "")
        if not access_token:
            raise Error(404, "imsdk can't login")

        tok = {
            'expires_in': TOKEN_EXPIRE,
            'token_type': 'Bearer',
            "access_token":access_token,
            "refresh_token":random_token_generator(),
            'uid':int(session.uid),
            'sid':session.sid
        }        
        Token.save_access_token(rds, access_token, int(session.uid), TOKEN_EXPIRE)
        session.expire(rds, TOKEN_EXPIRE)
        
        web.setcookie("sid", session.sid, TOKEN_EXPIRE)
        web.setcookie("token", access_token, TOKEN_EXPIRE)
        return json.dumps(tok)
        
    def GET(self):
        logging.debug("qrcode login")
        rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD, db=config.REDIS_DB)
        sid = web.input().sid
        session = Session()
        session.sid = sid
        session.load(rds)
         
        if not session.is_valid:
            logging.debug("sid not found")
            raise Error(404, "sid not found")
         
        if session.uid:
            #已经登录
            return self.loginSession(session, rds)
         
        e = wait_sweep(sid)
        if not e:
            logging.debug("qrcode login timeout")
            raise Error(400, "timeout")

        session.load(rds)
        if not session.is_valid:
            raise Error(404, "sid not found")
         
        if session.uid:
            #登录成功
            return self.loginSession(session, rds)

        logging.warning("session login fail")
        raise Error(400, "timeout")


def init_logger(logger):
    root = logger
    root.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(filename)s:%(lineno)d- %(asctime)s-%(levelname)s - %(message)s')

log = logging.getLogger('')
init_logger(log)
logging.debug("startup")

config.APP_ID = config.BAUHINIA_APP_ID
config.APP_KEY = config.BAUHINIA_APP_KEY
config.APP_SECRET = config.BAUHINIA_APP_SECRET
config.APP_NAME = "羊蹄甲"
    
application = app.wsgifunc()

if __name__ == "__main__": 
    app.run()
