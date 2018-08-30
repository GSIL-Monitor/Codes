# -*- coding: utf-8 -*-
# tornado yield 同步化版本
import sys, os
import datetime, time
import traceback
from tornado import httpclient, gen, ioloop, queues
import pycurl
import Cookie
import json
from urllib import quote
import random
import threading

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper, util, name_helper

#logger
loghelper.init_logger("tianyancha_gongshang2")
logger = loghelper.get_logger("tianyancha_gongshang2")

concurrency = 1
SOURCE = 13090  #天眼查
TYPE = 36008    #工商

Q = queues.Queue()

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


@gen.coroutine
def get_proxy():
    wait_time = 10
    while True:
        mongo = db.connect_mongo()
        proxy = mongo.raw.proxy_tyc.find_one({
                "$or":[{'status':0}, {'status':{'$exists':False}}]
        }, sort=[("fail", 1)])
        if proxy is not None:
            logger.info(proxy)
            mongo = db.connect_mongo()
            mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"status":1}})
        mongo.close()

        if proxy is None:
            yield gen.sleep(wait_time)
            continue

        raise gen.Return(proxy)


def release_proxy(proxy):
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"status":0,"releaseTime":datetime.datetime.utcnow()}})
    mongo.close()


def proxy_fail(proxy):
    mongo = db.connect_mongo()
    result = mongo.raw.proxy_tyc.find_one({"_id":proxy["_id"]})
    if result is not None:
        fail_num = result.get("fail",0)
        if fail_num > 15:
            mongo.raw.proxy_tyc.delete_one({"_id":proxy["_id"]})
        else:
            mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"fail":fail_num+1}})
    mongo.close()


def proxy_success(proxy):
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"fail": 0}})
    mongo.close()


def check_utm(_utm):
    if _utm is None or _utm == "":
        return False
    for s in _utm:
        if s not in ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']:
            return False
    return True


def process_tongji(content, key):
        # logger.info("key: %s", key)
        try:
            data = json.loads(content)
        except Exception, ex:
            return None, None

        try:
            v = data["data"]["v"]
            # logger.info(v)

            c = "%s" % ord(key[0])
            # logger.info("c=%s", c)
            if len(c) > 1:
                index = int(c[1])
            else:
                index = int(c)
            # logger.info("index=%s", index)
            SoGou = sgArr[index]

            str = ""
            for c in v.split(","):
                str += chr(int(c))

            (token,) = util.re_get_result("token=(.*?);", str)
            (s,) = util.re_get_result("return'(.*?)'", str)

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
        except Exception, ex:
            return None, None


def prepare_curl_socks4(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)

def prepare_curl_socks5(curl):
    curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)

@gen.coroutine
def request(proxy, url, headers=None):
    logger.info("request: %s", url)
    if headers is None:
        headers = {}
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.4.8 (KHTML, like Gecko)"
    headers["Accept-Language"] = "zh-CN,zh;q=0.5,en;q=0.3"
    headers["Accept-Encoding"] = ""

    if proxy["type"].lower() == "socks4":
        http_request = httpclient.HTTPRequest(
            url,
            prepare_curl_callback=prepare_curl_socks4,
            proxy_host=proxy["ip"],
            proxy_port=int(proxy["port"]),
            headers=headers
        )
    else:
        http_request = httpclient.HTTPRequest(
            url,
            prepare_curl_callback=prepare_curl_socks5,
            proxy_host=proxy["ip"],
            proxy_port=int(proxy["port"]),
            headers=headers
        )

    response = None
    try:
        client = httpclient.AsyncHTTPClient()
        client.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        response = yield client.fetch(http_request, raise_error=False)
    except Exception as e:
        # traceback.print_exc()
        logger.info("fetch error!")

    if response is not None:
        if response.error:
            logger.info("Error: %s, %s" % (response.error, response.request.url))
            logger.info("proxy: %s", response.request.proxy_host)
        else:
            raise gen.Return(response)

    release_proxy(proxy)
    proxy_fail(proxy)
    raise gen.Return(None)


def cookie_to_dict(cookie):
    """Convert a string cookie into a dict"""
    cookie_dict = dict()
    C = Cookie.SimpleCookie(cookie)
    for morsel in C.values():
        cookie_dict[morsel.key] = morsel.value
    return cookie_dict


@gen.coroutine
def step1(proxy, company_name):
    # 搜索公司页，获得TYCID
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com",
               }
    url = "http://www.tianyancha.com/search?key=%s&checkFrom=searchBox" % quote(company_name.encode("utf8"))
    response = yield request(proxy, url, headers=headers)
    if response is None:
        raise gen.Return(False)

    try:
        html = unicode(response.body, encoding="utf-8", errors='replace')
        # logger.info(html)
        # logger.info(response.headers.get_list("Set-Cookie"))
        TYCID = None
        for str in response.headers.get_list("Set-Cookie"):
            # logger.info(str)
            cookies = cookie_to_dict(str)
            TYCID = cookies.get("TYCID")
            if TYCID is not None:
                break
    except:
        traceback.print_exc()

    if TYCID is not None:
        logger.info("step1: TYCID=%s" % TYCID)
        mongo = db.connect_mongo()
        proxy["TYCID"] = TYCID
        mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"TYCID": TYCID}})
        mongo.close()
        raise gen.Return(True)

    logger.info("step1: can't get TYCID")
    release_proxy(proxy)
    proxy_fail(proxy)
    raise gen.Return(False)


@gen.coroutine
def step2(proxy, company_name):
    TYCID = proxy["TYCID"]
    if proxy.get("token") is None:
        cookie = "TYCID=%s, tnet=%s" % (TYCID, proxy["ip"])
    else:
        cookie = "TYCID=%s, tnet=%s, token=%s, _utm=%s" % (TYCID, proxy["ip"], proxy["token"], proxy["utm"])

    url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (quote(company_name.encode("utf8")), int(time.time() * 1000))
    headers = {"accept": "application/json",
               "Tyc-From": "normal",
               "CheckError": "check",
               "Cookie": cookie,
               "Referer": "http://www.tianyancha.com/search?key=%s?checkFrom=searchBox" % company_name}
    response = yield request(proxy, url, headers=headers)
    if response is None:
        raise gen.Return(False)

    try:
        html = unicode(response.body, encoding="utf-8", errors='replace')
    except:
        traceback.print_exc()

    # logger.info(html)
    token, _utm = process_tongji(html, company_name)
    if token is None or _utm is None:
        logger.info(html)
        logger.info("step2: can't get token,_utm")
        release_proxy(proxy)
        proxy_fail(proxy)
        raise gen.Return(False)

    proxy["token"] = token
    proxy["utm"] = _utm
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"token": token, "utm": _utm}})
    mongo.close()
    logger.info("step2: TYCID=%s, token=%s, _utm=%s" % (TYCID, token, _utm))
    raise gen.Return(True)


def process_search(content, key):
        try:
            data = json.loads(content)
            # logger.info(r.text)
        except:
            # logger.info(r.status_code)
            # logger.info(r.text)
            return -1, None
        if data["state"] != "ok":
            return -2, None

        for c in data["data"]:
            if c["name"].replace("<em>", "").replace("</em>", "").strip() == key:
                return 1, c["id"]

        return 0, None


@gen.coroutine
def step3(proxy, company_name):
    # search
    url = "http://www.tianyancha.com/v2/search/%s.json?" % quote(company_name.encode("utf8"))
    headers = {"accept": "application/json",
               "Tyc-From": "normal",
               "CheckError": "check",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               "Referer": "http://www.tianyancha.com/search/%s?checkFrom=searchBox" % company_name}
    response = yield request(proxy, url, headers=headers)
    if response is None:
        raise gen.Return(-1)

    try:
        html = unicode(response.body, encoding="utf-8", errors='replace')
    except:
        traceback.print_exc()

    # logger.info(html)
    status, tyc_company_id = process_search(html, company_name)
    if status == -1:
        release_proxy(proxy)
        proxy_fail(proxy)
        raise gen.Return(-1)
    elif status == 0 or status == -2:
        logger.info("%s Not Found!" % company_name)
        release_proxy(proxy)
        proxy_success(proxy)
        raise gen.Return(0)

    logger.info("step3: tyc_company_id=%s" % tyc_company_id)
    raise gen.Return(tyc_company_id)


@gen.coroutine
def step4(proxy, company_name, tyc_company_id):
    referer = "http://www.tianyancha.com/search/%s?checkFrom=searchBox" % quote(company_name.encode("utf8"))
    url = "http://www.tianyancha.com/wxApi/getJsSdkConfig.json?url=%s" % quote(referer.encode("utf8"), '')
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com/company/%s" % tyc_company_id,
               "Tyc-From": "normal",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               }
    response = yield request(proxy, url, headers=headers)
    if response is None:
        raise gen.Return(False)

    raise gen.Return(True)


@gen.coroutine
def step5(proxy, company_name, tyc_company_id):
    url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (tyc_company_id, int(time.time() * 1000))
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com/company/%s" % tyc_company_id,
               "Tyc-From": "normal",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               }
    response = yield request(proxy, url, headers=headers)
    if response is None:
        raise gen.Return(False)

    try:
        html = unicode(response.body,encoding="utf-8",errors='replace')
    except:
        traceback.print_exc()

    #logger.info(html)
    token, _utm = process_tongji(html, "%s" % tyc_company_id)
    if token is None or _utm is None:
        release_proxy(proxy)
        proxy_fail(proxy)
        raise gen.Return(False)

    proxy["token"] = token
    proxy["utm"] = _utm
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"token": token, "utm": _utm}})
    mongo.close()
    logger.info("step5: TYCID=%s, token=%s, _utm=%s" % (proxy["TYCID"], token, _utm))

    raise gen.Return(True)


@gen.coroutine
def step6(proxy, company_name, tyc_company_id):
    url = "http://www.tianyancha.com/company/%s.json" % tyc_company_id
    headers = {"accept":"application/json",
               "Tyc-From":"normal",
               "CheckError":"check",
               "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id}
    response = yield request(proxy, url, headers=headers)
    if response is None:
        raise gen.Return(False)

    try:
        html = unicode(response.body, encoding="utf-8", errors='replace')
        logger.info("step6: ")
        logger.info(html)
    except:
        traceback.print_exc()

    try:
        content = json.loads(html)
        #logger.info(content)
    except:
        release_proxy(proxy)
        proxy_fail(proxy)
        raise gen.Return(False)

    url = "http://www.tianyancha.com/company/%s" % tyc_company_id
    save(url, company_name, tyc_company_id, content, True)
    logger.info("step6: success")

    raise gen.Return(True)

def save(url, company_name, tyc_company_id, content, exist):
    collection_content = {
        "date":datetime.datetime.utcnow(),
        "source":SOURCE,
        "type":TYPE,
        "url":url,
        "key":company_name,
        "key_int":tyc_company_id,
        "content":content,
        "exist":exist
    }

    mongo = db.connect_mongo()
    if mongo.raw.projectdata.find_one({"source":SOURCE, "type":TYPE, "key":company_name}) is not None:
        mongo.raw.projectdata.delete_one({"source":SOURCE, "type":TYPE, "key":company_name})
    mongo.raw.projectdata.insert_one(collection_content)
    mongo.close()


@gen.coroutine
def step7(proxy, company_name, tyc_company_id):
    referer = "http://www.tianyancha.com/company/%s" % tyc_company_id
    url = "http://www.tianyancha.com/wxApi/getJsSdkConfig.json?url=%s" % quote(referer.encode("utf8"), '')
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com/company/%s" % tyc_company_id,
               "Tyc-From": "normal",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               }
    response = yield request(proxy, url, headers=headers)
    if response is None:
        raise gen.Return(False)

    raise gen.Return(True)


@gen.coroutine
def process(company):
    company_name = name_helper.company_name_normalize(company["name"])
    company_name = company_name.replace("'","")
    while True:
        proxy = yield get_proxy()
        wait_time = random.randrange(3, 10)
        yield gen.sleep(wait_time)

        TYCID = proxy.get("TYCID")
        if TYCID is None:
            # step1
            # 搜索公司页，获得TYCID
            flag = yield step1(proxy, company_name)
            if flag is False:
                continue

        # step2
        # 已有TYCID, 访问/tongji/companyname.json
        flag = yield step2(proxy, company_name)
        if flag is False:
            continue

        # step3
        # 搜索获得tyc_company_id
        tyc_company_id = yield step3(proxy, company_name)
        if tyc_company_id == -1:
            continue
        elif tyc_company_id == 0:
            # 搜不到
            update_check_time(company, exist=False)
            break

        wait_time = random.randrange(1, 3)
        yield gen.sleep(wait_time)

        # step4
        flag = yield step4(proxy, company_name, tyc_company_id)
        if flag is False:
            continue

        # step5
        flag = yield step5(proxy, company_name, tyc_company_id)
        if flag is False:
            continue

        # step6
        flag = yield step6(proxy, company_name, tyc_company_id)
        if flag is False:
            continue
        update_check_time(company, exist=True)

        # step7
        yield step7(proxy, company_name, tyc_company_id)

        release_proxy(proxy)
        proxy_success(proxy)
        yield gen.sleep(1)
        break


def update_check_time(company, exist):
    if company.has_key("_id"):
        mongo = db.connect_mongo()
        mongo.info.company_idx.update_one({"_id":company["_id"]},
                                          {"$set":{
                                              "tycCheckTime":datetime.datetime.utcnow(),
                                              "tycCheckExist": exist
                                          }})
        if exist:
            mongo.info.company_idx.update_one({"_id": company["_id"]},
                                              {"$set": {
                                                  "tycCheckExistTime": datetime.datetime.utcnow()
                                              }})
        mongo.close()
    else:
        conn = db.connect_torndb()
        sql = "update company_alias set gongshangCheckTime=now() where id=%s"
        conn.update(sql, company["id"])
        conn.close()


@gen.coroutine
def fetch_company(index):
    while True:
        company = yield Q.get()
        try:
            logger.info('worker: %s, fetching: %s',index, company["name"])
            # chinese, iscompany = name_helper.name_check(company["name"])
            # if chinese is True and iscompany is True:
            #     yield process(company)
            # else:
            #     update_check_time(company, False)
            # 公司名有英文字符
            # IDG资本投资顾问（北京）有限公司

            if "/" in company["name"]:
                update_check_time(company, False)
            else:
                yield process(company)
        finally:
            Q.task_done()


@gen.coroutine
def worker(index):
    while True:
        yield fetch_company(index)


@gen.coroutine
def main():
    for index in range(concurrency):
        worker(index)

    while True:
        conn = db.connect_torndb()
        company_aliases = conn.query("select * from company_alias where type=12010 and "
                                     "(gongshangCheckTime is null or gongshangCheckTime < date_sub(now(),interval 25 day)) "
                                     "order by id desc limit %s", concurrency*20)
        conn.close()

        mongo = db.connect_mongo()
        cs = list(mongo.info.company_idx.find({
                "$or":[
                    {"tycCheckTime": None},
                    {"tycCheckTime": {"$lt":datetime.datetime.now()-datetime.timedelta(days=30)}}
                ]
        }).sort('_id', -1).limit(concurrency*20))
        mongo.close()

        if len(cs) > 0 or len(company_aliases)>0:
            logger.info("***********Batch fetch begin****************")
            for c in company_aliases:
                Q.put(c)
            for c in cs:
                Q.put(c)
            yield Q.join()
            logger.info("***********Batch fetch end****************")
        else:
            logger.info("***********No task****************")
            time.sleep(60)


if __name__ == '__main__':
    logger.info("Start.")
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update_many({}, {"$set": {"status": 0}})
    mongo.close()

    import logging
    logging.basicConfig()
    httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

    io_loop = ioloop.IOLoop().current()
    io_loop.run_sync(main)
