#!/usr/bin/env python 
#coding=utf-8 
import sys
import os
import traceback
import datetime, time
import urllib, urllib2
import hashlib
import json
import base64, hmac, binascii
from hashlib import sha1
from urllib import quote
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

register_openers()


def signature(values, secret):
    vals = []
    keys = sorted(values.keys())
    for key in keys:
        vals.append(str(values[key]))

    raw = "\n".join(vals)
    hashed = hmac.new(secret.encode('ascii'), raw, sha1)
    s =binascii.b2a_base64(hashed.digest())[:-1]
    sign = quote(s)

    return sign


# 获取机构的库列表
def getLibs(client_id, client_secret):
    values = {
        "client_id": client_id,
        "dateline": int(time.time()),
        "type": 1
    }

    sign = signature(values, client_secret)
    values["sign"] = sign
    data = urllib.urlencode(values)
    url = "http://yk3-api-ent.gokuai.com/1/org/ls"
    url += "?" + data
    #print url
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        strJson = response.read()
        #print strJson
        m = json.loads(strJson)
    except Exception,x:
        print traceback.print_exc()

        return None

    return m["list"]

# 获取库授权
def getLibToken(client_id, client_secret, org_id):
    values = {
        "client_id": client_id,
        "dateline": int(time.time()),
        'org_id':org_id
    }

    sign = signature(values, client_secret)
    values["sign"] = sign
    data = urllib.urlencode(values)
    url = "http://yk3-api-ent.gokuai.com/1/org/bind"
    url += "?" + data
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        strJson = response.read()
        #print strJson
        m = json.loads(strJson)
        org_client_id = m["org_client_id"]
        org_client_secret = m["org_client_secret"]
    except Exception,x:
        print traceback.print_exc()
        return None, None
    return (org_client_id, org_client_secret)


# 文件最近更新列表
def getUpdatedFileList(org_client_id,org_client_secret,fetch_dateline):
    values = {
            'org_client_id':org_client_id,
            'dateline':int(time.time()),
            'fetch_dateline':fetch_dateline,
            'mode':'compare'
    }

    sign = signature(values, org_client_secret)
    values["sign"] = sign
    data = urllib.urlencode(values)
    url = "http://yk3-api-ent.gokuai.com/1/file/updates"
    url += "?" + data
    #print url

    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        strJson = response.read()
        #print strJson
        m = json.loads(strJson)
    except Exception,x:
        print traceback.print_exc()
        return None
    return m


# 文件（夹）信息
def getFileInfo(org_client_id, org_client_secret, hash):
    values = {
            'org_client_id': org_client_id,
            'dateline': str(int(time.time())),
            'hash': hash,
    }

    sign = signature(values, org_client_secret)
    values["sign"] = sign
    data = urllib.urlencode(values)
    url = "http://yk3-api-ent.gokuai.com/1/file/info"
    url += "?" + data
    #print url

    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        strJson = response.read()
        #print strJson
        m = json.loads(strJson)
    except urllib2.HTTPError,e:
        #print e.code
        return None
    except Exception,x:
        print traceback.print_exc()
        return None
    return m


if __name__ == '__main__':
    client_id = "B6Mer0SRVQeNxG2UMkbcibAbWk"
    client_secret = "7Yfl58ZojwIAnmhSPx6qzM5PHnY"
    org_client_id, org_client_secret = getLibToken(client_id, client_secret, 473679)
    print org_client_id, org_client_secret
    result = getUpdatedFileList(org_client_id, org_client_secret, 0)
    print "fetch_dateline: ", result["fetch_dateline"]
    for f in result["list"]:
        hash = f["hash"]
        m = getFileInfo(org_client_id, org_client_secret, hash)
        print m["filename"], m.get("preview")