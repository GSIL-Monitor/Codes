# -*- coding: utf-8 -*-
import os, sys, datetime, json, urllib2, time
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db

#logger
loghelper.init_logger("crawler_itjuzi_company3", stream=True)
logger = loghelper.get_logger("crawler_itjuzi_company3")


TYPE = 36001
SOURCE =13030
columns = [
    {"column": "new", "max": 20}]
URLS = []

class ItjuziCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title == "找不到您访问的页面":
            #return True
            return False
        if title.find("IT桔子") >= 0:
            return True
        return False

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["status"] == 1 or j["status"] == 4:
                logger.info("code=%d, %s" % (j["status"], j["msg"]))
                return True
            else:
                logger.info("code=%d, %s" % (j["status"], j["msg"]))
                return False
        return False


class SessionCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, max_crawl=10):
        BaseCrawler.BaseCrawler.__init__(self, max_crawl=max_crawl)

    def get_jsessionid(self, url, headers, postdata):
        nsession = None
        """Get JSESSIONID."""
        flag = False
        while True:
            logger.info("get session : %s|%s", url, postdata)
            self.init_http_session(url)
            try:
                request = urllib2.Request(url, headers=headers,data=postdata)
                r = self.opener.open(request, timeout=20)
                if r.getcode() != 200:
                    logger.info("wrong 1")
                    continue

                for cookie in self.cookiejar:
                    logger.info("Get Cookie step1: %s, %s", cookie.name, cookie.value)
                    if cookie.name == "identity":
                        flag = True
                    if cookie.name == "session":
                        nsession = cookie.value
                if flag is True:
                    break

            except Exception, e:
                logger.info(e)

        return True,nsession


def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.replace("-", "|").split("|")
    if len(temp) != 2:
        return False
    if temp[1].strip() != "IT桔子":
        return False
    if temp[0].strip() == "" or temp[0].strip() == "的简介，官网，联系方式，":
        return False
    return True

def run_news(column, crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)
        crawl(column, crawler, URL["id"], URL["name"])


def crawl(column, crawler, id, name):
    url = "https://www.itjuzi.com/company/%s" % id
    retries = 0
    retries_2 = 0
    headers = {
               # "Cookie": "acw_sc__=5a44bfed12f472772990fdadd57a71ba15554322",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"}
    while True:
        result = crawler.crawl(url, headers=headers)
        if result['get'] == 'success':
            #logger.info(result["content"])
            try:
                # save(g, crawler, url, key, result['content'])
                if has_content(result["content"]):
                    save(SOURCE, TYPE, url, id, result["content"])
            except Exception,ex:
                logger.exception(ex)
            break
        else:
            if result.has_key("content") is False or result["content"] is None or result["content"].strip() == "" or result["content"].find("</html>") == -1:
                retries_2 += 1
                if retries_2 > 25:
                    break
                continue
            d = pq(html.fromstring(result["content"]))
            title = d('head> title').text().strip()
            if title == "找不到您访问的页面":
                if retries >= 2:
                    break
                retries += 1

        retries_2 += 1
        if retries_2 > 25:
            break



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
    # logger.info(content)
    j = json.loads(content)
    companies = j["data"]["rows"]
    cnt = 0
    if len(companies) == 0:
        return cnt

    for a in companies:
        try:

            id = a["com_id"]
            name = a["com_name"]
            logger.info("company: %s|%s", id, name)

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "type":36001,"key_int": int(id)})
            mongo.close()
            # if item is None or ((datetime.datetime.now() - item["date"]).days>= 1 and (datetime.datetime.now() - item["date"]).days <2):
            if item is None:
                URLS.append({"id": id, "name": name})
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")
    return len(URLS)


def get_session(scrawler,crawlFlag=True):
    session = None
    nheaders = {
        # "Cookie": "acw_sc__=5a44bfed12f472772990fdadd57a71ba15554322",
        # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",

        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    url = 'https://www.itjuzi.com/user/login?redirect=%2Fcompany&flag=radar&radar_coupon='

    mongo = db.connect_mongo()
    collection = mongo.xiniudata.itjuziLogin
    ids = list(collection.find({}).sort("modifyTime", -1))

    for id in ids:
        # begin time do not get a session,just check if old session works
        if crawlFlag is False and id.has_key("session") is True and id["session"] is not None:
            logger.info("first time: checking old session: %s", id["session"])
            session = id["session"]
            break

        if id.has_key("session") is True:
            nheaders["Cookie"] = 'session=' + id["session"]

        pdata = "identity=%s&password=%s&submit=&page=&url=" % (id["name"], id["password"])
        # Get session
        res, newsession = scrawler.get_jsessionid(url, nheaders, pdata)
        if res is True:
            logger.info("old: %s, new :%s", id.get("session",None), newsession)
            if newsession is not None:
                session = newsession
            else:
                session = id.get("session",None)

        if session is not None:
            collection.update_one({"_id":id["_id"]},{'$set':{"session":session,
                                                             "modifyTime": datetime.datetime.now()}})
            break
            
    mongo.close()
    return session


def run(flag, column, scrawler, listcrawler, companycrawler, concurrent_num):
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
        headers = {
            # "Cookie": "acw_sc__=5a44bfed12f472772990fdadd57a71ba15554322",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest'
        }


        if key == 1:
            url = 'http://radar.itjuzi.com/company/infonew'
        else:
            url = 'http://radar.itjuzi.com/company/infonew?page=%s' % key
        ses = None
        firstTime = True
        while True:
            if firstTime is True:
                ses = get_session(scrawler,crawlFlag=False)
                firstTime = False

            if ses is None:
                ses = get_session(scrawler)

            if ses is not None:
                headers["Cookie"] = 'session=' + ses
                result = listcrawler.crawl(url,agent=True, headers=headers)

                if result['get'] == 'success':
                    j = json.loads(result["content"])
                    if j["status"] == 4:
                        logger.info("need to reget session")
                        ses = None
                        continue
                    else:

                        cnt = process(result['content'], flag)
                        logger.info("%s has %s fresh company", url, cnt)
                        if cnt > 0:
                            logger.info("%s has %s fresh company", url, cnt)
                            logger.info(URLS)
                            run_news(column, companycrawler)

                    break


def process_invest(content, flag):
    # logger.info(content)
    j = json.loads(content)
    invests = j["data"]["rows"]
    cnt = 0
    if len(invests) == 0:
        return cnt

    for a in invests:
        try:
            i_id = a["invse_id"]
            url = "https://www.itjuzi.com/investevents/%s" % i_id
            id = a["com_id"]
            name = a["com_name"]
            logger.info("Invest: %s,  company: %s|%s", i_id, id, name)

            # check mongo data if link is existed
            mongo = db.connect_mongo()
            collection_news = mongo.raw.projectdata
            item = collection_news.find_one({"source": SOURCE, "type":36001, "key_int": int(id)})
            mongo.close()
            # if item is None or ((datetime.datetime.now() - item["date"]).days>= 1 and (datetime.datetime.now() - item["date"]).days <2):
            if item is None:
                URLS.append({"id": id, "name": name})

            save(13032, 36002, url, str(i_id), a)
        except Exception, e:
            logger.info(e)
            logger.info("cannot get company data")

    return len(URLS)


def run_invest(flag, column, scrawler, listcrawler, companycrawler, concurrent_num):
    global CURRENT_PAGE

    CURRENT_PAGE += 1
    headers = {
        # "Cookie": "acw_sc__=5a44bfed12f472772990fdadd57a71ba15554322",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }

    for loc in ["in", "out"]:
        url = 'http://radar.itjuzi.com/investevent/info?location=%s&orderby=def&page=1' % loc

        ses = None
        firstTime = True
        while True:
            if firstTime is True:
                ses = get_session(scrawler,crawlFlag=False)
                firstTime = False

            if ses is None:
                ses = get_session(scrawler)

            if ses is not None:
                headers["Cookie"] = 'session=' + ses
                result = listcrawler.crawl(url,agent=True, headers=headers)

                if result['get'] == 'success':
                    j = json.loads(result["content"])
                    if j["status"] == 4:
                        logger.info("need to reget session")
                        ses = None
                        continue
                    else:

                        cnt = process_invest(result['content'], flag)
                        logger.info("%s has %s fresh company", url, cnt)
                        if cnt > 0:
                            logger.info("%s has %s fresh company", url, cnt)
                            logger.info(URLS)
                            run_news(column, companycrawler)

                    break


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        dt = datetime.datetime.now()
        logger.info("now hour is %s", dt.hour)

        if dt.hour >= 9 and dt.hour <= 19:
            logger.info("%s company %s start...", SOURCE, flag)
            listcrawler = ListCrawler()
            companycrawler = ItjuziCrawler()
            scrawler = SessionCrawler()
            # download_crawler = None
            for column in columns:
                CURRENT_PAGE = 1
                run(flag, column, scrawler, listcrawler, companycrawler, concurrent_num)
                run_invest(flag, column, scrawler, listcrawler, companycrawler, concurrent_num)
        # break
        if flag == "incr":
            time.sleep(120*60)        #30 minutes
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
            crawl({},ItjuziCrawler(),link, "aaaaaa")

    else:
        start_run(1, "incr")