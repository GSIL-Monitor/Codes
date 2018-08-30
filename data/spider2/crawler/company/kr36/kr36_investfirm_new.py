# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
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

#logger
loghelper.init_logger("crawler_36kr_investor", stream=True)
logger = loghelper.get_logger("crawler_36kr_investor")

TYPE = 36003
SOURCE =13023
URLS = []
CURRENT_PAGE = 1
linkPattern = "/article/\d+"
Nocontents = [
]
columns = [
    {"column": None, "max": 1826},
]

KEYS = [i for i in range(4,1826)]

login_users = [
    {"name":"daffy@mailinator.com", "pwd":"daffy123"},
    {"name":"minnie@mailinator.com", "pwd":"minnie"},
    {"name":"elmer@mailinator.com", "pwd":"elmer123"},
    {"name":"tweety@mailinator.com", "pwd":"tweety"},
    {"name":"alfonse@mailinator.com", "pwd":"alfonse"},
    {"name":"alice@mailinator.com","pwd":"123456"},
    {"name":"anna@mailinator.com","pwd":"123456"},
    {"name":"annie@mailinator.com","pwd":"123456"},
    {"name":"barbara@mailinator.com","pwd":"123456"},
    {"name":"bernice@mailinator.com","pwd":"123456"},
    {"name":"dolores@mailinator.com","pwd":"123456"},
    {"name":"doris@mailinator.com","pwd":"123456"},
    {"name":"dorothy@mailinator.com","pwd":"123456"},
    {"name":"edith@mailinator.com","pwd":"123456"},
    {"name":"edna@mailinator.com","pwd":"123456"},
    {"name":"eleanor@mailinator.com","pwd":"123456"},
    {"name":"elizabeth@mailinator.com","pwd":"123456"},
    {"name":"ethel@mailinator.com","pwd":"123456"},
    {"name":"evelyn@mailinator.com","pwd":"123456"},
    {"name":"florence@mailinator.com","pwd":"123456"},
    {"name":"frances@mailinator.com","pwd":"123456"},
    {"name":"gladys@mailinator.com","pwd":"123456"},
    {"name":"gloria@mailinator.com","pwd":"123456"},
    {"name":"grace@mailinator.com","pwd":"123456"},
    {"name":"hazel@mailinator.com","pwd":"123456"},
    {"name":"Arthur123@mailinator.com","pwd":"123456"},
    {"name":"Arthur1234@mailinator.com","pwd":"123456"},
    {"name":"Arthur1235@mailinator.com","pwd":"123456"},
    {"name":"Arthur1236@mailinator.com","pwd":"123456"},
    {"name":"Arthur1237@mailinator.com","pwd":"123456"},
    {"name":"Arthur1238@mailinator.com","pwd":"123456"},
    {"name":"Arthur1239@mailinator.com","pwd":"123456"},
    {"name":"Arthur1240@mailinator.com","pwd":"123456"},
    {"name":"Arthur1241@mailinator.com","pwd":"123456"},
    {"name":"Arthur1242@mailinator.com","pwd":"123456"},
    {"name":"Arthur1243@mailinator.com","pwd":"123456"},
    {"name":"Arthur1244@mailinator.com","pwd":"123456"},
    {"name":"Arthur1245@mailinator.com","pwd":"123456"},
    {"name":"Arthur1246@mailinator.com","pwd":"123456"},
    {"name":"Arthur1247@mailinator.com","pwd":"123456"},
    {"name":"Arthur1248@mailinator.com","pwd":"123456"},
    {"name":"Arthur1249@mailinator.com","pwd":"123456"},
    {"name":"Arthur1250@mailinator.com","pwd":"123456"},
    {"name":"Arthur1251@mailinator.com","pwd":"123456"},
    {"name":"Arthur1252@mailinator.com","pwd":"123456"},
    {"name":"Arthur1253@mailinator.com","pwd":"123456"},
    {"name":"Arthur1254@mailinator.com","pwd":"123456"},
    {"name":"Arthur1255@mailinator.com","pwd":"123456"},
    {"name":"Arthur1256@mailinator.com","pwd":"123456"},
    {"name":"Arthur1257@mailinator.com","pwd":"123456"},
    {"name":"Arthur1258@mailinator.com","pwd":"123456"},
    {"name":"Arthur1259@mailinator.com","pwd":"123456"},
    {"name":"Arthur1260@mailinator.com","pwd":"123456"},
    {"name":"Arthur1261@mailinator.com","pwd":"123456"},
    {"name":"Arthur1262@mailinator.com","pwd":"123456"},
    {"name":"Arthur1263@mailinator.com","pwd":"123456"},
    {"name":"Arthur1264@mailinator.com","pwd":"123456"},
    {"name":"Arthur1265@mailinator.com","pwd":"123456"},
    {"name":"Arthur1266@mailinator.com","pwd":"123456"},
    {"name":"Arthur1267@mailinator.com","pwd":"123456"},
    {"name":"Arthur1268@mailinator.com","pwd":"123456"},
    {"name":"Arthur1269@mailinator.com","pwd":"123456"},
    {"name":"Arthur1270@mailinator.com","pwd":"123456"},
    {"name":"Arthur1271@mailinator.com","pwd":"123456"},
    {"name":"Arthur1272@mailinator.com","pwd":"123456"},
    {"name":"Arthur1273@mailinator.com","pwd":"123456"},
    {"name":"Arthur1274@mailinator.com","pwd":"123456"},
    {"name":"Arthur1275@mailinator.com","pwd":"123456"},
    {"name":"Arthur1276@mailinator.com","pwd":"123456"},
    {"name":"Arthur1277@mailinator.com","pwd":"123456"},
    {"name":"Arthur1278@mailinator.com","pwd":"123456"},
    {"name":"Arthur1279@mailinator.com","pwd":"123456"},
    {"name":"Arthur1280@mailinator.com","pwd":"123456"},
    {"name":"Arthur1281@mailinator.com","pwd":"123456"},
    {"name":"Arthur1282@mailinator.com","pwd":"123456"},
    {"name": "ann1@mailinator.com", "pwd": "123456"},
    {"name": "ann2@mailinator.com", "pwd": "123456"},
    {"name": "ann3@mailinator.com", "pwd": "123456"},
    {"name": "ann4@mailinator.com", "pwd": "123456"},
    {"name": "ann5@mailinator.com", "pwd": "123456"},
    {"name": "ann6@mailinator.com", "pwd": "123456"},
    {"name": "ann7@mailinator.com", "pwd": "123456"},
    {"name": "ann8@mailinator.com", "pwd": "123456"},
    {"name": "ann9@mailinator.com", "pwd": "123456"},
    {"name": "ann10@mailinator.com", "pwd": "123456"},
    {"name": "ann11@mailinator.com", "pwd": "123456"},
    {"name": "ann12@mailinator.com", "pwd": "123456"},
    {"name": "ann13@mailinator.com", "pwd": "123456"},
    {"name": "ann14@mailinator.com", "pwd": "123456"},
    {"name": "ann15@mailinator.com", "pwd": "123456"},
    {"name": "ann16@mailinator.com", "pwd": "123456"},
    {"name": "ann17@mailinator.com", "pwd": "123456"},
    {"name": "ann18@mailinator.com", "pwd": "123456"},
    {"name": "ann19@mailinator.com", "pwd": "123456"},
    {"name": "ann20@mailinator.com", "pwd": "123456"},
    {"name": "ann21@mailinator.com", "pwd": "123456"},
    {"name": "ann22@mailinator.com", "pwd": "123456"},
    {"name": "ann23@mailinator.com", "pwd": "123456"},
    {"name": "ann24@mailinator.com", "pwd": "123456"},
    {"name": "ann25@mailinator.com", "pwd": "123456"},
    {"name": "ann26@mailinator.com", "pwd": "123456"},
    {"name": "ann27@mailinator.com", "pwd": "123456"},
    {"name": "ann28@mailinator.com", "pwd": "123456"},
    {"name": "ann29@mailinator.com", "pwd": "123456"},
    {"name": "ann30@mailinator.com", "pwd": "123456"},
    {"name": "ann31@mailinator.com", "pwd": "123456"},
    {"name": "ann32@mailinator.com", "pwd": "123456"},
    {"name": "ann33@mailinator.com", "pwd": "123456"},
    {"name": "ann34@mailinator.com", "pwd": "123456"},
    {"name": "ann35@mailinator.com", "pwd": "123456"},
    {"name": "bob1@mailinator.com", "pwd": "123456"},
    {"name": "bob2@mailinator.com", "pwd": "123456"},
    {"name": "bob3@mailinator.com", "pwd": "123456"},
    {"name": "bob4@mailinator.com", "pwd": "123456"},
    {"name": "bob5@mailinator.com", "pwd": "123456"},
    {"name": "bob6@mailinator.com", "pwd": "123456"},
    {"name": "bob7@mailinator.com", "pwd": "123456"},
    {"name": "bob8@mailinator.com", "pwd": "123456"},
    {"name": "bob9@mailinator.com", "pwd": "123456"},
    {"name": "bob10@mailinator.com", "pwd": "123456"},
    {"name": "bob11@mailinator.com", "pwd": "123456"},
    {"name": "bob12@mailinator.com", "pwd": "123456"},
    {"name": "bob13@mailinator.com", "pwd": "123456"},
    {"name": "bob14@mailinator.com", "pwd": "123456"},
    {"name": "bob15@mailinator.com", "pwd": "123456"},
    {"name": "bob16@mailinator.com", "pwd": "123456"},
    {"name": "bob17@mailinator.com", "pwd": "123456"},
    {"name": "bob18@mailinator.com", "pwd": "123456"},
    {"name": "bob19@mailinator.com", "pwd": "123456"},
    {"name": "bob20@mailinator.com", "pwd": "123456"},
    {"name": "bob21@mailinator.com", "pwd": "123456"},
    {"name": "bob22@mailinator.com", "pwd": "123456"},
    {"name": "bob23@mailinator.com", "pwd": "123456"},
    {"name": "bob24@mailinator.com", "pwd": "123456"},
    {"name": "bob25@mailinator.com", "pwd": "123456"},
    {"name": "bob26@mailinator.com", "pwd": "123456"},
    {"name": "bob27@mailinator.com", "pwd": "123456"},
]

def get_url(key):
    url = {}
    url["key"] = key
    url["basic"] = "https://rong.36kr.com/n/api/org/%s/basic" % key
    url["member"] = "https://rong.36kr.com/n/api/org/%s/member" % key
    return url


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "操作成功！":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return True
            else:
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
        return False


class kr36Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "操作成功！":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return True
            else:
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
        return False

    # def login(self, url, redirect=True):
    #     while True:
    #         self.init_http_session(url)
    #
    #         idx = random.randint(0, len(login_users) - 1)
    #         login_user = login_users[idx]
    #         logger.info(login_user)
    #         logger.info("want: %s", url)
    #
    #         data = {
    #             "type": "login",
    #             "bind": False,
    #             "needCaptcha": False,
    #             "username": login_user["name"],
    #             "password": login_user["pwd"],
    #             "ok_url": "/"
    #
    #         }
    #         data = urllib.urlencode(data)
    #         headers = {
    #             "Referer": "https://passport.36kr.com"
    #         }
    #         user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
    #         headers['User-Agent'] = user_agent
    #
    #         try:
    #             request = urllib2.Request("https://passport.36kr.com/passport/sign_in", data, headers)
    #             r = self.opener.open(request, timeout=20)
    #             page = r.read()
    #             logger.info(page)
    #         except Exception, e:
    #             logger.info("wrong 1")
    #             logger.info(e)
    #             continue
    #
    #         if r.getcode() != 200:
    #             logger.info("wrong 2")
    #             continue
    #
    #         if page.strip() != '{"countDownTimer":3,"redirect_to":"/"}':
    #             logger.info("wrong 3")
    #             continue
    #
    #         try:
    #             request = urllib2.Request("https://uc.36kr.com/api/user/identity")
    #             r = self.opener.open(request, timeout=20)
    #             page = r.read()
    #             logger.info("identity")
    #             logger.info(page)
    #         except:
    #             logger.info("wrong here")
    #             continue
    #
    #         if r.getcode() == 200:
    #             try:
    #                 result = json.loads(page)
    #             except:
    #                 logger.info("wrong 4")
    #                 logger.info(page)
    #
    #                 continue
    #             # logger.info(result)
    #             if result["code"] == 0 and result["msg"] == "操作成功！":
    #                 break
    #         else:
    #             logger.info("wrong 5, %s", r.getcode())


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

        crawler_investor(column, crawler, URL["id"], URL["name"])

def crawler_investor(column, crawler, id, name):

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

    save(SOURCE, TYPE, url_map["basic"], id, company)


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


def process(content, flag):

    j = json.loads(content)
    # logger.info(content)
    companies = j["data"]["org"]["data"]
    ttnum = j["data"]["org"]["totalPages"]
    cnt = 0
    if len(companies) == 0:
        return cnt, ttnum

    for a in companies:
        try:

            id = a["org"]["id"]
            name = a["org"]["nameAbbr"]
            logger.info("Investor: %s|%s", id, name)


            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "key_int": int(id)})
            mongo.close()
            if item is None or (datetime.datetime.now() - item["date"]).days>= 1:
                URLS.append({"id": id, "name": name})
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return len(URLS),ttnum


def run(flag, column, listcrawler, companycrawler, concurrent_num):
    global CURRENT_PAGE
    # total_page=1
    while True:
        key = CURRENT_PAGE

        # if key > total_page:
        #     return
        if len(KEYS) == 0:
            return
        key = KEYS.pop(0)

        # CURRENT_PAGE += 1
        url = 'https://rong.36kr.com/n/api/org/list?page=%s' % (key)

        while True:
            result = listcrawler.crawl(url,agent=True)

            if result['get'] == 'success':
                try:
                    cnt, total_page = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh company", url, cnt)
                        logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, companycrawler) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, companycrawler)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s kr 36 investor start...", SOURCE, flag)
        # listcrawler = ListCrawler()
        # companycrawler = kr36Crawler()

        # download_crawler = None
        for column in columns:
            CURRENT_PAGE = 1
            # run(flag, column, listcrawler, companycrawler, concurrent_num)
            threads = [gevent.spawn(run, flag, column, ListCrawler(), kr36Crawler(), concurrent_num) for i in xrange(concurrent_num)]
            gevent.joinall(threads)

        break
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        start_run(1,"incr")
    else:
        start_run(5,"incr")
