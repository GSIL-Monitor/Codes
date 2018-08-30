# -*- coding: utf-8 -*-
import sys, os
import time, datetime
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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../support'))
import loghelper, config
import util
import db

#logger
loghelper.init_logger("crawler_tianyancha", stream=True)
logger = loghelper.get_logger("crawler_tianyancha")

#mongo
(mongodb_host, mongodb_port) = config.get_mongodb_config()
mongo = MongoClient(mongodb_host, mongodb_port)

collection = mongo.crawler_v3.projectdata
collection.create_index([("source", pymongo.DESCENDING),
                         ("type", pymongo.DESCENDING),
                         ("key_int", pymongo.DESCENDING)], unique=False)
collection.create_index([("source", pymongo.DESCENDING),
                         ("type", pymongo.DESCENDING),
                         ("key", pymongo.DESCENDING)], unique=True)


#kafka
(kafka_url) = config.get_kafka_config()
kafka = KafkaClient(kafka_url)
# HashedPartitioner is default
kafka_producer = SimpleProducer(kafka)


SOURCE = 13090  #天眼查
TYPE = 36008    #工商

cnt = 0
total = 0

sgArr = [
    ["6", "b", "t", "f", "l", "5", "w", "h", "q", "i", "s", "e", "c", "p", "m", "u", "9", "8", "y", "2", "z", "k", "j", "r", "x", "n", "-", "0", "3", "4", "d", "1", "a", "o", "7", "v", "g"],
    ["1", "8", "o", "s", "z", "m", "b", "9", "f", "d", "7", "h", "c", "u", "n", "v", "p", "y", "2", "0", "3", "j", "-", "i", "l", "k", "t", "q", "4", "6", "r", "a", "w", "5", "e", "x", "g"],
    ["g", "a", "c", "t", "h", "u", "p", "f", "6", "x", "7", "0", "d", "i", "v", "e", "q", "4", "b", "5", "k", "w", "9", "s", "-", "j", "l", "y", "3", "o", "n", "z", "m", "2", "1", "r", "8"],
    ["s", "6", "h", "0", "y", "l", "d", "x", "e", "a", "k", "z", "u", "f", "4", "r", "b", "-", "p", "g", "3", "n", "m", "7", "o", "c", "i", "8", "v", "2", "1", "9", "q", "w", "t", "j", "5"],
    ["d", "4", "9", "m", "o", "i", "5", "k", "q", "n", "c", "s", "6", "b", "j", "y", "x", "l", "a", "v", "3", "t", "u", "h", "-", "r", "z", "2", "0", "7", "g", "p", "8", "f", "1", "w", "e"],
    ["z", "5", "g", "c", "h", "7", "o", "t", "2", "k", "a", "-", "e", "x", "y", "j", "3", "l", "1", "u", "s", "4", "b", "n", "8", "i", "6", "q", "p", "0", "d", "r", "v", "m", "w", "f", "9"],
    ["p", "x", "3", "d", "6", "5", "8", "k", "t", "l", "z", "b", "4", "n", "r", "v", "y", "m", "g", "a", "0", "1", "c", "9", "-", "2", "7", "q", "j", "h", "e", "w", "u", "s", "f", "o", "i"],
    ["q", "-", "u", "d", "k", "7", "t", "z", "4", "8", "x", "f", "v", "w", "p", "2", "e", "9", "o", "m", "5", "g", "1", "j", "i", "n", "6", "3", "r", "l", "b", "h", "y", "c", "a", "s", "0"],
    ["7", "-", "g", "x", "6", "5", "n", "u", "q", "z", "w", "t", "m", "0", "h", "o", "y", "p", "i", "f", "k", "s", "9", "l", "r", "1", "2", "v", "4", "e", "8", "c", "b", "a", "d", "j", "3"],
    ["1", "t", "8", "z", "o", "f", "l", "5", "2", "y", "q", "9", "p", "g", "r", "x", "e", "s", "d", "4", "n", "b", "u", "a", "m", "c", "h", "j", "3", "v", "i", "0", "-", "w", "7", "k", "6"]
]


def process_tongji(content, key):
        try:
            data = json.loads(content)
        except Exception,ex:
            return None, None

        v = data["data"]["v"]
        #logger.info(v)

        c = "%s" % ord(key[0])
        if len(c) > 1:
            index = int(c[1])
        else:
            index = int(c)
        SoGou = sgArr[index]

        str = ""
        for c in v.split(","):
            str += chr(int(c))

        (token,) = util.re_get_result("token=(.*?);",str)
        (s,) = util.re_get_result("return'(.*?)'",str)
        _utm = ""
        for c in s.split(","):
            _utm += SoGou[int(c)]
        return token, _utm


def get_proxy():
    conn = db.connect_torndb_crawler()
    proxy = conn.get("select * from proxy_tyc where status = 0 and DATE_ADD(createTime,INTERVAL 2 SECOND) < now() order by fail limit 1")
    #proxy = conn.get("select * from proxy where type like 'socks%%' order by rand() limit 1");
    #proxy = conn.get("select * from proxy where type='http' order by rand() limit 1");
    if proxy is not None:
        conn.execute("update proxy_tyc set status=1 where id=%s", proxy["id"])
        logger.info(proxy)
    conn.close()
    return proxy


def release_proxy(proxy):
    if proxy["id"] == 0:
        return
    conn = db.connect_torndb_crawler()
    conn.execute("update proxy_tyc set status=0, createTime=now() where id=%s", proxy["id"])
    conn.close()


def proxy_fail(proxy):
    if proxy["id"] == 0:
        return
    conn = db.connect_torndb_crawler()
    result = conn.get("select * from proxy_tyc where id=%s", proxy["id"])
    if result is not None:
        fail_num = result["fail"]
        if fail_num > 30:
            conn.execute("delete from proxy_tyc where id=%s", proxy["id"])
        else:
            conn.execute("update proxy_tyc set fail=%s where id=%s", fail_num+1, proxy["id"])
    conn.close()


def proxy_success(proxy):
    if proxy["id"] == 0:
        return
    conn = db.connect_torndb_crawler()
    conn.execute("update proxy_tyc set fail=%s where id=%s", 0, proxy["id"])
    conn.close()

def prepare_curl_socks4(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)


def prepare_curl_socks5(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)


def request(url, proxy, callback, headers=None):
    if headers is None:
        headers = {}
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0"

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
            #logger.info(response.headers.get_list("Set-Cookie"))
            TID = None
            for str in response.headers.get_list("Set-Cookie"):
                cookies = cookie_to_dict(str)
                TID = cookies.get("TID")
                if TID is not None:
                    break

            if TID is None:
                release_proxy(proxy)
                proxy_fail(proxy)
                first_request(key)
                return

            logger.info("TID=%s" % TID)

            #
            total += 1
            url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (key, int(time.time()*1000))
            headers = {"accept":"application/json",
                       "Cookie":"TID=%s" % TID}
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
            logger.info("TID=%s, token=%s, _utm=%s" % (TID, token, _utm))

            #
            total += 1
            url = "http://www.tianyancha.com/search/%s.json" % key
            headers = {"accept":"application/json",
                       "Tyc-From":"normal",
                       "Cookie":"TID=%s, token=%s, _utm=%s" % (TID, token, _utm)}
            request(url, proxy, lambda resp,key=key,proxy=proxy,TID=TID:handle_search_company_json(resp, key, proxy,TID), headers=headers)
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)


def handle_search_company_json(response, key, proxy, TID):
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
            elif status == 1:
                logger.info("tyc_company_id=%s" % tyc_company_id)
                total += 1
                url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (tyc_company_id, int(time.time()*1000))
                headers = {"accept":"application/json",
                           "Cookie":"TID=%s" % TID}
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
            logger.info("TID=%s, token=%s, _utm=%s" % (TID, token, _utm))

            #
            total += 1
            url = "http://www.tianyancha.com/company/%s.json" % tyc_company_id
            headers = {"accept":"application/json",
                       "Tyc-From":"normal",
                       "Cookie":"TID=%s, token=%s, _utm=%s" % (TID, token, _utm),
                       "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id}
            request(url, proxy, lambda resp,key=key,proxy=proxy,tyc_company_id=tyc_company_id:handle_search_company_id_json(resp, key, proxy,tyc_company_id), headers=headers)
        except:
            traceback.print_exc()

    total -= 1
    if total <=0:
        begin()
        #exit(0)

def handle_search_company_id_json(response, key, proxy,tyc_company_id):
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

    msg = {"source":SOURCE, "type":TYPE, "key":key}
    logger.info(json.dumps(msg))

    flag = False
    while flag == False:
        try:
            kafka_producer.send_messages("crawler_projectdata", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)

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
    global total, cnt
    if first:
        cnt += 1
        total += 1

    wait_time = 2
    while True:
        proxy = get_proxy()
        if proxy is None:
            #logger.info("proxy is None")
            yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, time.time() + wait_time)
            if wait_time < 10:
                wait_time += 2
            continue
        break

    #proxy = get_proxy()
    if first:
        if proxy is not None:
            url = "http://www.tianyancha.com/search/%s" % key
            request(url, proxy, lambda resp,key=key,proxy=proxy:handle_search_company(resp, key, proxy))
    else:
        if proxy is not None:
            url = "http://www.tianyancha.com/search/%s" % key
            request(url, proxy, lambda resp,key=key,proxy=proxy:handle_search_company(resp, key, proxy))
        else:
            proxy = {"id":0,"ip":"127.0.0.1","port":50000,"type":"socks4"}
            url = "http://www.tianyancha.com/search/%s" % key
            request(url, proxy, lambda resp,key=key,proxy=proxy:handle_search_company(resp, key, proxy))

def begin():
    global total, cnt
    NUM = 1000
    conn = db.connect_torndb()

    while True:
        conn2 = db.connect_torndb_crawler()
        result = conn2.get("select count(*) cnt from proxy_tyc where status = 0 and DATE_ADD(createTime,INTERVAL 2 SECOND) < now()")
        conn2.close()
        if result["cnt"] > 0:
            break
        time.sleep(5)

    while True:
        logger.info("cnt=%d" % cnt)

        cs = conn.query("select * from company_alias where type=12010 order by id limit %s,%s", cnt, NUM)
        if len(cs) <= 0:
            logger.info("Finish.")
            exit()

        request_num = 0
        for c in cs:
            key = c["name"].strip().replace("(", u"（").replace(")", u"）").\
                replace("?", "").replace(" ", "").replace("'","").\
                replace(".","").replace(";","")
            if key.find("/") != -1:
                cnt += 1
                continue
            if collection.find_one({"source":SOURCE, "type":TYPE, "key":key}) is not None:
                cnt += 1
                continue
            logger.info(key)
            first_request(key,first=True)
            request_num += 1

        if request_num == 0:
            continue
        else:
            break

    conn.close()

if __name__ == "__main__":
    logger.info("Start...")
    conn2 = db.connect_torndb_crawler()
    conn2.execute("update proxy_tyc set status=0")
    conn2.close()
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = AsyncHTTPClient(max_clients=5)
    begin()
    tornado.ioloop.IOLoop.instance().start()
