# -*- coding: utf-8 -*-
from flask import request
from flask import Flask
from flask import g
import flask
import md5
import json
import logging
import sys
import os
import redis
import authorization
import config

from views import auth
from views import user
from views import download
from views import image
from views import conference

app = Flask(__name__)
app.debug = config.DEBUG

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD, db=config.REDIS_DB)
auth.rds = rds
user.rds = rds
authorization.rds = rds


def before_request():
    logging.debug("before request")
    g.rds= rds

def app_teardown(exception):
    logging.debug('app_teardown')

    
# 初始化接口
def init_app(app):
    app.teardown_appcontext(app_teardown)
    app.before_request(before_request)    
    app.register_blueprint(auth.app)
    app.register_blueprint(user.app)
    app.register_blueprint(download.app)
    app.register_blueprint(image.app)
    app.register_blueprint(conference.app)

def init_logger(logger):
    root = logger
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(filename)s:%(lineno)d -  %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)    

log = logging.getLogger('')
init_logger(log)
init_app(app)

if len(sys.argv) > 1 and sys.argv[1] == "face":
    config.APP_ID = config.FACE_APP_ID
    config.APP_KEY = config.FACE_APP_KEY
    config.APP_SECRET = config.FACE_APP_SECRET
    config.APP_NAME = "电话虫"
else:
    config.APP_ID = config.BAUHINIA_APP_ID
    config.APP_KEY = config.BAUHINIA_APP_KEY
    config.APP_SECRET = config.BAUHINIA_APP_SECRET
    config.APP_NAME = "羊蹄甲"

if not os.path.exists(config.IMAGE_PATH):
    os.makedirs(config.IMAGE_PATH)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000)
