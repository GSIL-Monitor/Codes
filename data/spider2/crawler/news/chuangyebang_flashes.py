# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()
import json

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, extract, db, util, url_helper, download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util
import time

# logger
loghelper.init_logger("crawler_chuangyebang_newfs", stream=True)
logger = loghelper.get_logger("crawler_chuangyebang_newfs")

# mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

newsid = []
b_id = ""

SOURCE = 13806
TYPE = 60008


def find_companyId(sourceId):
    if sourceId == "0" or sourceId == 0:
        return None
    conn = db.connect_torndb()
    sc = conn.get("select * from source_company where source=%s and sourceId=%s", 13020, sourceId)
    if sc is not None:
        if sc["companyId"] is not None:
            return sc["companyId"]
    return None


class chuangyebangCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self, use_proxy=1)

    def is_crawl_success(self, url, content):
        if content is not None:
            d = pq(html.fromstring(content.decode('utf-8')))
            infos = d('.bulletin-item')
            if len(infos) > 0: return True

        return False


def has_content(content):
    # logger.info(newsid)
    if content is not None:
        d = pq(html.fromstring(content.decode('utf-8')))
        infos = d('.bulletin-item')
        if len(infos) > 0: return True
    else:
        logger.info("Fail to get content")
    return False


def has_news_content(item):
    if item.has_key("description") is False:
        return False
    return True


def process_news(item):
    # if has_news_content(item):
    if 1:
        d = pq(item)
        title = d('.item-title').text()
        url = d('.item-title').attr('href')
        key = url.split('/')[-1].split('.')[0]
        date = d('.news-time').attr('data-time')
        news_time = datetime.datetime.fromtimestamp(float(date))

        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": TYPE,
            "original_tags": [],
            "processStatus": 0,
            # "companyId":companyId,
            "companyIds": [],
            "category": None,
            "domain": domain,
            "categoryNames": []
        }

        dcontents = []
        description = d('.item-desc').text()
        if description is not None:
            dc = {
                "rank": 1,
                "content": "创业邦快讯",
                "image": "",
                "image_src": "",
            }

            dcontents.append(dc)
            dc = {
                "rank": 2,
                "content": description,
                "image": "",
                "image_src": "",
            }
            dcontents.append(dc)

            logger.info(description)

        dnews["contents"] = dcontents

        brief = util.get_brief_from_news(dcontents)

        post = util.get_posterId_from_news(dcontents)
        dnews["postId"] = post
        # dnews["post"] = post
        dnews["brief"] = brief
        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        # collection_news.insert(dnews)


def process_page(content, flag):
    d = pq(html.fromstring(content.decode('utf-8')))

    infos = d('.bulletin-item')
    if infos is not None:
        for info in infos:
            title = d(info)('.item-title').text()
            url = d(info)('.item-title').attr('href')
            key = url.split('/')[-1].split('.')[0]
            date = d(info)('.news-time').attr('data-time')
            date = datetime.datetime.fromtimestamp(float(date))
            logger.info("%s, %s, %s", key, date, title)

            if collection_news.find_one({"source": SOURCE, "key_int": int(key), "type": TYPE}) is None or flag == "all":
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

                    # bid = key

                    # return len(newsid), bid


def start_run(flag):
    while True:
        logger.info("chuangyebang flashes %s start...", flag)

        crawler = chuangyebangCrawler()
        currentTime = int(time.time())
        while True:
            page_url = "http://www.cyzone.cn/index.php?m=content&c=index&a=init&tpl=page_kuaixun&inputtime=%s" % currentTime

            result = crawler.crawl(page_url, agent=True)
            if result['get'] == 'success':
                if has_content(result["content"]):
                    process_page(result["content"], flag)

                break

        logger.info("chuangyebang news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60 * 5)  # 10 minutes
        else:
            gevent.sleep(86400 * 3)  # 3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "all":
            start_run("all")
        else:
            start_run("incr")
    else:
        start_run("incr")
