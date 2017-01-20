# -*- coding: utf-8 -*-

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

#URL = "http://192.168.33.10:6000"
URL = "http://dev.gobelieve.io"
access_token = ""


    
def LoginUser():
    url = URL + "/verify_code?"
    NUMBER = "13800000000"
    values = {'zone' : '86', 'number' : NUMBER}
    params = urllib.urlencode(values) 
    url += params
     
    r = requests.post(url)
    print r.content
    resp = json.loads(r.content)
    code = resp["code"]

    url = URL + "/users/register"
    headers = {"Content-Type":"application/json"}
    
    values = {
        "nickname":"测试1",
        "password":"111111",
        "country_code":"86",
        "number":"13800000000",
        "code":code
    }
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "register:", r.status_code, r.content

    url = URL + "/users/login"
    headers = {"Content-Type":"application/json"}
    values = {
        "password":"111111",
        "country_code":"86",
        "number":"13800000000"
    }
    r = requests.post(url, data = data, headers = headers)
    print "login:", r.status_code, r.content

    return json.loads(r.content)['access_token']


    
def TestAcceptFriend():
    url = URL + "/users/login"
    headers = {"Content-Type":"application/json"}
    values = {
        "password":"111111",
        "country_code":"86",
        "number":"13800000000"
    }
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "login:", r.status_code, r.content
    resp0 = json.loads(r.content)

    
    url = URL + "/users/login"
    headers = {"Content-Type":"application/json"}
    values = {
        "password":"111111",
        "country_code":"86",
        "number":"13800000001"
    }
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "login:", r.status_code, r.content
    resp1 = json.loads(r.content)

    
    url = URL + "/friends/request"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + resp0['access_token']
    }
    #13800000000 -> 13800000001
    values = {"friend_uid":resp1['uid']}
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "request friend:", r.status_code, r.content

    request_id = json.loads(r.content)['request_id']


    url = URL + "/friends/accept"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + resp1['access_token']
    }

    values = {"uid":resp0['uid'], "request_id":request_id}
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "accept friend:", r.status_code, r.content


    #解除好友关系
    url = URL + "/friends/" + str(resp1['uid'])
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + resp0['access_token']
    }
    r = requests.delete(url, headers = headers)
    print "delete friend:", r.status_code, r.content


def TestRejectFriend():
    url = URL + "/users/login"
    headers = {"Content-Type":"application/json"}
    values = {
        "password":"111111",
        "country_code":"86",
        "number":"13800000000"
    }
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "login:", r.status_code, r.content
    resp0 = json.loads(r.content)

    
    url = URL + "/users/login"
    headers = {"Content-Type":"application/json"}
    values = {
        "password":"111111",
        "country_code":"86",
        "number":"13800000001"
    }
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "login:", r.status_code, r.content
    resp1 = json.loads(r.content)

    
    url = URL + "/friends/request"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + resp0['access_token']
    }
    #13800000000 -> 13800000001
    values = {"friend_uid":resp1['uid']}
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "request friend:", r.status_code, r.content

    request_id = json.loads(r.content)['request_id']


    url = URL + "/friends/reject"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + resp1['access_token']
    }

    values = {"uid":resp0['uid'], "request_id":request_id}
    data = json.dumps(values)
    r = requests.post(url, data = data, headers = headers)
    print "reject friend:", r.status_code, r.content
    
    


def LoginNumber():
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

    return access_token    
    
def TestUser():
    url = URL + "/users/me"
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    values = {"state":"xxxx"}
    data = json.dumps(values)
    r = requests.patch(url, data = data, headers = headers)
    print "set user state:", r.status_code
     
     
    url = URL + "/users/me"
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    values = {"name":"测试"}
    data = json.dumps(values)
    r = requests.patch(url, data = data, headers = headers)
    print "set user name:", r.status_code
     
     
    url = URL + "/users"
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
     
    obj = [{"zone":"86", "number":"13800000009", "name":"test9"},
           {"zone":"86", "number":"13800000001", "name":"test1"}]
    r = requests.post(url, data = json.dumps(obj), headers = headers)
    print "upload contact list:", r.status_code
     
    r = requests.get(url, headers = headers)
    print "users:", r.text

    
#二维码登录    
def TestQRCode():
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


def TestImage():
    url = URL + "/images"
    f = open("data/test.jpg", "rb")
    data = f.read()
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers["Content-Type"] = "image/jpeg"
    r = requests.post(url, data=data, headers = headers)
    assert(r.status_code == 200)
    image_url = json.loads(r.text)["src_url"]
    print "image url:", image_url
     
    r = requests.get(image_url, headers = headers)
    assert(r.status_code == 200)
    print "origin image len:", len(data), "image len:", len(r.content)






def TestVOIP():
    headers = {}
    headers["Authorization"] = "Bearer " + access_token
    headers["Content-Type"] = "application/json"
     
    url = URL + "/conferences"
    data = json.dumps({"channel_id":"11", "partipants":[13800000000, 13800000003]})
    r = requests.post(url, data=data, headers = headers)
    assert(r.status_code == 200)
    print "new conference:", r.content
     
     
    url = URL + "/calls"
    data = json.dumps({"channel_id":"11", "peer_uid":100})
    r = requests.post(url, data=data, headers = headers)
    assert(r.status_code == 200)
    print "new call:", r.content

access_token = LoginNumber()
TestUser()
TestVOIP()
TestQRCode()
TestImage()

access_token = LoginUser()
TestAcceptFriend()
TestRejectFriend()
