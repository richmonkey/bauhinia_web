import requests
import urllib
import urllib2
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import threading
import json
import sys

URL = "http://192.168.33.10"
#URL = "http://im.yufeng.me"

url = URL + "/verify_code?"
NUMBER = "13800000000"
values = {'zone' : '86', 'number' : NUMBER}
params = urllib.urlencode(values) 
url += params

r = requests.post(url)
print r.content
resp = json.loads(r.content)

code = resp["code"]
url = URL + "/auth/token"
values = {"zone":"86", "number":NUMBER, "code":code}
data = json.dumps(values)
r = requests.post(url, data=data)
print r.content
resp = json.loads(r.content)

print "access token:", resp["access_token"]
print "refresh token:", resp["refresh_token"]
access_token = resp["access_token"]
refresh_token = resp["refresh_token"]

url = URL + "/auth/refresh_token"
headers = {}
headers["Authorization"] = "Bearer " + access_token
 
values = {"refresh_token":refresh_token}
data = json.dumps(values)
r = requests.post(url, data=data, headers = headers)
print r.content
resp = json.loads(r.content)
 
print "access token:", resp["access_token"]
print "refresh token:", resp["refresh_token"]
access_token = resp["access_token"]
refresh_token = resp["refresh_token"]
 
url = URL + "/users/me"
headers = {}
headers["Authorization"] = "Bearer " + access_token
values = {"state":"xxxx"}
data = json.dumps(values)
r = requests.patch(url, data = data, headers = headers)
print r.status_code
 
 
url = URL + "/users"
headers = {}
headers["Authorization"] = "Bearer " + access_token
 
obj = [{"zone":"86", "number":"13800000009", "name":"test9"},
       {"zone":"86", "number":"13800000001", "name":"test1"}]
r = requests.post(url, data = json.dumps(obj), headers = headers)
print r.status_code
 
r = requests.get(url, headers = headers)
print "users:", r.text


url = URL + "/qrcode/session"
r = requests.get(url)
assert(r.status_code == 200)
obj = json.loads(r.content)
sid = obj["sid"]
print "new sid:", sid

def sweep_qrcode():
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    url = URL + "/qrcode/sweep"
    obj = {"sid":sid}
    r = requests.post(url, headers=headers, data=json.dumps(obj))
    print "sweep:", r.status_code
    return

t = threading.Thread(target=sweep_qrcode)
t.start()

url = URL + "/qrcode/login?sid=%s"%sid
r = requests.get(url)
assert(r.status_code == 200)
print "qrcode login success"

t.join()

