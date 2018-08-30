# -*- coding: utf-8 -*-
# 多进程版本
import sys, os
import datetime, time
import traceback
import pycurl
import Cookie
import json
from urllib import quote
import random
from multiprocessing import Process, Queue, Lock
import requests

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import db
import loghelper, util, name_helper

#logger
loghelper.init_logger("tianyancha_gongshang3")
logger = loghelper.get_logger("tianyancha_gongshang3")

concurrency = 5
SOURCE = 13090  #天眼查
TYPE = 36008    #工商
worker_no = -1

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


def get_proxy(lock, worker):
    while True:
        lock.acquire()
        wait_time = random.randrange(0, 1000)
        time.sleep(wait_time / 1000.0)
        try:
            mongo = db.connect_mongo()
            proxy = mongo.raw.proxy_tyc.find_one({
                    "$or":[{'status':0}, {'status':{'$exists':False}}]
            }, sort=[("fail", 1)])
            if proxy is not None:
                print("worker: %s, %s"% (worker,proxy))
                mongo.raw.proxy_tyc.update({"_id":proxy["_id"]},{"$set":{"status":1}})
            mongo.close()
        finally:
            lock.release()

        if proxy is None:
            wait_time = random.randrange(10000, 11000)
            time.sleep(wait_time / 1000.0)
            continue
        return proxy


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
            if fail_num > 5:
                mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"TYCID": None}})
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

def request(proxy, url, headers=None):
    print("request: %s" % url)
    if headers is None:
        headers = {}
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.4.8 (KHTML, like Gecko)"
    headers["Accept-Language"] = "zh-CN,zh;q=0.5,en;q=0.3"
    headers["Accept-Encoding"] = ""

    stype = "socks5"
    if proxy["type"].lower() == "socks4":
        stype = "socks4"
    proxy = "%s://%s:%s" % (stype, proxy["ip"], proxy["port"])
    # print(proxy)
    proxies = {
        'http': proxy,
        'https': proxy
    }

    response = None
    retries = 0
    while True:
        try:
            response = requests.get(url, headers=headers, proxies=proxies)
        except Exception as e:
            if retries < 3:
                retries += 1
                time.sleep(1)
                continue
            else:
                traceback.print_exc()
                print("worker: %s, fetch error! proxy: %s" % (worker_no, proxy))
        break

    if response is not None:
        if response.status_code != 200:
            print("worker: %s, Error: %s, %s" % (worker_no, response.status_code, url))
            print("worker: %s, proxy: %s" % (worker_no, proxy))
        else:
            return response

    return None


def cookie_to_dict(cookie):
    """Convert a string cookie into a dict"""
    cookie_dict = dict()
    C = Cookie.SimpleCookie(cookie)
    for morsel in C.values():
        cookie_dict[morsel.key] = morsel.value
    return cookie_dict


def step1(proxy, company_name):
    # 搜索公司页，获得TYCID
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com",
               }
    url = "http://www.tianyancha.com/search?key=%s&checkFrom=searchBox" % quote(company_name.encode("utf8"))
    response = request(proxy, url, headers=headers)
    if response is None:
        return False

    try:
        # html = unicode(response.text, encoding="utf-8", errors='replace')
        html = response.text
        # logger.info(html)
        # logger.info(response.headers.get_list("Set-Cookie"))
        TYCID = response.cookies.get("TYCID")
    except:
        traceback.print_exc()

    if TYCID is not None:
        print("worker: %s, step1: TYCID=%s" % (worker_no, TYCID))
        mongo = db.connect_mongo()
        proxy["TYCID"] = TYCID
        mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"TYCID": TYCID}})
        mongo.close()
        return True

    print("worker: %s, step1: can't get TYCID" % worker_no)
    return False


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
    response = request(proxy, url, headers=headers)
    if response is None:
        return False

    try:
        # html = unicode(response.text, encoding="utf-8", errors='replace')
        html = response.text
    except:
        traceback.print_exc()

    # logger.info(html)
    token, _utm = process_tongji(html, company_name)
    if token is None or _utm is None:
        print("worker: %s, %s" % (worker_no, html))
        print("worker: %s, step2: can't get token,_utm" % worker_no)
        return False

    proxy["token"] = token
    proxy["utm"] = _utm
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"token": token, "utm": _utm}})
    mongo.close()
    print("worker: %s, step2: TYCID=%s, token=%s, _utm=%s" % (worker_no, TYCID, token, _utm))
    return True


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


def step3(proxy, company_name):
    # search
    url = "http://www.tianyancha.com/v2/search/%s.json?" % quote(company_name.encode("utf8"))
    headers = {"accept": "application/json",
               "Tyc-From": "normal",
               "CheckError": "check",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               "Referer": "http://www.tianyancha.com/search/%s?checkFrom=searchBox" % company_name}
    response = request(proxy, url, headers=headers)
    if response is None:
        return -1

    try:
        # html = unicode(response.text, encoding="utf-8", errors='replace')
        html = response.text
    except:
        traceback.print_exc()

    # logger.info(html)
    status, tyc_company_id = process_search(html, company_name)
    if status == -1:
        return -1
    elif status == 0 or status == -2:
        print("worker: %s, %s Not Found!" % (worker_no, company_name))
        return 0

    print("worker: %s, step3: tyc_company_id=%s" % (worker_no, tyc_company_id))
    return tyc_company_id


def step4(proxy, company_name, tyc_company_id):
    referer = "http://www.tianyancha.com/search/%s?checkFrom=searchBox" % quote(company_name.encode("utf8"))
    url = "http://www.tianyancha.com/wxApi/getJsSdkConfig.json?url=%s" % quote(referer.encode("utf8"), '')
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com/company/%s" % tyc_company_id,
               "Tyc-From": "normal",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               }
    response = request(proxy, url, headers=headers)
    if response is None:
        return False

    return True


def step5(proxy, company_name, tyc_company_id):
    url = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (tyc_company_id, int(time.time() * 1000))
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com/company/%s" % tyc_company_id,
               "Tyc-From": "normal",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               }
    response = request(proxy, url, headers=headers)
    if response is None:
        return False

    try:
        # html = unicode(response.text,encoding="utf-8",errors='replace')
        html = response.text
    except:
        traceback.print_exc()

    #logger.info(html)
    token, _utm = process_tongji(html, "%s" % tyc_company_id)
    if token is None or _utm is None:
        return False

    proxy["token"] = token
    proxy["utm"] = _utm
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update({"_id": proxy["_id"]}, {"$set": {"token": token, "utm": _utm}})
    mongo.close()
    print("worker: %s, step5: TYCID=%s, token=%s, _utm=%s" % (worker_no, proxy["TYCID"], token, _utm))

    return True


def step6(proxy, company_name, tyc_company_id):
    url = "http://www.tianyancha.com/company/%s.json" % tyc_company_id
    headers = {"accept":"application/json",
               "Tyc-From":"normal",
               "CheckError":"check",
               "Cookie":"TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               "Referer":"http://www.tianyancha.com/company/%s" % tyc_company_id}
    response = request(proxy, url, headers=headers)
    if response is None:
        return False

    try:
        # html = unicode(response.text, encoding="utf-8", errors='replace')
        html = response.text
        print("worker: %s, step6: " % worker_no)
        print("worker: %s, %s" % (worker_no, html))
    except:
        traceback.print_exc()

    try:
        content = json.loads(html)
        #logger.info(content)
    except:
        return False

    url = "http://www.tianyancha.com/company/%s" % tyc_company_id
    save(url, company_name, tyc_company_id, content, True)
    print("worker: %s, step6: success" % worker_no)

    return True

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


def step7(proxy, company_name, tyc_company_id):
    referer = "http://www.tianyancha.com/company/%s" % tyc_company_id
    url = "http://www.tianyancha.com/wxApi/getJsSdkConfig.json?url=%s" % quote(referer.encode("utf8"), '')
    headers = {"accept": "application/json",
               "Referer": "http://www.tianyancha.com/company/%s" % tyc_company_id,
               "Tyc-From": "normal",
               "Cookie": "TYCID=%s, token=%s, _utm=%s, tnet=%s" % (proxy["TYCID"], proxy["token"], proxy["utm"], proxy["ip"]),
               }
    response = request(proxy, url, headers=headers)
    if response is None:
        return False

    return True


def process(company, proxy):
    company_name = name_helper.company_name_normalize(company["name"])
    company_name = company_name.replace("'","")

    wait_time = random.randrange(3, 10)
    time.sleep(wait_time)

    TYCID = proxy.get("TYCID")
    if TYCID is None:
        # step1
        # 搜索公司页，获得TYCID
        flag = step1(proxy, company_name)
        if flag is False:
            return False

    # step2
    # 已有TYCID, 访问/tongji/companyname.json
    flag = step2(proxy, company_name)
    if flag is False:
        return False

    # step3
    # 搜索获得tyc_company_id
    tyc_company_id = step3(proxy, company_name)
    if tyc_company_id == -1:
        return False
    elif tyc_company_id == 0:
        # 搜不到
        update_check_time(company, exist=False)
        return True

    wait_time = random.randrange(1, 3)
    time.sleep(wait_time)

    # step4
    flag = step4(proxy, company_name, tyc_company_id)
    if flag is False:
        return False

    # step5
    flag = step5(proxy, company_name, tyc_company_id)
    if flag is False:
        return False

    # step6
    flag = step6(proxy, company_name, tyc_company_id)
    if flag is False:
        return False
    update_check_time(company, exist=True)

    # step7
    step7(proxy, company_name, tyc_company_id)

    time.sleep(1)
    return True


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


def worker(q, lock, index):
    global worker_no
    worker_no = index
    proxy = get_proxy(lock, index)
    while True:
        company = q.get()
        try:
            if "/" in company["name"]:
                update_check_time(company, False)
                continue

            print('worker: %s, fetching: %s' % (worker_no, company["name"]))
            while True:
                wait_time = random.randrange(3, 10)
                time.sleep(wait_time)
                flag = process(company, proxy)
                if flag:
                    proxy_success(proxy)
                    break
                else:
                    proxy_fail(proxy)
                    mongo = db.connect_mongo()
                    result = mongo.raw.proxy_tyc.find_one({"_id": proxy["_id"]})
                    mongo.close()
                    if result is None:
                        proxy = get_proxy(lock, index)
        finally:
            # q.task_done()
            pass


def main(q):
    while True:
        if q.empty():
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
                print("***********Batch fetch begin****************")
                for c in company_aliases:
                    q.put(c)
                for c in cs:
                    q.put(c)
                print("***********Batch fetch end****************")
            else:
                print("***********No task****************")
                time.sleep(60)
        else:
            # print "q is not empty"
            time.sleep(10)


if __name__ == '__main__':
    print("Start.")
    mongo = db.connect_mongo()
    mongo.raw.proxy_tyc.update_many({}, {"$set": {"status": 0}})
    mongo.close()

    lock = Lock()
    q = Queue(1000)
    for index in range(concurrency):
        w = Process(target=worker, args=(q, lock, index))
        w.start()

    main(q)
