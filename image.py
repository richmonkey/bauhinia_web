from flask import request
from flask import Flask
import flask
import md5
import json
import os
from flask import request, Blueprint
from util import make_response
from authorization import require_auth
import config

app = Blueprint('image', __name__)

def image_ext(content_type):
    if content_type == "image/png":
        return ".png"
    elif content_type == "image/jpeg":
        return ".jpg"
    else:
        return ""

@app.route('/images', methods=['POST'])
@require_auth
def upload_image():
    if not request.data:
        return make_response(400)

    content_type = request.headers["Content-Type"] if request.headers.has_key("Content-Type") else ""
    ext = image_ext(content_type)
    if not ext:
        return make_response(400)

    data = request.data
    name = md5.new(data).hexdigest()
    path = os.path.join(config.IMAGE_PATH, name + ext)

    with open(path, "wb") as f:
        f.write(data)
    url = request.url_root + "images/" + name + ext
    src = "/images/" + name + ext
    obj = {"src":src, "src_url":url}
    return make_response(200, data=obj)

    
@app.route('/images/<image_path>', methods=['GET'])
def download_image(image_path):
    path = os.path.join(config.IMAGE_PATH, image_path)

    with open(path, "rb") as f:
        data = f.read()
        if not data:
            return flask.make_response("", 400)
        else:
            res = flask.make_response(data, 200)
            if image_path.endswith(".jpg"):
                res.headers['Content-Type'] = "image/jpeg"
            elif image_path.endswith(".png"):
                res.headers['Content-Type'] = "image/png"
            else:
                print "invalid image type"
            return res


