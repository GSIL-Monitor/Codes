# -*- coding: utf-8 -*-
# tornado 异步回调版本
import sys, os
import time, datetime
from urllib import quote
import random
import tornado.ioloop
import tornado.gen
from tornado.httpclient import AsyncHTTPClient
import json
import Cookie
import pycurl
import traceback
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, config
import util, name_helper
import db
import proxy_pool

#logger
loghelper.init_logger("crawler_tianyancha", stream=True)
logger = loghelper.get_logger("crawler_tianyancha")

#mongo
mongo = db.connect_mongo()
collection = mongo.raw.projectdata
collection_proxy = mongo.raw.proxy


SOURCE = 13090  #天眼查
TYPE = 36008    #工商

total = 0

success = 0
search = 0

sgArr_old = [
    #2
    ["6", "b", "t", "f", "2", "z", "l", "5", "w", "h", "q", "i", "s", "e", "c", "p", "m" ,"u", "9", "8", "y", "k", "j", "r", "x", "n", "-", "0", "3", "4", "d", "1", "a", "o", "7", "v", "g"],
    ["6", "b", "t", "f", "l", "5", "w", "h", "q", "i", "s", "e", "c", "p", "m", "u", "9", "8", "y", "2", "z", "k", "j", "r", "x", "n", "-", "0", "3", "4", "d", "1", "a", "o", "7", "v", "g"],

    #3
    ["1", "8", "o", "s", "z", "u", "n", "v", "m", "b", "9", "f", "d", "7", "h", "c", "p", "y", "2", "0", "3", "j", "-", "i", "l", "k", "t", "q", "4", "6", "r", "a", "w", "5", "e", "x", "g"],
    ["1", "8", "o", "s", "z", "m", "b", "9", "f", "d", "7", "h", "c", "u", "n", "v", "p", "y", "2", "0", "3", "j", "-", "i", "l", "k", "t", "q", "4", "6", "r", "a", "w", "5", "e", "x", "g"],

    #5
    ["x", "7", "0", "d", "i", "g", "a", "c", "t", "h", "u", "p", "f", "6", "v", "e", "q", "4", "b", "5", "k", "w", "9", "s", "-", "j", "l", "y", "3", "o", "n", "z", "m", "2", "1", "r", "8"],
    ["g", "a", "c", "t", "h", "u", "p", "f", "6", "x", "7", "0", "d", "i", "v", "e", "q", "4", "b", "5", "k", "w", "9", "s", "-", "j", "l", "y", "3", "o", "n", "z", "m", "2", "1", "r", "8"],

    #4
    ["s", "6", "h", "0", "p", "g", "3", "n", "m", "y", "l", "d", "x", "e", "a", "k", "z", "u", "f", "4", "r", "b", "-", "7", "o", "c", "i", "8", "v", "2", "1", "9", "q", "w", "t", "j", "5"],
    ["s", "6", "h", "0", "y", "l", "d", "x", "e", "a", "k", "z", "u", "f", "4", "r", "b", "-", "p", "g", "3", "n", "m", "7", "o", "c", "i", "8", "v", "2", "1", "9", "q", "w", "t", "j", "5"],

    #9
    ["d", "4", "9", "m", "o", "i", "5", "k", "q", "n", "c", "s", "6", "b", "j", "y", "x", "l", "a", "v", "3", "t", "u", "h", "-", "r", "z", "2", "0", "7", "g", "p", "8", "f", "1", "w", "e"],
    ["d", "4", "9", "m", "o", "i", "5", "k", "q", "n", "c", "s", "6", "b", "j", "y", "x", "l", "a", "v", "3", "t", "u", "h", "-", "r", "z", "2", "0", "7", "g", "p", "8", "f", "1", "w", "e"],

    #6
    ["z", "j", "3", "l", "1", "u", "s", "4", "5", "g", "c", "h", "7", "o", "t", "2", "k", "a", "-", "e", "x", "y", "b", "n", "8", "i", "6", "q", "p", "0", "d", "r", "v", "m", "w", "f", "9"],
    ["z", "5", "g", "c", "h", "7", "o", "t", "2", "k", "a", "-", "e", "x", "y", "j", "3", "l", "1", "u", "s", "4", "b", "n", "8", "i", "6", "q", "p", "0", "d", "r", "v", "m", "w", "f", "9"],

    #7
    ["j", "h", "p", "x", "3", "d", "6", "5", "8", "k", "t", "l", "z", "b", "4", "n", "r", "v", "y", "m", "g", "a", "0", "1", "c", "9", "-", "2", "7", "q", "e", "w", "u", "s", "f", "o", "i"],
    ["p", "x", "3", "d", "6", "5", "8", "k", "t", "l", "z", "b", "4", "n", "r", "v", "y", "m", "g", "a", "0", "1", "c", "9", "-", "2", "7", "q", "j", "h", "e", "w", "u", "s", "f", "o", "i"],

    #8
    ["8", "q", "-", "u", "d", "k", "7", "t", "z", "4", "x", "f", "v", "w", "p", "2", "e", "9", "o", "m", "5", "g", "1", "j", "i", "n", "6", "3", "r", "l", "b", "h", "y", "c", "a", "s", "0"],
    ["q", "-", "u", "d", "k", "7", "t", "z", "4", "8", "x", "f", "v", "w", "p", "2", "e", "9", "o", "m", "5", "g", "1", "j", "i", "n", "6", "3", "r", "l", "b", "h", "y", "c", "a", "s", "0"],

    #0
    ["7", "-", "g", "x", "6", "5", "n", "u", "q", "z", "w", "t", "m", "0", "h", "o", "y", "p", "i", "f", "k", "s", "9", "l", "r", "1", "2", "v", "4", "e", "8", "c", "b", "a", "d", "j", "3"],
    ["7", "-", "g", "x", "6", "5", "n", "u", "q", "z", "w", "t", "m", "0", "h", "o", "y", "p", "i", "f", "k", "s", "9", "l", "r", "1", "2", "v", "4", "e", "8", "c", "b", "a", "d", "j", "3"],

    #1
    ["1", "t", "8", "z", "o", "f", "l", "5", "2", "y", "q", "9", "p", "g", "r", "x", "e", "s", "d", "4", "n", "b", "u", "a", "m", "c", "h", "j", "3", "v", "i", "0", "-", "w", "7", "k", "6"],
    ["1", "t", "8", "z", "o", "f", "l", "5", "2", "y", "q", "9", "p", "g", "r", "x", "e", "s", "d", "4", "n", "b", "u", "a", "m", "c", "h", "j", "3", "v", "i", "0", "-", "w", "7", "k", "6"],
]

sgArr = [
    ["6", "b", "t", "f", "2", "z", "l", "5", "w", "h", "q", "i", "s", "e", "c", "p", "m" ,"u", "9", "8", "y", "k", "j", "r", "x", "n", "-", "0", "3", "4", "d", "1", "a", "o", "7", "v", "g"],
    ["1", "8", "o", "s", "z", "u", "n", "v", "m", "b", "9", "f", "d", "7", "h", "c", "p", "y", "2", "0", "3", "j", "-", "i", "l", "k", "t", "q", "4", "6", "r", "a", "w", "5", "e", "x", "g"],
    ["s", "6", "h", "0", "p", "g", "3", "n", "m", "y", "l", "d", "x", "e", "a", "k", "z", "u", "f", "4", "r", "b", "-", "7", "o", "c", "i", "8", "v", "2", "1", "9", "q", "w", "t", "j", "5"],
    ["x", "7", "0", "d", "i", "g", "a", "c", "t", "h", "u", "p", "f", "6", "v", "e", "q", "4", "b", "5", "k", "w", "9", "s", "-", "j", "l", "y", "3", "o", "n", "z", "m", "2", "1", "r", "8"],
    ["z", "j", "3", "l", "1", "u", "s", "4", "5", "g", "c", "h", "7", "o", "t", "2", "k", "a", "-", "e", "x", "y", "b", "n", "8", "i", "6", "q", "p", "0", "d", "r", "v", "m", "w", "f", "9"],
    ["j", "h", "p", "x", "3", "d", "6", "5", "8", "k", "t", "l", "z", "b", "4", "n", "r", "v", "y", "m", "g", "a", "0", "1", "c", "9", "-", "2", "7", "q", "e", "w", "u", "s", "f", "o", "i"],
    ["8", "q", "-", "u", "d", "k", "7", "t", "z", "4", "x", "f", "v", "w", "p", "2", "e", "9", "o", "m", "5", "g", "1", "j", "i", "n", "6", "3", "r", "l", "b", "h", "y", "c", "a", "s", "0"],
    ["d", "4", "9", "m", "o", "i", "5", "k", "q", "n", "c", "s", "6", "b", "j", "y", "x", "l", "a", "v", "3", "t", "u", "h", "-", "r", "z", "2", "0", "7", "g", "p", "8", "f", "1", "w", "e"],
    ["7", "-", "g", "x", "6", "5", "n", "u", "q", "z", "w", "t", "m", "0", "h", "o", "y", "p", "i", "f", "k", "s", "9", "l", "r", "1", "2", "v", "4", "e", "8", "c", "b", "a", "d", "j", "3"],
    ["1", "t", "8", "z", "o", "f", "l", "5", "2", "y", "q", "9", "p", "g", "r", "x", "e", "s", "d", "4", "n", "b", "u", "a", "m", "c", "h", "j", "3", "v", "i", "0", "-", "w", "7", "k", "6"],
]


def check_utm(_utm):
    if _utm is None or _utm == "":
        return False
    for s in _utm:
        if s not in ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']:
            return False
    return True


def process_tongji(content, key):
        #logger.info("key: %s", key)
        try:
            data = json.loads(content)
        except Exception,ex:
            return None, None

        v = data["data"]["v"]
        #logger.info(v)

        c = "%s" % ord(key[0])
        #logger.info("c=%s", c)
        if len(c) > 1:
            index = int(c[1])
        else:
            index = int(c)
        #logger.info("index=%s", index)
        SoGou = sgArr[index]

        str = ""
        for c in v.split(","):
            str += chr(int(c))

        (token,) = util.re_get_result("token=(.*?);",str)
        (s,) = util.re_get_result("return'(.*?)'",str)

        '''
        for m in sgArr:
            _utm = ""
            for c in s.split(","):
                _utm += m[int(c)]
            logger.info(_utm)
            if check_utm(_utm):
                break

        '''
        _utm = ""
        for c in s.split(","):
            _utm += SoGou[int(c)]

        if check_utm(_utm) is False:
            _utm = None

        return token, _utm


def get_proxy():
    # conn = db.connect_torndb_crawler()
    # proxy = conn.get("select * from proxy_tyc where status = 0 and DATE_ADD(createTime,INTERVAL 2 SECOND) < now() order by fail limit 1")
    # if proxy is not None:
    #     conn.execute("update proxy_tyc set status=1 where id=%s", proxy["id"])
    #     logger.info(proxy)
    # conn.close()

    # release_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
    proxy = mongo.raw.proxy_tyc.find_one({
            "$or":[{'status':0}, {'status':{'$exists':False}}]
    })
    if proxy is not None:
        logger.info(proxy)
        mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"status":1}})
    return proxy


def release_proxy(proxy):
    # if not proxy.has_key("id"):
    #     return
    # if proxy["id"] == 0:
    #     return
    # conn = db.connect_torndb_crawler()
    # conn.execute("update proxy_tyc set status=0, createTime=now() where id=%s", proxy["id"])
    # conn.close()
    mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"status":0,"releaseTime":datetime.datetime.utcnow()}})

def proxy_fail(proxy):
    # if not proxy.has_key("id"):
    #     return
    # if proxy["id"] == 0:
    #     return
    # conn = db.connect_torndb_crawler()
    # result = conn.get("select * from proxy_tyc where id=%s", proxy["id"])
    result = mongo.raw.proxy_tyc.find_one({"_id":proxy["_id"]})
    if result is not None:
        fail_num = result.get("fail",0)
        if fail_num > 15:
            # conn.execute("delete from proxy_tyc where id=%s", proxy["id"])
            mongo.raw.proxy_tyc.delete_one({"_id":proxy["_id"]})
        else:
            # conn.execute("update proxy_tyc set fail=%s where id=%s", fail_num+1, proxy["id"])
            mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"fail":fail_num+1}})
    #conn.close()


def proxy_success(proxy):
    # if not proxy.has_key("id"):
    #     return
    # if proxy["id"] == 0:
    #     return
    # conn = db.connect_torndb_crawler()
    # conn.execute("update proxy_tyc set fail=%s where id=%s", 0, proxy["id"])
    # conn.close()
    mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"fail": 0}})


def prepare_curl_socks4(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)


def prepare_curl_socks5(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)


def request(url, proxy, callback, headers=None):
    if headers is None:
        headers = {}
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    headers["Accept-Language"] = "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
    headers["Accept-Encoding"] = ""

    if proxy["type"].lower() == "socks4":
        http_request = tornado.httpclient.HTTPRequest(
            url,
            prepare_curl_callback=prepare_curl_socks4,
            proxy_host=proxy["ip"],
            proxy_port=int(proxy["port"]),
            headers=headers
        )
    else:
        http_request = tornado.httpclient.HTTPRequest(
            url,
            prepare_curl_callback=prepare_curl_socks5,
            proxy_host=proxy["ip"],
            proxy_port=int(proxy["port"]),
            headers=headers
        )
    '''
    http_request = tornado.httpclient.HTTPRequest(
            url,
            proxy_host=proxy["ip"],
            proxy_port=int(proxy["port"]),
            headers=headers
    )
    '''
    http_client.fetch(http_request, callback)


def cookie_to_dict(cookie):
    """Convert a string cookie into a dict"""
    cookie_dict = dict()
    C = Cookie.SimpleCookie(cookie)
    for morsel in C.values():
        cookie_dict[morsel.key] = morsel.value
    return cookie_dict


def handle_search_company(response, key, proxy):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        release_proxy(proxy)
        proxy_fail(proxy)
        first_request(key)
        return
    else:
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            #logger.info(response.headers.get_list("Set-Cookie"))
            TID = None
            if proxy.get("TYCID") is None:
                for str in response.headers.get_list("Set-Cookie"):
                    #logger.info(str)
                    cookies = cookie_to_dict(str)
                    TID = cookies.get("TYCID")
                    if TID is not None:
                        break
            else:
                TID = proxy["TYCID"]

            if TID is None:
                logger.info("TID is None")
                #logger.info(html)
                #for k,v in response.headers.get_all():
                #    logger.info("%s: %s", k,v)

                #conn = db.connect_torndb_crawler()
                #conn.execute("update proxy_tyc set TYCID=null where id=%s",proxy["id"])
                #conn.close()
                release_proxy(proxy)
                proxy_fail(proxy)
                first_request(key)
                return

            logger.info("TID=%s" % TID)
            if proxy.get("TYCID") is None:
                # conn = db.connect_torndb_crawler()
                # conn.execute("update proxy_tyc set TYCID=%s where id=%s", TID, proxy["id"])
                # conn.close()
                proxy["TYCID"] = TID
                mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"TYCID":TID}})

            if proxy.get("token") is None:
                cookie = "TYCID=%s, tnet=%s" % (TID,proxy["ip"])
            else:
                cookie = "TYCID=%s, tnet=%s, token=%s, _utm=%s" % (TID,proxy["ip"],proxy["token"],proxy["utm"])
            #
            total += 1
            url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (key, int(time.time()*1000))
            headers = {"accept":"application/json",
                       "Tyc-From":"normal",
                       "Cookie": cookie,
                       "CheckError":"check",
                       "Referer":"http://www.tianyancha.com/search/%s?checkFrom=searchBox" % key}
            request(url, proxy, lambda resp,key=key,proxy=proxy,TID=TID:handle_tongji_company(resp, key, proxy,TID), headers=headers)
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)


def handle_tongji_company(response, key, proxy, TID):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        release_proxy(proxy)
        proxy_fail(proxy)
        first_request(key)
        return
    else:
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            token, _utm = process_tongji(html, key)
            if TID is None or token is None or _utm is None:
                release_proxy(proxy)
                proxy_fail(proxy)
                first_request(key)
                return
            # conn = db.connect_torndb_crawler()
            # conn.execute("update proxy_tyc set token=%s, utm=%s where id=%s", token, _utm, proxy["ip"])
            # conn.close()
            mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"token": token, "utm":_utm}})
            logger.info("handle_tongji_company: TID=%s, token=%s, _utm=%s" % (TID, token, _utm))
            proxy["token"] = token
            proxy["utm"] = _utm

            #
            total += 1
            url = "http://www.tianyancha.com/search/%s.json?&pn=1" % key
            headers = {"accept":"application/json",
                       "Tyc-From":"normal",
                       "CheckError":"check",
                       "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (TID, token, _utm, proxy["ip"]),
                       "Referer":"http://www.tianyancha.com/search/%s?checkFrom=searchBox" % key}
            request(url, proxy, lambda resp,key=key,proxy=proxy,TID=TID:handle_search_company_json(resp, key, proxy,TID), headers=headers)
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)


def handle_search_company_json(response, key, proxy, TID):
    global total, success, search
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        release_proxy(proxy)
        proxy_fail(proxy)
        first_request(key)
        return
    else:
        #time.sleep(random.randint(1,10))

        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            status, tyc_company_id = process_search(html, key)
            if status == -1:
                release_proxy(proxy)
                proxy_fail(proxy)
                first_request(key)
                return
            elif status == 0 or status == -2:
                logger.info("%s Not Found!" % key)
                release_proxy(proxy)
                proxy_success(proxy)
                save(None, key, None, None, False)
                success += 1
                logger.info("success: %s", success)
            elif status == 1:
                logger.info("tyc_company_id=%s" % tyc_company_id)
                #test
                release_proxy(proxy)
                proxy_success(proxy)

                total += 1
                referer = "http://www.tianyancha.com/search/%s?checkFrom=searchBox" % key
                #logger.info("referer: %s", referer)
                url = "http://www.tianyancha.com/wxApi/getJsSdkConfig.json?url=%s" % quote(referer.encode("utf8"),'')
                #logger.info("url: %s", url)
                headers = {"accept":"application/json",
                           "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id,
                           "Tyc-From":"normal",
                           "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (TID, proxy["token"], proxy["utm"], proxy["ip"]),
                           }
                request(url, proxy, lambda resp,key=key,proxy=proxy,TID=TID,tyc_company_id=tyc_company_id:handle_getJsSdkConfig(resp, key, proxy,TID,tyc_company_id), headers=headers)

                '''
                total += 1
                url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (tyc_company_id, int(time.time()*1000))
                headers = {"accept":"application/json",
                           "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id,
                           "Tyc-From":"normal",
                           "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (TID, proxy["token"], proxy["utm"], proxy["ip"]),
                           }
                request(url, proxy, lambda resp,key=key,proxy=proxy,TID=TID,tyc_company_id=tyc_company_id:handle_tongji_company_id(resp, key, proxy,TID,tyc_company_id), headers=headers)
                '''

            search += 1
            logger.info("search: %s", search)
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)

def handle_getJsSdkConfig(response, key, proxy,TID,tyc_company_id):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        release_proxy(proxy)
        proxy_fail(proxy)
        first_request(key)
        return
    else:
        try:
            #html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            total += 1
            url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (tyc_company_id, int(time.time()*1000))
            headers = {"accept":"application/json",
                       "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id,
                       "Tyc-From":"normal",
                       "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (TID, proxy["token"], proxy["utm"], proxy["ip"]),
                       }
            request(url, proxy, lambda resp,key=key,proxy=proxy,TID=TID,tyc_company_id=tyc_company_id:handle_tongji_company_id(resp, key, proxy,TID,tyc_company_id), headers=headers)
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)

def handle_tongji_company_id(response, key, proxy,TID,tyc_company_id):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        release_proxy(proxy)
        proxy_fail(proxy)
        first_request(key)
        return
    else:
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            #logger.info(html)
            token, _utm = process_tongji(html, "%s" % tyc_company_id)
            if TID is None or token is None or _utm is None:
                release_proxy(proxy)
                proxy_fail(proxy)
                first_request(key)
                return
            logger.info("handle_tongji_company_id: TID=%s, token=%s, _utm=%s" % (TID, token, _utm))

            #test
            #release_proxy(proxy)
            #proxy_success(proxy)


            total += 1
            url = "http://www.tianyancha.com/company/%s.json" % tyc_company_id
            headers = {"accept":"application/json",
                       "Tyc-From":"normal",
                       "CheckError":"check",
                       "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (TID, token, _utm, proxy["ip"]),
                       "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id}
            request(url, proxy, lambda resp,key=key,proxy=proxy,tyc_company_id=tyc_company_id:handle_search_company_id_json(resp, key, proxy,tyc_company_id), headers=headers)

        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)

def handle_search_company_id_json(response, key, proxy,tyc_company_id):
    global total, success
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        release_proxy(proxy)
        proxy_fail(proxy)
        first_request(key)
        return
    else:
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            logger.info(html)
            try:
                content = json.loads(html)
                logger.info(content)
            except:
                release_proxy(proxy)
                proxy_fail(proxy)
                first_request(key)
                return

            release_proxy(proxy)
            proxy_success(proxy)
            url = "http://www.tianyancha.com/company/%s" % tyc_company_id
            save(url, key, tyc_company_id, content, True)
            success += 1
            logger.info("success: %s", success)

            total += 1
            referer = "http://www.tianyancha.com/company/%s" % tyc_company_id
            #logger.info("referer: %s", referer)
            url = "http://www.tianyancha.com/wxApi/getJsSdkConfig.json?url=%s" % quote(referer.encode("utf8"),'')
            logger.info("url: %s", url)
            headers = {"accept":"application/json",
                       "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id,
                       "Tyc-From":"normal",
                       "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
                       }
            request(url, proxy, lambda resp,key=key,proxy=proxy,TID=proxy["TYCID"],tyc_company_id=tyc_company_id:handle_getJsSdkConfig2(resp, key, proxy,TID,tyc_company_id), headers=headers)

        except:
            traceback.print_exc()
    total -= 1
    if total <=0:
        begin()
        #exit(0)

def handle_getJsSdkConfig2(response, key, proxy,TID,tyc_company_id):
    global total
    if response.error:
        logger.info("Error: %s, %s" % (response.error,response.request.url))
        release_proxy(proxy)
        proxy_fail(proxy)
        first_request(key)
        return
    else:
        try:
            html = unicode(response.body,encoding="utf-8",errors='replace')
            logger.info(html)
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)

def save(url, key, key_int, content, exist):
    collection_content = {
        "date":datetime.datetime.now(),
        "source":SOURCE,
        "type":TYPE,
        "url":url,
        "key":key,
        "key_int":key_int,
        "content":content,
        "exist":exist
    }

    if collection.find_one({"source":SOURCE, "type":TYPE, "key":key}) is not None:
        collection.delete_one({"source":SOURCE, "type":TYPE, "key":key})
    collection.insert_one(collection_content)

    update_time_by_company_name(key)

    #msg = {"source":SOURCE, "type":TYPE, "key":key}
    #logger.info(json.dumps(msg))


def process_search(content, key):
        try:
            data = json.loads(content)
            #logger.info(r.text)
        except:
            #logger.info(r.status_code)
            #logger.info(r.text)
            return -1, None
        if data["state"] != "ok":
            return -2, None

        for c in data["data"]:
            if c["name"].replace("<em>","").replace("</em>","").strip() == key:
                return 1, c["id"]

        return 0, None


@tornado.gen.engine
def first_request(key, first=False):
    global total
    if first:
        total += 1

    wait_time = 10
    while True:
        proxy = get_proxy()
        if proxy is None:
            #logger.info("proxy is None")
            yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + wait_time)
            #if wait_time < 10:
            #     wait_time += 2
            continue
        break
    wait_time = random.randrange(3,10)
    yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + wait_time)

    #proxy = get_proxy

    headers = {"accept":"application/json",
               "Referer":"http://www.tianyancha.com"}

    if proxy is not None:
        if proxy.get("TYCID") is not None:
            TID = proxy["TYCID"]
            if proxy.get("token") is None:
                cookie = "TYCID=%s, tnet=%s" % (TID,proxy["ip"])
            else:
                cookie = "TYCID=%s, tnet=%s, token=%s, _utm=%s" % (TID,proxy["ip"],proxy["token"],proxy["utm"])

            url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (key, int(time.time()*1000))
            headers = {"accept":"application/json",
                       "Tyc-From":"normal",
                       "CheckError":"check",
                       "Cookie": cookie,
                       "Referer":"http://www.tianyancha.com/search/%s?checkFrom=searchBox" % key}
            request(url, proxy, lambda resp,key=key,proxy=proxy,TID=TID:handle_tongji_company(resp, key, proxy,TID), headers=headers)
        else:
            url = "http://www.tianyancha.com/search/%s" % key
            request(url, proxy, lambda resp,key=key,proxy=proxy:handle_search_company(resp, key, proxy), headers=headers)



def update_time(row_id):
    conn = db.connect_torndb()
    # sql = "update source_company_name set gongshangCheckTime=now() where id=%s"
    sql = "update company_alias set gongshangCheckTime=now() where id=%s"
    #logger.info(sql, row_id)
    conn.update(sql, row_id)
    conn.close()

def update_time_by_company_name(name):
    conn = db.connect_torndb()
    sql = "update company_alias set gongshangCheckTime=now() where name=%s"
    #logger.info(sql, row_id)
    conn.update(sql, name)
    conn.close()


def begin():
    global total
    NUM = 100

    # while True:
    #     conn2 = db.connect_torndb_crawler()
    #     result = conn2.get("select count(*) cnt from proxy_tyc where status = 0 and DATE_ADD(createTime,INTERVAL 2 SECOND) < now()")
    #     conn2.close()
    #     if result["cnt"] > 0:
    #         break
    #     time.sleep(5)

    #time.sleep(random.randint(1,10))

    while True:
        has_request = False
        conn = db.connect_torndb()
        company_aliases = conn.query("select * from company_alias where type=12010 and "
                                     "(gongshangCheckTime is null or gongshangCheckTime < date_sub(now(),interval 30 day)) "
                                     "order by id desc limit %s",
                                     NUM)
        #company_aliases = conn.query("select * from company_alias where type=12010 and gongshangCheckTime is null order by id desc limit %s", NUM)
        #company_aliases = conn.query("select * from company_alias where id=428826")
        conn.close()
        if len(company_aliases) <= 0:
            logger.info("Finish.")
            time.sleep(60)
            logger.info("Start...")
            continue

        for alias in company_aliases:
            company_name = alias["name"]
            #NAME CHECK
            chinese, is_company = name_helper.name_check(company_name)
            if chinese and is_company:
                logger.info(company_name)
                first_request(company_name,first=True)
                has_request = True
            else:
                update_time(alias["id"])

        if has_request:
            break


def process_tongji_test(content, key, index):
        try:
            data = json.loads(content)
        except Exception,ex:
            return None, None

        v = data["data"]["v"]
        #logger.info(v)
        '''
        c = "%s" % ord(key[0])
        if len(c) > 1:
            index = int(c[1])
        else:
            index = int(c)
        '''
        SoGou = sgArr[index]

        str = ""
        for c in v.split(","):
            str += chr(int(c))
        print str

        (token,) = util.re_get_result("token=(.*?);",str)
        (s,) = util.re_get_result("return'(.*?)'",str)
        _utm = ""
        for c in s.split(","):
            _utm += SoGou[int(c)]
        return token, _utm


if __name__ == "__main__":
    logger.info("Start...")
    # conn2 = db.connect_torndb_crawler()
    # conn2.execute("update proxy_tyc set status=0")
    # conn2.close()
    mongo.raw.proxy_tyc.update_many({},{"$set":{"status":0}})

    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=10)
    begin()
    tornado.ioloop.IOLoop.instance().start()


    '''
    content = '{"state":"ok","message":"","data":{"name":"2350564024","uv":380498,"pv":909802,"v":"33,102,117,110,99,116,105,111,110,40,110,41,123,100,111,99,117,109,101,110,116,46,99,111,111,107,105,101,61,39,116,111,107,101,110,61,50,52,97,51,51,55,51,50,55,50,56,101,52,49,100,54,97,49,100,51,50,97,102,50,48,57,99,54,55,54,53,97,59,112,97,116,104,61,47,59,39,59,110,46,119,116,102,61,102,117,110,99,116,105,111,110,40,41,123,114,101,116,117,114,110,39,49,51,44,49,56,44,50,55,44,49,57,44,49,51,44,51,44,55,44,49,52,44,51,49,44,51,49,44,50,57,44,51,44,50,57,44,51,49,44,49,44,49,56,44,49,57,44,49,56,44,51,44,49,57,44,51,49,44,51,50,44,51,52,44,48,44,52,44,51,44,50,55,44,50,57,44,51,52,44,51,50,44,48,44,51,52,39,125,125,40,119,105,110,100,111,119,41,59"}}'
    key = "2350564024"

    for i in range(0,len(sgArr)):
        token, _utm = process_tongji_test(content,key,i)
        print token
        print _utm

    '''
    '''
    str = ""
    #l = [119,105,110,100,111,119,46,36,83,111,71,111,117,36,32,61,32,119,105,110,100,111,119,46,95,115,103,65,114,114,91,2,93]
    l = [105, 102, 40, 119, 105, 110, 100, 111, 119, 46, 119, 116, 102, 41, 123, 118, 97, 114, 32, 102, 120, 99, 107, 32, 61, 32, 119, 105, 110, 100, 111, 119, 46, 119, 116, 102, 40, 41, 46, 115, 112, 108, 105, 116, 40, 34, 44, 34, 41, 59, 118, 97, 114, 32, 102, 120, 99, 107, 83, 116, 114, 32, 61, 32, 34, 34, 59, 102, 111, 114, 40, 118, 97, 114, 32, 105, 61, 48, 59, 105, 60, 102, 120, 99, 107, 46, 108, 101, 110, 103, 116, 104, 59, 105, 43, 43, 41, 123, 102, 120, 99, 107, 83, 116, 114, 43, 61, 119, 105, 110, 100, 111, 119, 46, 36, 83, 111, 71, 111, 117, 36, 91, 102, 120, 99, 107, 91, 105, 93, 93, 59, 125, 100, 111, 99, 117, 109, 101, 110, 116, 46, 99, 111, 111, 107, 105, 101, 32, 61, 32, 34, 95, 117, 116, 109, 61, 34, 43, 102, 120, 99, 107, 83, 116, 114, 43, 34, 59, 112, 97, 116, 104, 61, 47, 59, 34, 59, 119, 105, 110, 100, 111, 119, 46, 119, 116, 102, 32, 61, 32, 110, 117, 108, 108, 59, 125]
    for c in l:
        str += chr(c)
        #print chr(c)
    print str
    '''
