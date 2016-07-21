from flask import request, Blueprint
from flask import redirect
import httpagentparser
from util import make_response

app = Blueprint('download', __name__)

def platforms():
    r = request.environ
    user_agent = r.get('HTTP_USER_AGENT')
    if not user_agent:
        user_agent = request.headers.get('User-Agent')
    print user_agent
    agt_parsed = httpagentparser.detect(user_agent)
    str_platform = None

    if 'WOW64' in user_agent:
        str_platform = 'win32'
    elif 'Win64' in user_agent:
        str_platform = 'win64'
    else:
        if 'os' in agt_parsed:
            str_platform = agt_parsed['os']['name'].lower()
        if 'dist' in agt_parsed:
            str_platform = agt_parsed['dist']['name'].lower()

    return str_platform


def is_voip():
    pos1 = request.base_url.find("http://voip")
    pos2 = request.base_url.find("http://face")
    return pos1 == 0 or pos2 == 0
    
def is_ios():
    platform = platforms()
    if platform == 'iphone' or platform == 'ipad' or platform == 'ios':
        return True
    else:
        return False

def message_package(is_ios):
    if is_ios:
        return "https://itunes.apple.com/us/app/yang-ti-jia/id923695740?mt=8"
    else:
        return "http://gdown.baidu.com/data/wisegame/1e513446470ee74a/yangtijia_2.apk"
    
def face_package(is_ios):
    if is_ios:
        return "https://itunes.apple.com/us/app/dian-hua-chong/id939167209?mt=8"
    else:
        return "http://p.gdown.baidu.com/a1a1c70d6927cb663b0b01bfe7105e475a27ec87047ce1ee860187276e7fead61e1b92e7ce5d055dc58f29b5df2eeb112f2cc0365081f5911dea2c85142c46de373043d4a33cbb2c031f5f4ce3454392488a5eb5c992f3e89b86eb91c530294f3ce0b32fc4ddb0fa22395128b6a542bfe29b45e8b41f1de2466870e2978a7ca0"

@app.route("/download", methods=["GET"])
def download():
    if is_voip():
        package_url = face_package(is_ios())
    else:
        package_url = message_package(is_ios())

    return redirect(package_url)

def face_app_version(is_ios):
    ver = {}
    ver["url"] = face_package(is_ios)
    if is_ios:
        ver["major"] = 1
        ver["minor"] = 0
    else:
        ver["major"] = 1
        ver["minor"] = 5
    return ver

def message_app_version(is_ios):
    ver = {}
    ver["url"] = message_package(is_ios)
    if is_ios:
        ver["major"] = 1
        ver["minor"] = 7
    else:
        ver["major"] = 1
        ver["minor"] = 0
    return ver

@app.route("/version/android", methods=["GET"])
def android_version():
    if is_voip():
        ver = face_app_version(False)
    else:
        ver = message_app_version(False)

    return make_response(200, ver)

@app.route("/version/ios", methods=["GET"])
def ios_version():
    if is_voip():
        ver = face_app_version(True)
    else:
        ver = message_app_version(True)

    return make_response(200, ver)
