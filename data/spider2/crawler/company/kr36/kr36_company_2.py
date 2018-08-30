# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random, time
from lxml import html
from pyquery import PyQuery as pq
import urllib2
import urllib
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

import kr36_user
#logger
loghelper.init_logger("crawler_36kr_company2", stream=True)
logger = loghelper.get_logger("crawler_36kr_company2")

TYPE = 36001
SOURCE =13022
URLS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]
columns = [
    {"column": "fund-e", "max": 3},
    # {"column": "FARMING", "max": 3},{"column": "E_COMMERCE", "max": 3},{"column": "SOCIAL_NETWORK", "max": 3},
    # {"column": "INTELLIGENT_HARDWARE", "max": 3},{"column": "MEDIA", "max": 3},{"column": "SOFTWARE", "max": 3},
    # {"column": "CONSUMER_LIFESTYLE", "max": 3},{"column": "FINANCE", "max": 3},{"column": "MEDICAL_HEALTH", "max": 3},
    # {"column": "SERVICE_INDUSTRIES", "max": 3},{"column": "TRAVEL_OUTDOORS", "max": 3},{"column": "PROPERTY_AND_HOME_FURNISHINGS", "max": 3},
    # {"column": "EDUCATION_TRAINING", "max": 3}, {"column": "AUTO", "max": 3}, {"column": "LOGISTICS", "max": 3},
    # {"column": "AI", "max": 3}, {"column": "UAV", "max": 3}, {"column": "ROBOT", "max": 3},
    # {"column": "VR_AR", "max": 3}, {"column": "SPORTS", "max": 3}, {"column": "SHARE_BUSINESS", "max": 3},
    # {"column": "CHU_HAI", "max": 3}, {"column": "CONSUME", "max": 3},
    {"column": None, "max": 10},
]

login_users = [
    {"name":"minnie@mailinator.com", "pwd":"minnie"},
    {"name":"anna@mailinator.com","pwd":"123456"},
    {"name":"dorothy@mailinator.com","pwd":"123456"},
    {"name":"edna@mailinator.com","pwd":"123456"},
    {"name":"grace@mailinator.com","pwd":"123456"},
    {"name":"Arthur1236@mailinator.com","pwd":"123456"},
    {"name":"Arthur1238@mailinator.com","pwd":"123456"},
    {"name":"Arthur1242@mailinator.com","pwd":"123456"},
    {"name":"Arthur1251@mailinator.com","pwd":"123456"},
    {"name":"Arthur1252@mailinator.com","pwd":"123456"},
    {"name":"Arthur1255@mailinator.com","pwd":"123456"},
    {"name":"Arthur1256@mailinator.com","pwd":"123456"},
    {"name":"Arthur1258@mailinator.com","pwd":"123456"},
    {"name":"Arthur1259@mailinator.com","pwd":"123456"},
    {"name":"Arthur1261@mailinator.com","pwd":"123456"},
    {"name":"Arthur1262@mailinator.com","pwd":"123456"},
    {"name":"Arthur1266@mailinator.com","pwd":"123456"},
    {"name":"Arthur1267@mailinator.com","pwd":"123456"},
    {"name":"Arthur1272@mailinator.com","pwd":"123456"},
    {"name":"Arthur1274@mailinator.com","pwd":"123456"},
    {"name":"Arthur1275@mailinator.com","pwd":"123456"},
    {"name":"Arthur1277@mailinator.com","pwd":"123456"},
    {"name":"Arthur1278@mailinator.com","pwd":"123456"},
    {"name":"Arthur1279@mailinator.com","pwd":"123456"},
    {"name":"Arthur1281@mailinator.com","pwd":"123456"},
    {"name": "ann4@mailinator.com", "pwd": "123456"},
    {"name": "ann9@mailinator.com", "pwd": "123456"},
    {"name": "ann10@mailinator.com", "pwd": "123456"},
    {"name": "ann11@mailinator.com", "pwd": "123456"},
    {"name": "ann13@mailinator.com", "pwd": "123456"},
    {"name": "ann23@mailinator.com", "pwd": "123456"},
    {"name": "ann28@mailinator.com", "pwd": "123456"},
    {"name": "ann29@mailinator.com", "pwd": "123456"},
    {"name": "ann32@mailinator.com", "pwd": "123456"},
    {"name": "ann33@mailinator.com", "pwd": "123456"},
    {"name": "ann35@mailinator.com", "pwd": "123456"},
    {"name": "bob1@mailinator.com", "pwd": "123456"},
    {"name": "bob4@mailinator.com", "pwd": "123456"},
    {"name": "bob7@mailinator.com", "pwd": "123456"},
    {"name": "bob8@mailinator.com", "pwd": "123456"},
    {"name": "bob9@mailinator.com", "pwd": "123456"},
    {"name": "bob10@mailinator.com", "pwd": "123456"},
    {"name": "bob17@mailinator.com", "pwd": "123456"},
    {"name": "bob18@mailinator.com", "pwd": "123456"},
    {"name": "bob20@mailinator.com", "pwd": "123456"},
    {"name": "bob23@mailinator.com", "pwd": "123456"},

    {"name": "hush1@mailinator.com", "pwd": "123456"},
    {"name": "hush2@mailinator.com", "pwd": "123456"},
    {"name": "hush3@mailinator.com", "pwd": "123456"},
    {"name": "hush4@mailinator.com", "pwd": "123456"},
    {"name": "hush5@mailinator.com", "pwd": "123456"},
    {"name": "qwe1@mailinator.com", "pwd": "123456"},
    {"name": "qwe2@mailinator.com", "pwd": "123456"},
    {"name": "qwe3@mailinator.com", "pwd": "123456"},
    {"name": "qwe4@mailinator.com", "pwd": "123456"},
    {"name": "qwe5@mailinator.com", "pwd": "123456"},
    {"name": "aaa1@mailinator.com", "pwd": "123456"},
    {"name": "aaa2@mailinator.com", "pwd": "123456"},
    {"name": "aaa3@mailinator.com", "pwd": "123456"},
    {"name": "aaa4@mailinator.com", "pwd": "123456"},
    {"name": "aaa5@mailinator.com", "pwd": "123456"},
    {"name": "zzz1@mailinator.com", "pwd": "123456"},
    {"name": "zzz2@mailinator.com", "pwd": "123456"},
    {"name": "zzz3@mailinator.com", "pwd": "123456"},
    {"name": "zzz4@mailinator.com", "pwd": "123456"},
    {"name": "zzz5@mailinator.com", "pwd": "123456"},
]

def get_url(key):
    millis = int(round(time.time() * 1000))
    url = {}
    url["key"] = key
    url["company_base"] = "https://rong.36kr.com/n/api/company/%s?asEncryptedTs=0.9998040941925237&asTs=%s" % (key, millis)
    url["past_finance"] = "https://rong.36kr.com/n/api/company/%s/finance?asEncryptedTs=0.9998040941925237&asTs=%s" % (key, millis)
    # url["past_investor"] = "http://rong.36kr.com/api/company/%s/past-investor?pageSize=100" % key
    # url["funds"] = "https://rong.36kr.com/n/api/company/%s/funds" % key
    url["product"] = "https://rong.36kr.com/n/api/company/%s/product?asEncryptedTs=0.9998040941925237&asTs=%s" % (key, millis)
    # url["past_investment"] = "http://rong.36kr.com/api/company/%s/past-investment" % key
    # url["company_fa"] = "http://rong.36kr.com/api/fa/company-fa?cid=%s" % key
    # url["founders"] = "http://rong.36kr.com/api/company/%s/founder?pageSize=1000" % key
    # url["employees"] = "http://rong.36kr.com/api/company/%s/employee?pageSize=1000" % key
    # url["former_members"] = "http://rong.36kr.com/api/company/%s/former-member?pageSize=1000" % key
    url["member"] = "https://rong.36kr.com/n/api/company/%s/member?asEncryptedTs=0.9998040941925237&asTs=%s" % (key, millis)
    # url["similar"] = "https://rong.36kr.com/n/api/company/%s/similar" % key

    return url


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=40,max_crawl=10):
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
    def __init__(self,timeout=40,max_crawl=20):
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


def run_news(column, crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["id"], URL["name"])
        time.sleep(random.randint(13, 18))

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
                time.sleep(random.randint(3,8))

    save(SOURCE, TYPE, url_map["company_base"], id, company)


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
        "key": key,
        "key_int": key_int,
        "content": content
    }
    newflag = True
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key": key})
    if item is not None:
        if item["content"] != content:
            collection.delete_one({"source": SOURCE, "type": TYPE, "key": key})
            logger.info("old data changed for company: %s", key)
        else:
            logger.info("old data not changed for company: %s", key)
            newflag = False
    if newflag is True: collection.insert_one(collection_content)
    mongo.close()
    logger.info("Saved: %s", url)


def process(content, flag, column):

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

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "type": TYPE, "key_int": int(id)})
            mongo.close()
            # if item is None or ((datetime.datetime.now() - item["date"]).days>= 1 and (datetime.datetime.now() - item["date"]).days <2):
            if item is None:
                URLS.append(a)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return len(URLS)

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
                    cnt = process(result['content'], flag, column)
                    if cnt > 0:
                        logger.info("%s has %s fresh company", url, cnt)
                        logger.info(URLS)
                        time.sleep(random.randint(13, 18))
                        threads = [gevent.spawn(run_news, column, companycrawler) for i in xrange(concurrent_num)]
                        gevent.joinall(threads)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
        time.sleep(random.randint(13, 18))



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        ccrawler = kr36_user.ListCrawler()
        dt = datetime.datetime.now()
        logger.info("now hour is %s", dt.hour)

        if dt.hour >= 9 and dt.hour <= 20:
            logger.info("%s company %s start...", SOURCE, flag)
            listcrawler = ListCrawler()
            companycrawler = kr36Crawler()

            # download_crawler = None
            for column in columns:
                CURRENT_PAGE = 1
                run(flag, column, ccrawler, ccrawler, concurrent_num)

        if flag == "incr":
            gevent.sleep(60*60)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            link = param
            crawler_news({},kr36Crawler(),link, "aaaaaa")

    else:
        start_run(1, "incr")