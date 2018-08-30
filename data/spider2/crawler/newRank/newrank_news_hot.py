# -*- coding: utf-8 -*-
import os, sys,datetime, time
import random, math
import urllib
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading
import gen_par
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../news'))
import Wechatcrawler

#logger
loghelper.init_logger("crawler_newrank_hot", stream=True)
logger = loghelper.get_logger("crawler_newrank_hot")


columns = [
    {"rank_name": "科技", "rank_name_group": "资讯"},
    {"rank_name": "创业", "rank_name_group": "资讯"},
]

class nrCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现
    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                # logger.info(j)
            except:
                return False

            if j.has_key("success") is True and j["success"] == True:
                return True

        return False

class wechat(Wechatcrawler.NewsDownloader):
    def __init__(self, TYPE=60001, SOURCE=13841, RETRY=20):
        Wechatcrawler.NewsDownloader.__init__(self, TYPE = TYPE, SOURCE=SOURCE, RETRY=RETRY)



def get():
    crawler =  nrCrawler()
    wechatcrawler = Wechatcrawler.WechatCrawler()
    wechatprocess = wechat()
    mongo = db.connect_mongo()

    for column in columns:
        for nday in [1,2]:
            date = datetime.date.today() - datetime.timedelta(days=nday)
            nonce = gen_par.gen_nonce()
            xyz =  gen_par.gen_xyz_hot(str(date), column["rank_name"], column["rank_name_group"], nonce)
            logger.info("date: %s, nonce: %s, xyz: %s", str(date), nonce, xyz)
            link = "http://www.newrank.cn/xdnphb/list/day/article"
            pdata = {
                "end": date,
                "rank_name": column["rank_name"],
                "rank_name_group": column["rank_name_group"],
                "start": date,
                "nonce": nonce,
                "xyz": xyz

            }
            data = urllib.urlencode(pdata)
            cnt = get_article_links(crawler, data, link, wechatcrawler, wechatprocess)


    mongo.close()


def get_article_links(crawler, data, nr_link, wechatcrawler, wechatprocess):
    cnt  = 0
    while True:
        result = crawler.crawl(nr_link, postdata=data, agent=True)
        if result['get'] == 'success':
            logger.info(result['content'])
            # logger.info(result["redirect_url"])
            try:
                cnt = process(result['content'], wechatcrawler, wechatprocess)
            except Exception, ex:
                logger.exception(ex)
            break
    return cnt

def process(content, wechatcrawler, wechatprocess):
    j = json.loads(content)
    infos = j["value"]["datas"]
    logger.info("Got %s news", len(infos))
    cnt = 0
    download_crawler = download.DownloadCrawler(use_proxy=False)
    if len(infos) == 0:
        return cnt
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    for info in infos:

            wexinlink = info["url"]
            readNum = int(info["clicks_count"])
            likeNum = int(info["like_count"])
            title = info["title"]
            try:
                publicTime = datetime.datetime.strptime(info["public_time"],"%Y-%m-%d %H:%M:%S.0")- datetime.timedelta(hours=8)
            except:
                publicTime = datetime.datetime.now() - datetime.timedelta(hours=8)

            logger.info("link: %s", wexinlink)
            logger.info("article : %s, read: %s, like: %s", title, readNum, likeNum)

            item = collection_news.find_one({"link": wexinlink})
            # item2 = collection_news.find_one({"title": title})

            if item is None:
                dnews = wechatprocess.crawler_news(wechatcrawler, wexinlink, download_crawler, wechatId="微信公众号")
                # for a in dnews:
                #     logger.info("%s _> %s", a, dnews[a])
                dnews["date"] = publicTime
                dnews["clicksCount"] = readNum
                dnews["likeCount"] = likeNum
                # dnews["wechatId"] = wechatId
                # dnews["wechatName"] = wechatName
                dnews["processStatus"] = 0
                dnews["imgChecked"] = True
                # dnews["sectors"] = [20]

                if dnews["result"] == 'SUCCESS' and len(dnews["contents"])>=1:
                    dnews.pop('result')
                    try:
                        collection_news.insert(dnews)
                        cnt += 1
                    except Exception, e:
                        logger.info(e)
                        pass
            else:
                if item["source"] == 13841:
                    logger.info("Update click/update: %s/%s", readNum, likeNum)
                    collection_news.update_one({"_id": item["_id"]}, {"$set": {"clicksCount": readNum, "likeCount": likeNum}})

    mongo.close()

    return cnt


if __name__ == "__main__":
    while True:
        get()
        time.sleep(60*60)
