# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib
import time
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from urllib import quote
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

#logger
loghelper.init_logger("crawler_36kr_company2_member", stream=True)
logger = loghelper.get_logger("crawler_36kr_company2_member")

TYPE = 36005
SOURCE =13022
# URLS = []
KEYCS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]

# companycrawler = kr36Crawler()

login_users = [
    {"name": "yunzhisheng@mailinator.com", "pwd": "123456"},
    {"name": "yidaoyongche@mailinator.com", "pwd": "123456"},
    {"name": "fFineEx@mailinator.com", "pwd": "123456"},
    {"name": "jgpzcl@mailinator.com", "pwd": "123456"},
    {"name": "guangzhouyouaiwangluo@mailinator.com", "pwd": "123456"},
    {"name": "beijinglangdongkeji@mailinator.com", "pwd": "123456"},
    {"name": "gh-jt@mailinator.com", "pwd": "123456"},
    {"name": "senzheruo@mailinator.com", "pwd": "123456"},
    {"name": "guangxihuiyunxinxi@mailinator.com", "pwd": "123456"},
    {"name": "shanghaihongyi@mailinator.com", "pwd": "123456"},
    {"name": "guiyuan@mailinator.com", "pwd": "123456"},
    {"name": "wozai@mailinator.com", "pwd": "123456"},
    {"name": "zhuangzhuang@mailinator.com", "pwd": "123456"},
    {"name": "chengcheng@mailinator.com", "pwd": "123456"},
    {"name": "haige@mailinator.com", "pwd": "123456"},
    {"name": "dadiao@mailinator.com", "pwd": "123456"},
    {"name": "pangzi@mailinator.com", "pwd": "123456"},
    {"name": "chaobi@mailinator.com", "pwd": "123456"},
    {"name": "longmei@mailinator.com", "pwd": "123456"},
    {"name": "qiangge@mailinator.com", "pwd": "123456"},
]

def get_url(key):
    millis = int(round(time.time() * 1000))
    url = {}
    url["member"] = "https://rong.36kr.com/n/api/company/%s/member?asEncryptedTs=0.2865982147907245&asTs=%s" % (key,millis)
    return url


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=33):
        BaseCrawler.BaseCrawler.__init__(self,timeout=timeout)

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

    def login(self, url, redirect=True):
        while True:
            self.init_http_session(url)

            idx = random.randint(0, len(login_users) - 1)
            login_user = login_users[idx]
            logger.info(login_user)
            logger.info("want: %s", url)

            data = {
                "type": "login",
                "bind": False,
                "needCaptcha": False,
                "username": login_user["name"],
                "password": login_user["pwd"],
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
                continue

            if r.getcode() != 200:
                logger.info("wrong 2")
                continue

            if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
                logger.info("wrong 3")
                continue

            try:
                request = urllib2.Request("https://uc.36kr.com/api/user/identity")
                r = self.opener.open(request, timeout=30)
                page = r.read()
                logger.info("identity")
                logger.info(page)
            except:
                logger.info("wrong here")
                continue

            if r.getcode() == 200:
                try:
                    result = json.loads(page)
                except:
                    logger.info("wrong 4")
                    logger.info(page)

                    continue
                # logger.info(result)
                if result["code"] == 0 and result["msg"] == "操作成功！":
                    break
            else:
                logger.info("wrong 5, %s", r.getcode())


class kr36Crawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=33,max_crawl=20):
        BaseCrawler.BaseCrawler.__init__(self,timeout=timeout,max_crawl=max_crawl)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "操作成功！"  or j["msg"].strip() == "公司不存在":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return True
            else:
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
        return False

    def login(self, url, redirect=True):
        while True:
            self.init_http_session(url)

            idx = random.randint(0, len(login_users) - 1)
            login_user = login_users[idx]
            logger.info(login_user)
            logger.info("want: %s", url)

            data = {
                "type": "login",
                "bind": False,
                "needCaptcha": False,
                "username": login_user["name"],
                "password": login_user["pwd"],
                "ok_url": "/"

            }
            data = urllib.urlencode(data)
            headers = {
                "Referer": "https://passport.36kr.com"
            }
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
            headers['User-Agent'] = user_agent

            try:
                request= urllib2.Request("https://passport.36kr.com/passport/sign_in", data, headers)
                r = self.opener.open(request, timeout=30)
                page=r.read()
                logger.info(page)
            except Exception,e:
                logger.info("wrong 1")
                logger.info(e)
                continue

            if r.getcode() != 200:
                logger.info("wrong 2")
                continue

            if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
                logger.info("wrong 3")
                continue

            try:
                request = urllib2.Request("https://uc.36kr.com/api/user/identity")
                r = self.opener.open(request, timeout=30)
                page = r.read()
                logger.info("identity")
                logger.info(page)
            except:
                logger.info("wrong here")
                continue

            if r.getcode() == 200:
                try:
                    result = json.loads(page)
                except:
                    logger.info("wrong 4")
                    logger.info(page)

                    continue
                #logger.info(result)
                if result["code"] == 0 and result["msg"] == "操作成功！":
                    break
            else:
                logger.info("wrong 5, %s",r.getcode())

def has_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False

        if j["code"] == 0:
            return True
        else:
            logger.info("code=%d, %s" % (j["code"], j["msg"]))
    else:
        logger.info("Fail to get content")

    return False


def run_news(column, crawler, URL):

    logger.info(URL)
    crawler_news(column, crawler, URL["id"], URL["name"])

def crawler_news(column, crawler, id, name):

    company = {}
    logger.info("start crawler %s|%s", id, name)
    url_map = get_url(id)
    for k in url_map.keys():
        if k != "key":
            result = crawler.crawl(url_map[k])
            while True:
                if result['get'] == 'success':
                    break
                elif result["content"] is not None and result["content"].find("后台出错，请联系管理员！") > 0:
                    break
                else:
                    result = crawler.crawl(url_map[k])
            content_more = result['content']
            if has_content(content_more):
                company[k] = json.loads(content_more)
                logger.info(company[k])
                # time.sleep(random.randint(3,8))
        time.sleep(3)
    save(SOURCE, TYPE, url_map["member"], id, company)


def save(SOURCE, TYPE, url, key, content):
    logger.info("Saving: %s", url)
    try:
        key_int = int(key)
    except:
        key_int = None

    collection_content = {
        "date": datetime.datetime.now(),
        "source": SOURCE,
        "type": TYPE,
        "url": url,
        "key": int(key),
        "key_int": key_int,
        "content": content
    }
    newflag = True
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": int(key)})
    if item is not None:
        if item["content"] != content:
            collection.delete_one({"source": SOURCE, "type": TYPE, "key": int(key)})
            logger.info("old data changed for company: %s", key)
        else:
            logger.info("old data not changed for company: %s", key)
            newflag = False
    if newflag is True: collection.insert_one(collection_content)
    mongo.close()
    logger.info("Saved: %s", url)


def ss_run(listcrawler,companycrawler):

    while True:

        if len(KEYCS) == 0:
            return
        KEYC = KEYCS.pop(0)
        keyword = KEYC["keyword"]
        sourceId = KEYC["sourceId"]
        logger.info("*******here kr36 search %s|%s remain: %s", keyword, sourceId, len(KEYCS))

        if sourceId is None:
            pass
        else:
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "type": TYPE, "key_int": int(sourceId)})
            mongo.close()
            if item is None or ((datetime.datetime.now() - item["date"]).days >= 5):
                crawler_news({}, companycrawler, str(sourceId), "new")
            else:
                logger.info("we have data")
        # break

def start_run(kcolumns):

    for k in kcolumns:
        KEYCS.append(k)
    if len(KEYCS) > 0:
        threads = [gevent.spawn(ss_run, ListCrawler(), kr36Crawler()) for i in xrange(2)]
        gevent.joinall(threads)


    # global CURRENT_PAGE
    # while True:
    #     logger.info("%s company %s start...", SOURCE, flag)
    #     listcrawler = ListCrawler()
    #     companycrawler = kr36Crawler()
    #
    #     # download_crawler = None
    #     for column in columns:
    #         CURRENT_PAGE = 1
    #         run(flag, column, listcrawler, companycrawler, concurrent_num)
    #
    #     if flag == "incr":
    #         gevent.sleep(60*60)        #30 minutes
    #     else:
    #         return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":

    start_run([{"keyword":"teambition", "sourceId":None}], ListCrawler(), kr36Crawler())