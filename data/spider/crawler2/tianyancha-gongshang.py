# -*- coding: utf-8 -*-
import os, sys
import time, datetime
import json
import requesocks as requests
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../support'))
import loghelper, config
import util
import proxy_pool
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

#mysql
conn = None

SOURCE = 13090  #天眼查
TYPE = 36008    #工商

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

proxies_priority = 0
proxies = []
proxies_num = 0
proxies_current = 0

proxies1 = [
    #{"ip:port":"97.87.45.251:54032","http_type":"Socks5"},
    #{"ip:port":"101.0.44.229:54032","http_type":"Socks5"},
    #{"ip:port":"103.17.51.144:54032","http_type":"Socks5"},
    #{"ip:port":"103.17.51.85:54032","http_type":"Socks5"},
    #{"ip:port":"103.248.232.232:54032","http_type":"Socks5"},
    #{"ip:port":"103.255.235.131:54032","http_type":"Socks5"},
    #{"ip:port":"103.47.14.35:54032","http_type":"Socks5"},
    #{"ip:port":"103.51.28.59:54032","http_type":"Socks5"},
    #{"ip:port":"109.87.146.178:54032","http_type":"Socks5"},
    #{"ip:port":"109.87.146.249:54032","http_type":"Socks5"},
    {"ip:port":"59.58.162.141:2699","http_type":"Socks5"},
]

def fetch_proxies2():
    global proxies, proxies_num, proxies_current
    proxies = proxies1
    proxies_current = 0
    proxies_num = len(proxies)

def fetch_proxies1():
    global proxies, proxies_num, proxies_current, proxies_priority
    proxies_priority = 1
    url = "http://proxy.mimvp.com/api/fetch.php?orderid=860150908143212810&num=100&country_group=1&http_type=4,5&result_fields=1,2&result_format=json"
    #url = "http://proxy.mimvp.com/api/fetch.php?orderid=860150908143212810&num=10&http_type=1&result_fields=1,2&result_format=json"
    while True:
        http_session = requests.Session()
        r = http_get(http_session, url)
        if r is None or r.status_code != 200:
            continue
        try:
            data = json.loads(r.text)
        except:
            logger.info(r.status_code)
            logger.info(r.text)

        proxies = data["result"]
        proxies_num = len(proxies)
        proxies_current = 0
        if proxies_num == 0:
            time.sleep(10)
            continue
        break

def fetch_proxies():
    global proxies, proxies_num, proxies_current
    url = "http://www.socks-proxy.net"
    while True:
        proxies_temp = []
        http_session = requests.Session()
        r = http_get(http_session, url)
        if r is None or r.status_code != 200:
            continue
        try:
            d = pq(r.text)
            trs = d("tbody> tr")
            for tr in trs:
                l = pq(tr)
                tds = l("td")
                proxy = {"ip:port":"%s:%s" % (tds.eq(0).text(),tds.eq(1).text()), "http_type":tds.eq(4).text()}
                #logger.info(proxy)
                proxies_temp.append(proxy)
        except:
            logger.info(r.status_code)
            logger.info(r.text)

        proxies = proxies_temp
        proxies_num = len(proxies)
        proxies_current = 0
        if proxies_num == 0:
            time.sleep(10)
            continue
        break


def fetch_proxies3():
    logger.info("fetch_proxies3")
    global proxies, proxies_num, proxies_current, proxies_priority
    proxies_priority = 0

    proxies_temp = []
    while True:
        conn = db.connect_torndb_crawler()
        sql = 'select * from proxy_tyc'
        results = conn.query(sql)
        for result in results:
            proxy = {"ip:port":"%s:%s" % (result["ip"],result["port"]), "http_type":result["type"]}
            logger.info(proxy)
            proxies_temp.append(proxy)
        conn.close()
        proxies = proxies_temp
        proxies_num = len(proxies)
        proxies_current = 0
        logger.info("proxies_num=%d, proxies_current=%d" % (proxies_num, proxies_current))
        if proxies_num == 0:
            #time.sleep(60)
            fetch_proxies1()
            break
        break


def delete_last_proxy_from_db():
    global proxies, proxies_num, proxies_current
    if proxies_current-1 >=0:
        logger.info("delete")
        proxy_ip = proxies[proxies_current-1]
        logger.info(proxy_ip)
        ip_port = proxy_ip["ip:port"].split(":")
        conn = db.connect_torndb_crawler()
        conn.execute("delete from proxy_tyc where ip=%s and port=%s and type=%s", ip_port[0], int(ip_port[1]), proxy_ip["http_type"])
        conn.close()

def get_http_session():
    global proxies, proxies_num, proxies_current, proxies_priority
    flag = 0
    if proxies_priority != 0:
        conn = db.connect_torndb_crawler()
        result = conn.get("select count(*) cnt from proxy_tyc")
        conn.close()
        if result["cnt"] > 0:
            fetch_proxies3()
            flag = 1

    if flag == 0:
        if proxies_num == 0 or proxies_current >= proxies_num:
            if proxies_current == proxies_num:
                delete_last_proxy_from_db()
            fetch_proxies3()

        if proxies_current > 0:
            delete_last_proxy_from_db()

    proxy_ip = proxies[proxies_current]
    proxies_current += 1
    logger.info("Proxy IP: %s" % proxy_ip)

    http_session = requests.Session()
    if proxy_ip["http_type"] == "Socks4":
        http_type = "socks4"
    elif proxy_ip["http_type"] == "HTTP":
        http_type = "http"
    else:
        http_type = "socks5"
    http_session.proxies={"http":"%s://%s" % (http_type, proxy_ip["ip:port"])}
    #http_session.proxies={"http":"socks5://222.187.210.218:1080"}
    return http_session


def http_get(http_session, url, max_retry=3, headers=None, cookies=None):
    retry_times = 0
    timeout = 20
    if headers is None:
        headers={"Accept":"*/*"}
    headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101 Firefox/45.0"

    while retry_times < max_retry:
        logger.info("No.%d, %s" % (retry_times+1,url))
        try:
            r = http_session.get(url, timeout=timeout, headers=headers, cookies=cookies)
            if r.status_code !=200:
                logger.info("status_code=%s" % r.status_code)
                retry_times += 1
                continue
            # use page encoding
            #r.encoding = r.apparent_encoding
            r.encoding = 'utf-8'
        except Exception,ex:
            #logger.exception(ex)
            retry_times += 1
            continue

        return r


def process_tongji(r, key):
        try:
            data = json.loads(r.text)
            v = data["data"]["v"]
        except Exception,ex:
            #logger.exception(ex)
            logger.info(r.status_code)
            logger.info(r.text)
            return None, None

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


def process_search(r, key):
        try:
            data = json.loads(r.text)
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

if __name__ == "__main__":
    logger.info("Start...")

    conn = db.connect_torndb()
    cs = conn.query("select * from company_alias where type=12010 order by id desc limit 1000")
    conn.close()

    http_session = get_http_session()

    for c in cs:
        key = c["name"].strip().replace("(", u"（").replace(")", u"）").\
                replace("?", "").replace(" ", "").replace("'","").\
                replace(".","").replace(";","")
        if key.find("/") != -1:
            continue
        if collection.find_one({"source":SOURCE, "type":TYPE, "key":key}) is not None:
            continue

        retry_num = 0
        while True:
            retry_num += 1
            if retry_num > 1:
                http_session = get_http_session()
                retry_num = 0

            '''
            if retry_num >= 100:
                logger.info("Exit! Try too many times!")
                exit(0)
            '''
            #
            url1 = "http://www.tianyancha.com/search/%s" % key

            r = http_get(http_session, url1)
            if r is None or r.status_code != 200:
                #logger.info("status_code=%s" % r.status_code)
                continue
            #logger.info(r.text)
            #logger.info(r.cookies)
            TID = r.cookies.get("TID")
            if TID is None:
                continue
            logger.info("TID=%s" % TID)

            #
            url2 = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (key, int(time.time()*1000))
            headers = {"accept":"application/json"}
            r = http_get(http_session, url2, headers=headers)
            if r is None or r.status_code != 200:
                continue
            token, _utm = process_tongji(r, key)
            if token is None or _utm is None:
                continue

            #
            logger.info("TID=%s; token=%s; _utm=%s" % (TID,token,_utm))
            url3 = "http://www.tianyancha.com/search/%s.json" % key
            cookies = {"TID":TID, "token":token, "_utm":_utm}
            headers = {"accept":"application/json", "Tyc-From":"normal"}


            loop = 0
            retry1 = 0
            while True:
                r = http_get(http_session, url3, headers=headers, cookies=cookies)
                if r is None or r.status_code != 200:
                    retry1 += 1
                    if retry1 >=1:
                        status = -1
                        break
                    continue
                status, tyc_company_id = process_search(r, key)
                if status == -2:
                    headers={"loop":"%s" % loop}
                    loop += 1
                    #continue
                break

            if status == -1:
                continue
            elif status == 0 or status == -2:
                logger.info("%s Not Found!" % key)
                save(None, key, None, None, False)
                break

            #
            url4_0 = "http://www.tianyancha.com/company/%s" % tyc_company_id
            #r = http_get(http_session, url4_0)
            #if r is None or r.status_code != 200:
            #    continue
            #logger.info(r.text)

            #
            url4 = "http://www.tianyancha.com/tongji/%s.json?random=%d" % (tyc_company_id, int(time.time()*1000))
            headers = {"accept":"application/json"}
            r = http_get(http_session, url4, headers=headers)
            if r is None or r.status_code != 200:
                continue
            token, _utm = process_tongji(r, "%s" % tyc_company_id)
            if token is None or _utm is None:
                continue

            #
            logger.info("TID=%s; token=%s; _utm=%s" % (TID,token,_utm))
            url5 = "http://www.tianyancha.com/company/%s.json" % tyc_company_id
            cookies = {"TID":TID, "token":token, "_utm":_utm}
            headers = {"accept":"application/json", "Tyc-From":"normal", "Referer":url4_0}
            r = http_get(http_session, url5, headers=headers, cookies=cookies)
            if r is None or r.status_code != 200:
                continue
            try:
                content = json.loads(r.text)
            except:
                continue

            save(url4_0, key, tyc_company_id, content, True)

            break
        #break


    logger.info("End.")

