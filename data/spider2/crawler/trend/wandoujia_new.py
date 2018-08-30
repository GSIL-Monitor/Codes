# -*- coding: utf-8 -*-
import sys, os
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

from pyquery import PyQuery as pq

from lxml import html
import datetime, time
import json
import urllib
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config
import util
import proxy_pool
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import crawler_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import market.wandoujia as wandoujia_parser

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler


#logger
loghelper.init_logger("wandoujia_trends", stream=True)
logger = loghelper.get_logger("wandoujia_trends")

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.android

collection_market = mongo.market.android_market #TODO

cnt = 0
total = 0
TYPE = 16030
SC=[]

headers = {}
headers[
    "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"


class LagouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        #exception
        if content.find("com.vivekwarde.onegbrambooster") > 0:
            return True

        if content.find("com.vivekwarde.threegbrambooster") > 0:
            return True

        d = pq(html.fromstring(content.decode("utf-8", "ignore")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("豌豆荚") >= 0:
            return True
        #exception
        if title.find("豌豆家") > 0:
            return True

        if title.find("该应用已下架") > 0:
            return True

        return False



def has_content(content, apkname):
    # d = pq(html.fromstring(content.decode("utf-8")))
    # if content.find(u'很抱歉，您要访问的页面无法正常显示，可能是因为如下原因') >= 0:
    #     logger.info('404 for %s', apkname)
    #     return True
    # elif content.find(u'魅友评分') >= 0:
    #     return True
    # else:
    #     return False
    return True

def process(crawler, url, apkname, content):


    # try:
    #     # Parser data for newupdates:
    #     #logger.info("%s->%s", apkname, url)
    #     flyme_parser.process(None, url, apkname, content)
    #
    #     #html = unicode(response.body,encoding="utf-8",errors='replace')
    #
    #
    #     d = pq(html.fromstring(content.decode("utf-8")))
    #     download = d('span:contains("下      载：")+ div').text().strip()
    #     score = d('span:contains("魅友评分")+ div > div').attr('data-num').strip()
    #
    #     score = float(score)/10
    #     download = float(download)
    #     crawler_util.save_download(apkname,TYPE, download,score)
    #     logger.info("apkname=%s, download=%s, score=%s" % (apkname, download,score))
    #
    # except:
    #     traceback.print_exc()
    try:
        # Parser data for newupdates:
        # logger.info(html)
        wandoujia_parser.process(None, url, apkname, content)

        html = unicode(content, encoding="utf-8", errors='replace')
        d = pq(html)
        download = None
        try:
            dnum = d("i[itemprop='interactionCount']").attr("content").split(":")[1]

            try:
                download = int(dnum)
            except:
                if dnum.find("万") >= 0:
                    download = int(float(dnum.replace("万", "").strip()) * 10000)
                elif dnum.find("亿") >= 0:
                    download = int(float(dnum.replace("亿", "").strip()) * 10000 * 10000)
                else:
                    logger.info("********download :%s cannot get", dnum)

            # score = int(d("meta[itemprop='ratingValue']").attr("content"))
            score = None
            comment = int(d("a.comment-open> i").text())
        except:
            score = None; comment = None

        if download is not None:
            crawler_util.save_download_comment(apkname, TYPE, download, score, comment)
            logger.info("apkname=%s, download=%s, score=%s, comment=%s"
                        % (apkname, download, score, comment))

    except:
        logger.info("wrong: %s", url)
        traceback.print_exc()


        #exit(0)


def run(crawler):
    while True:
        if len(SC) == 0:
            return
        info = SC.pop(0)
        url = info["link"]
        apkname = info["apkname"]
        retry_times = 0
        while True:
            result = crawler.crawl(url, agent=True, headers=headers)
            if result['get'] == 'success':
                # logger.info(result["content"])
                if has_content(result["content"], apkname):
                    try:
                        process(crawler, url, apkname, result['content'])
                    except Exception, ex:
                        logger.exception(ex)
                    break
            retry_times += 1
            if retry_times > 30:
                break



def begin(concurrent_num):
    global total, cnt

    flag = False
    while flag is False:
        conn = db.connect_torndb_proxy()
        apps = conn.query(
            "select * from artifact where type=4050 and (active is null or active='Y') and id>%s order by id limit 1000",
            cnt)
        # apps = conn.query("select * from artifact where type=4050 and domain ='com.yixia.videoeditor' and id>%s order by id limit 1", cnt)
        # apps = conn.query("select * from artifact where id>371210 and id<371250")

        conn.close()

        if len(apps) <= 0:
           break


        for app in apps:
            # logger.info(app["name"])
            if app["id"] > cnt:
                cnt = app["id"]

            if app["domain"] is None or app["domain"].strip() == "":
                continue

            domain = app["domain"].strip()
            app["domain"] = domain
            dt = datetime.date.today()
            today = datetime.datetime(dt.year, dt.month, dt.day)

            m = collection_market.find_one({"appmarket":TYPE, "apkname": domain})
            if m is None:
                continue

            r = collection.find_one(({"appmarket":TYPE, "apkname": domain, "date": today}))
            if r is not None:
                # pass
                continue
            logger.info(app["name"])
            logger.info(m["link"])
            info = {
                "link": m["link"].replace("http:","https:"),
                "apkname": app["domain"],
            }
            SC.append(info)

        threads = [gevent.spawn(run, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)


if __name__ == "__main__":
    while True:
        begin(8)
        break