# -*- coding: utf-8 -*-
import os, sys,random, datetime,time
import urllib2
import urllib
import json
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import GlobalValues_news
import activity_simhash
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util


#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news
download_crawler = download.DownloadCrawler(use_proxy=False)

#logger
loghelper.init_logger("crawler_36kr_activity", stream=True)
logger = loghelper.get_logger("crawler_36kr_activity")

SOURCE=13020
TYPE=60002

class kr36Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "您请求的过于频繁，请稍后再试！":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
            else:
                return True
        return False


def has_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False

        if j["code"] == 0 and j["data"] != "活动不存在或状态非法":
            return True
        else:
            logger.info("code=%d, %s, %s" % (j["code"], j["data"], j["msg"]))
    else:
        logger.info("Fail to get content")

    return False

def catmap(id):
    id = int(id)
    if id== 1:
        return ["Demo Day"]
    elif id == 4:
        return ["氪空间"]
    elif id == 5:
        return ["股权投资"]
    elif id == 6:
        return ["企业服务"]
    elif id == 7:
        return ["极速融资"]
    else:
        return []


def process(g, crawler, url, key, content):
    if has_content(content):
        j = json.loads(content)
        info = j["data"]
        #logger.info(info)
        DT = datetime.date.today()
        TODAY = datetime.datetime(DT.year, DT.month, DT.day)

        if info.has_key("title") and info.has_key("link") and info.has_key("status") and info.has_key("activityBeginTime"):

            key_int = int(key)
            link = info["link"]
            title = info["title"]
            status = info["status"]
            img = info["headImageUrl"]

            if img is not None:
                # logger.info("poster: %s", poster)
                # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
                (posturl, width, height) = parser_mysql_util.get_logo_id_new(img, download_crawler, SOURCE, key,
                                                                             "news")
                if posturl is not None:
                    poster = str(posturl)
                else:
                    poster = None

            if info.has_key("categoryId"):
                tags =  catmap(info["categoryId"])
            else:
                tags = []

            beginTime = time.localtime(info["activityBeginTime"] / 1000)
            beginDate = datetime.datetime(beginTime.tm_year, beginTime.tm_mon, beginTime.tm_mday, beginTime.tm_hour,
                                          beginTime.tm_min, beginTime.tm_sec)
            endTime = time.localtime(info["activityEndTime"] / 1000)
            endDate = datetime.datetime(endTime.tm_year, endTime.tm_mon, endTime.tm_mday, endTime.tm_hour,
                                        endTime.tm_min, endTime.tm_sec)

            #location = info["city"]

            # if status != "online":
            #     return
            if beginDate is None or beginDate < TODAY:
                # Not save active activity
                return
            if link.find("chuang.36kr.com/huodong#/activityApply/details/") == -1:
                return

            flag, domain = url_helper.get_domain(url)
            dact = {
                "beginDate": beginDate - datetime.timedelta(hours=8),
                "endDate": endDate - datetime.timedelta(hours=8),
                "date": beginDate - datetime.timedelta(hours=8),
                "title": title,
                "link": link,
                "createTime": datetime.datetime.now(),
                "source": SOURCE,
                "key": key,
                "key_int": key_int,
                "type": TYPE,
                "original_tags": tags,
                "processStatus": 0,
                "companyIds": [],
                "location": info.get("city",None),
                "city": info.get("city",None),
                "sponors": ["36氪"],
                "post": poster,
                "domain": domain
            }
            dcontents = []

            if info.has_key("activityBriefArray") and len(info["activityBriefArray"])>= 1:
                rank = 1
                for text in info["activityBriefArray"]:
                    if not text.has_key("value"):
                        continue
                    d = pq(text["value"])('p')
                    dd = None

                    if d.text() is not None and d.text().strip() != "":
                        logger.info(d.text())
                        dd = {
                            "rank": rank,
                            "content": d.text(),
                            "image": "",
                            "image_src": "",
                        }
                    elif d('img').attr("src") is not None and d('img').attr("src") != "":
                        logger.info(d('img').attr("src"))
                        # dd = {
                        #     "rank": rank,
                        #     "content": "",
                        #     "image": "",
                        #     "image_src": d('img').attr("src").replace("!heading", ""),
                        # }
                        (imgurl, width, height) = parser_mysql_util.get_logo_id_new(d('img').attr("src").replace("!heading", ""),
                                                                                    download_crawler, SOURCE,
                                                                                    key, "news")
                        if imgurl is not None:
                            dd = {
                                "rank": rank,
                                "content": "",
                                "image": str(imgurl),
                                "image_src": "",
                                "height": int(height),
                                "width": int(width)
                            }
                        else:
                            continue
                    if dd is not None:
                        dcontents.append(dd)
                        rank += 1
            dact["contents"] = dcontents
            value = activity_simhash.get_simhash_value(dcontents)
            dact["simhashValue"] = value

            if collection_news.find_one({"source": SOURCE, "type": TYPE, "key_int": key_int}) is not None:
                collection_news.delete_one({"source": SOURCE, "type": TYPE, "key_int": key_int})

                collection_news.insert(dact)
                logger.info("%s, %s, %s, %s, %s, %s", title, beginDate, endDate, info.get("city", None), link, ":".join(tags))
            else:
                if activity_simhash.check_same_act(dact) is True:
                    pass
                else:
                    collection_news.insert(dact)
                    logger.info("%s, %s, %s, %s, %s, %s", title, beginDate, endDate, info.get("city",None), link, ":".join(tags))
        else:
            logger.info("%s, acitivity is incorrect", url)


        g.latestIncr()

def crawl(crawler, key ,g):
    url = "http://chuang.36kr.com/api/actapply/%s" % key
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            # logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception, ex:
                logger.exception(ex)
            break
        elif result["content"] is not None and result["content"].find("后台出错，请联系管理员！") > 0:
            break

def run(g, crawler):
    while True:
        if g.finish(num=50):
            return
        key = g.nextKey()
        crawl(crawler, key, g)


def start_run(concurrent_num, flag):
    while True:
        logger.info("36kr activity %s start...", flag)

        g = GlobalValues_news.GlobalValues(13020, TYPE, flag, back=1)

        threads = [gevent.spawn(run, g, kr36Crawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("36kr activity %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*60)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

        #break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            key = str(int(param))
            g = GlobalValues_news.GlobalValues(13800, TYPE, "incr", back=0)
            crawl(kr36Crawler(), key, g)
    else:
        start_run(1, "incr")