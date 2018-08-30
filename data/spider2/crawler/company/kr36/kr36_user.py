# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random, time
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib
import pymongo
import socket
import ssl
import gevent
import cookielib, Cookie
import requests

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

#logger
loghelper.init_logger("crawler_36kr_user", stream=True)
logger = loghelper.get_logger("crawler_36kr_user")


class RedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        pass


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=40,max_crawl=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout,max_crawl=max_crawl)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "操作成功！" or j["msg"].strip() == "公司不存在":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return True
            else:
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
        return False


    def init_http_session(self,url,redirect=True, userinfo=None):
        if self.opener is not None:
            self.opener.close()

        handlers = []
        if self.use_proxy:
            if url.lower().startswith("https"):
                http_type = "https"
            else:
                http_type = "http"

            # if self.http_proxy is None or http_type == "http":
            #     self.http_proxy = self.get_proxy("http")
            #     logger.info("Proxy: http://%s:%s" % (self.http_proxy["ip"], self.http_proxy["port"]))

            if self.https_proxy is None or http_type == "https":
                self.https_proxy = {"ip":userinfo["ip"],"port":userinfo["port"]}
                logger.info("Proxy: https://%s:%s" % (self.https_proxy["ip"], self.https_proxy["port"]))

            # handlers.append(urllib2.ProxyHandler({"http":"http://%s:%s" % (self.http_proxy["ip"], self.http_proxy["port"])}))
            handlers.append(urllib2.ProxyHandler({"https":"http://%s:%s" % (self.https_proxy["ip"], self.https_proxy["port"])}))

        context = ssl._create_unverified_context()
        handlers.append(urllib2.HTTPSHandler(0, context))

        self.cookiejar = cookielib.CookieJar()
        handlers.append(urllib2.HTTPCookieProcessor(self.cookiejar))
        if redirect is False:
            handlers.append(RedirectHandler)

        self.opener = urllib2.build_opener(*handlers)

    def login(self, url, redirect=True):
        while True:
            time.sleep(random.randint(5, 10))
            login_user = get_user()
            logger.info(login_user)
            logger.info("want: %s", url)

            if url.find("fund-express") >= 0:
                self.init_http_session(url, redirect,login_user)
                logger.info("here not to login")
                update_user(login_user)
                break
            else:
                logger.info("here go to login")
                self.init_http_session(url, redirect,login_user)
                data = {
                    "type": "login",
                    "bind": False,
                    "needCaptcha": False,
                    "username": login_user["mail"],
                    "password": login_user["password"],
                    "ok_url": "/"

                }
                data = urllib.urlencode(data)
                headers = {
                    "Referer": "https://passport.36kr.com"
                }
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
                headers['User-Agent'] = user_agent

                try:
                    request = urllib2.Request("https://passport.36kr.com/passport/sign_in", data, headers)
                    r = self.opener.open(request, timeout=30)
                    page = r.read()
                    logger.info(page)
                except Exception, e:
                    logger.info("wrong 1")
                    logger.info(e)
                    update_user_wrong(login_user)
                    continue

                if r.getcode() != 200:
                    logger.info("wrong 2")
                    update_user_wrong(login_user)
                    continue

                if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
                    logger.info("wrong 3")
                    update_user_wrong(login_user)
                    continue

                try:
                    request = urllib2.Request("https://uc.36kr.com/api/user/identity")
                    r = self.opener.open(request, timeout=30)
                    page = r.read()
                    logger.info("identity")
                    logger.info(page)
                except:
                    logger.info("wrong here")
                    update_user_wrong(login_user)
                    continue

                if r.getcode() == 200:
                    try:
                        result = json.loads(page)
                    except:
                        logger.info("wrong 4")
                        logger.info(page)
                        update_user_wrong(login_user)
                        continue
                    # logger.info(result)
                    if result["code"] == 0 and result["msg"] == "操作成功！":
                        update_user(login_user)
                        break
                else:
                    logger.info("wrong 5, %s", r.getcode())

def update_user(userinfo):
    mongo = db.connect_mongo()
    collection = mongo.xiniudata.kr36user
    collection.update_one({"mail": userinfo["mail"]}, {'$set': {"checktime": datetime.datetime.now()}})
    mongo.close()

def update_user_wrong(userinfo):
    mongo = db.connect_mongo()
    collection = mongo.xiniudata.kr36user
    collection.update_one({"mail": userinfo["mail"]}, {'$set': {"checktime": datetime.datetime.now(),"ip":None}})
    mongo.close()

def get_user():
    nitem = None
    mongo = db.connect_mongo()
    collection = mongo.xiniudata.kr36user
    item = collection.find_one({"checktime": None})
    if item is None:
        item = list(collection.find({}).sort("checktime", pymongo.ASCENDING).limit(1))[0]
    if item is not None:
        if item["ip"] is None:
            while True:
                url = 'https://rong.36kr.com/n/api/index/fund-express?page=1&pageSize=10'
                proxy = {'type': "https", 'anonymity': 'high'}
                proxy_ip = proxy_pool.get_single_proxy(proxy)
                ip, port = proxy_ip['ip'], proxy_ip['port']
                ip_port = ip + ':' + str(port)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
                }
                logger.info("crawler: %s, %s, %s", url, item["mail"], ip_port)
                timeout = 30
                proxies = {
                    'https': ip_port
                }

                try:
                    r = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
                    j = json.loads(r.text)

                    if j["msg"].strip() == "操作成功！" or j["msg"].strip() == "公司不存在":
                        logger.info("code=%d, %s" % (j["code"], j["msg"]))
                        collection.update_one({"_id":item["_id"]},{'$set':{"ip":proxy_ip['ip'],"port":proxy_ip['port']}})
                        break

                    else:
                        logger.info("code=%d, %s" % (j["code"], j["msg"]))
                        continue
                except:
                    continue
            nitem = collection.find_one({"_id":item["_id"]})
        else:
            nitem = item

    else:
        pass
    logger.info(nitem)
    mongo.close()
    return nitem



def process(mail,passw):
    mongo = db.connect_mongo()
    collection = mongo.xiniudata.kr36user
    item = collection.find_one({"mail": mail})

    if item is None:
        citem = {
            "mail": mail,
            "password": passw,
            "checktime": None,
            "ip": None,
            "port": None
        }
        collection.insert(citem)
    else:
        collection.update_one({"_id": item["_id"]}, {'$set': {"password": passw}})

    mongo.close()

CURRENT_PAGE=1
URLS = []

columns = [
    {"column": "fund-e", "max": 1},
    {"column": None, "max": 1},]

def process_o(content, flag, column):

    j = json.loads(content)
    # logger.info(content)
    if column["column"] is not None and column["column"] == "fund-e":
        companies = j["data"]
    else:
        companies = j["data"]["pageData"]["data"]

    cnt = 0
    if len(companies) == 0:
        return cnt

    for a in companies:
        try:

            id = a["id"]
            name = a["name"]
            logger.info("company: %s|%s", id, name)

    #         # check mongo data if link is existed
    #         mongo = db.connect_mongo()
    #         collection_news = mongo.raw.projectdata
    #         item = collection_news.find_one({"source": SOURCE, "type": TYPE, "key_int": int(id)})
    #         mongo.close()
    #         # if item is None or ((datetime.datetime.now() - item["date"]).days>= 1 and (datetime.datetime.now() - item["date"]).days <2):
    #         if item is None:
    #             URLS.append(a)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    # return len(URLS)

def run(flag, column, listcrawler, companycrawler, concurrent_num):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE

        if flag == "all":
            if key > column["max"]:
                return
        else:
            if cnt == 0 or key > column["max"]:
                return

        CURRENT_PAGE += 1
        if column["column"] is None:
            url = 'https://rong.36kr.com/n/api/column/0/company?p=%s' % (key)
        elif column["column"] == "fund-e":
            url = 'https://rong.36kr.com/n/api/index/fund-express?page=%s&pageSize=10' % (key)
        else:
            url = 'https://rong.36kr.com/n/api/column/0/company?industry=%s&p=%s' % (column["column"],key)
        while True:
            result = listcrawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    cnt = process_o(result['content'], flag, column)
                    # if cnt > 0:
                    #     logger.info("%s has %s fresh company", url, cnt)
                    #     logger.info(URLS)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break

def test():
    global CURRENT_PAGE
    listcrawler = ListCrawler()
    companycrawler = ListCrawler()

    # download_crawler = None
    for column in columns:

        CURRENT_PAGE = 1
        run("INCR", column, listcrawler, companycrawler, 1)


if __name__ == "__main__":
    # process("leilei_xu1989@126.com","qwerty")
    while True:
        test()
        time.sleep(random.randint(1,5))

    # get_user()