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
        return "http://p.gdown.baidu.com/1fc0b0a34ec86ac7f23e55b872f8ee6b086bb7f8ee57cf4f0d6b4115fcd52c748d6702952ed6850616395678ec67d58b33b5e725efe28db2ddf428ff848004e638fbe7c95b309bcb3c1e0f9b71e0b01ed8efe516cd86cf22ae00e3758ae8e06d7123b3e82b2a697b18cbfa319b2cab1f0f9bee94c225f2094bbcfc1f4a9e56276935b93f2c6f588d0169939b2aae94f2b0a34e375ecd8d4bacfef5f9a1cc12c1dc4ee305c8b8f2ed1e5b459bf94251816ffa8046e0df8fab20d0fc03f73757642c571e97bbcce9a012b8e0cbeed49e2e44996161e4e894097d6707d8863a1778ed54285e89d9b1c661b88a5c092a30a7669ecb915395858e13809f8c37646b6b213b26aeb56530c22454f1c3e513af12d4851adc5ab24e735a15120820137c199ddab2e6295d95e84a151479856024b6a668d0ceaa23778bbb2635dff1d62eabe6ae35164a4c442a9303a8383beba488"

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
        ver["minor"] = 6
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
