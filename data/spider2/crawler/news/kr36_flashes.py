# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import json

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_Kr36_newfs", stream=True)
logger = loghelper.get_logger("crawler_Kr36_newfs")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

newsid = []
b_id =""

TYPE = 60008

def find_companyId(sourceId):
    if sourceId== "0" or sourceId==0:
        return None
    conn = db.connect_torndb()
    sc = conn.get("select * from source_company where source=%s and sourceId=%s", 13020, sourceId)
    if sc is not None:
        if sc["companyId"] is not None:
            return sc["companyId"]
    return None



class kr36Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                # logger.info(j)
            except:
                return False

            if j.has_key("data"):
                return True

        return False

class kr36NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)
        if title.find("36氪_为创业者提供最好的产品和服务") != -1:
            return False
        if title.find("36氪") >= 0:
            return True
        # logger.info(content)
        return False


def has_content(content):
    # logger.info(newsid)
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

def has_news_content(item):
    if item.has_key("description") is False:
        return False
    return True


def process_news(item):
    if has_news_content(item):


        news_time = datetime.datetime.strptime(item["published_at"],"%Y-%m-%d %H:%M:%S")

        title = item["title"]

        key = str(item["id"])

        url = "http://36kr.com/newsflashes/%s" % key
        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": 13020,
            "key": key,
            "key_int": int(key),
            "type": TYPE,
            "original_tags":[],
            "processStatus":0,
            # "companyId":companyId,
            "companyIds": [],
            "category": None,
            "domain": domain,
            "categoryNames": []
        }

        dcontents = []
        if item["description"] is not None:
            dc = {
                "rank": 1,
                "content": "36氪快讯",
                "image": "",
                "image_src": "",
            }

            dcontents.append(dc)
            dc = {
                "rank": 2,
                "content": item["description"],
                "image": "",
                "image_src": "",
            }
            dcontents.append(dc)
            if item.has_key("news_url") is True and item["news_url"] is not None:
                dc = {
                    "rank": 3,
                    "content": item["news_url"],
                    "image": "",
                    "image_src": "",
                }
                dcontents.append(dc)
            logger.info(item["description"])


        dnews["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)

        post = util.get_posterId_from_news(dcontents)
        dnews["postId"] = post
        # dnews["post"] = post
        dnews["brief"] = brief
        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

        # collection_news.insert(dnews)
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)




def process_page(content, flag):
    logger.info(newsid)
    while True:
        if len(newsid) == 0:
            break
        newsid.pop(0)
    bid = None
    j = json.loads(content)
    infos = j["data"]["items"]
    if infos is not None:
        for info in infos:
            key = info["id"]
            title = info["title"]
            date = info["published_at"]
            # logger.info("%s, %s, %s", key, date, title)

            if collection_news.find_one({"source": 13020, "key_int": int(key), "type":60008}) is None or flag == "all":
                craw = True
                newses = list(collection_news.find({"title": title}))
                for news in newses:
                    if news.has_key("type") and news["type"] > 0:
                        craw = False
                        break
                if craw:
                    logger.info("%s, %s, %s", key, date, title)
                    newsid.append(key)
                    process_news(info)

            bid = key

    return len(newsid), bid


def start_run(flag):
    logger.info(newsid)
    global b_id
    while True:
        logger.info("36kr news %s start...", flag)

        crawler = kr36Crawler()
        while True:
            page_url = "http://36kr.com/api/newsflash?b_id%s=&per_page=20" % b_id

            result = crawler.crawl(page_url, agent=True)
            if result['get'] == 'success':
                if has_content(result["content"]):
                    numnews, b_id = process_page(result["content"], flag)
                    if numnews > 0 or flag == "all":
                        logger.info("crawler new news :%s", numnews)
                        # logger.info("news: %s", ";".join(newsid))
                        # continue
                    else:
                        b_id = ""
                else:
                    b_id = ""
                    logger.info("no content")
                    logger.info(result["content"])
                break


        logger.info("36kr news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*5)        #10 minutes
        else:
            gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "all":
            start_run("all")
        else:
            start_run("incr")
    else:
        start_run("incr")