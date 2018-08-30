# -*- coding: utf-8 -*-
import os, sys
import datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
from pymongo import MongoClient
import traceback
import urllib


reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,db,util

#logger
loghelper.init_logger("alexa_trends", stream=True)
logger = loghelper.get_logger("alexa_trends")

# mongo
mongo = db.connect_mongo()
alexa_collection = mongo.trend.alexa_raw

DOMAINS = []

class AlexaComCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False
        d = pq(content)
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)
        if title.find("Alexa") == -1:
            return False
        return True


class AlexaCnCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        return True


def handle_alexa_com_result(content, domain):
    try:
        d = pq(content)
        datas = d('strong.metrics-data')
        data_len = len(datas)

        global_rank = None
        country_rank = None
        bounce_rate = None
        daily_pageviews_per_visitor = None
        daily_time_on_site = None
        search_visits = None

        if data_len == 6:
            global_rank = pq(datas[0]).text()
            country_rank = pq(datas[1]).text()
            bounce_rate = pq(datas[2]).text()
            daily_pageviews_per_visitor = pq(datas[3]).text()
            daily_time_on_site = pq(datas[4]).text()
            search_visits = pq(datas[5]).text()
        elif data_len == 5:
            global_rank = pq(datas[0]).text()
            country_rank = ''
            bounce_rate = pq(datas[1]).text()
            daily_pageviews_per_visitor = pq(datas[2]).text()
            daily_time_on_site = pq(datas[3]).text()
            search_visits = pq(datas[4]).text()

        global_rank_value = None
        try:
            global_rank_value = int(global_rank.replace(",", ""))
        except:
            #traceback.print_exc()
            pass
        country_rank_value = None
        try:
            country_rank_value = int(country_rank.replace(",", ""))
        except:
            #traceback.print_exc()
            pass
        search_visits_value = None
        try:
            search_visits_value = float(search_visits.replace("%", "")) / 100
        except:
            #traceback.print_exc()
            pass

        dt = datetime.date.today()
        today = datetime.datetime(dt.year, dt.month, dt.day)

        result = {
            'date': today,
            'domain': app["domain"],
            'global_rank': global_rank,
            'country_rank': country_rank,
            'search_visits': search_visits,
            'global_rank_value': global_rank_value,
            'country_rank_value': country_rank_value,
            'search_visits_value': search_visits_value,
        }
        #logger.info(result)
        if result["global_rank"] is None:
            logger.info(content)
        return result

    except:
        traceback.print_exc()

    return None


def handle_alexa_cn_result(content, domain, crawler_cn):
    try:
        d = pq(content)
        data = d('script').text()
        data = ''.join(data)
        try:
            (ids,) = util.re_get_result("showHint\('(\S*)'\);", data)
        except:
            traceback.print_exc()
            # logger.info(html)
            return None

        id_arr = ids.split(',')

        data = {"url": id_arr[0],
                "sig": id_arr[1],
                "keyt": id_arr[2]
                }
        body = urllib.urlencode(data)
        url = "http://www.alexa.cn/api_150710.php"
        result = crawler_cn.crawl(url,postdata=body)
        if result['get'] == 'success':
            #logger.info(result["content"])
            data_cn = handle_api_result(result["content"], domain)
            return data_cn
    except:
        traceback.print_exc()
    return None


def handle_api_result(content, domain):
    try:
        pv = content
        info = pv.split('*')

        page_view = []
        for i in xrange(0, len(info)):
            if i > 7 and i < 16:
                page_view.append(info[i])

        result = {
            "page_view": page_view,
        }
        #logger.info(result)
        return result
    except:
        traceback.print_exc()
    return None


def run():
    global DOMAINS
    crawler_com = AlexaComCrawler()
    crawler_cn = AlexaCnCrawler()

    while True:
        if len(DOMAINS) ==0:
            return
        domain = DOMAINS.pop(0)

        dt = datetime.date.today()
        today = datetime.datetime(dt.year, dt.month, dt.day)
        r = alexa_collection.find_one(({"domain": domain, "date": today}))
        if r is not None:
            continue

        url = "https://www.alexa.com/siteinfo/%s" % domain
        max_retry = 0
        data_com = None
        while True:
            result = crawler_com.crawl(url)
            if result['get'] == 'success':
                #logger.info(result["content"])
                data_com = handle_alexa_com_result(result["content"], domain)
                if data_com:
                    break
            max_retry += 1
            if max_retry > 50:
                break

        # url = "http://www.alexa.cn/index.php?url=%s" % domain
        # while True:
        #     result = crawler_com.crawl(url)
        #     if result['get'] == 'success':
        #         #logger.info(result["content"])
        #         data_cn = handle_alexa_cn_result(result["content"], domain, crawler_cn)
        #         if data_cn:
        #             break
        #     else:
        #         continue
        if data_com is not None:
            data = {
                'date': today,
                'domain': domain,
                'global_rank': data_com["global_rank"],
                'country_rank': data_com["country_rank"],
                'search_visits': data_com["search_visits"],
                'global_rank_value': data_com["global_rank_value"],
                'country_rank_value': data_com["country_rank_value"],
                'search_visits_value': data_com["search_visits_value"],
                'page_view': [],
                'parser': 'wait'
            }
            logger.info(data)
            r = alexa_collection.find_one({"domain": domain, "date": today})
            if r is None:
                alexa_collection.insert_one(data)
            else:
                alexa_collection.update_one({"_id": r["_id"]}, {'$set': data})


if __name__ == "__main__":
    concurrent = 30
    logger.info("Start...")
    start = 0
    while True:
        conn = db.connect_torndb_proxy()
        apps = conn.query("select * from artifact where type=4010 and domain is not null and (active is null or active='Y') and id>%s order by id limit 5000", start)
        # apps = conn.query("select * from artifact where id=457011")
        conn.close()

        if len(apps) <= 0:
            logger.info("Finish.")
            break

        for app in apps:
            if app["id"] > start:
                start = app["id"]
            if app["domain"].strip() == "":
                continue
            domain = app["domain"].strip()
            DOMAINS.append(domain)

        threads = [gevent.spawn(run) for i in xrange(concurrent)]
        gevent.joinall(threads)

        # break
