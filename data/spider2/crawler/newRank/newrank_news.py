# -*- coding: utf-8 -*-
import os, sys,datetime, time
import random, math
import urllib
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import subprocess
import threading
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../news'))
import Wechatcrawler

#logger
loghelper.init_logger("crawler_newrank", stream=True)
logger = loghelper.get_logger("crawler_newrank")


class nrCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现
    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                logger.info(j)
            except:
                return False

            if j.has_key("success") is True and j["success"] == True and\
                j.has_key("value") and isinstance(j["value"], dict):
                return True

        return False

class wechat(Wechatcrawler.NewsDownloader):
    def __init__(self, TYPE=60001, SOURCE=13840, RETRY=10):
        Wechatcrawler.NewsDownloader.__init__(self, TYPE = TYPE, SOURCE=SOURCE, RETRY=RETRY)



def get():
    crawler =  nrCrawler()
    wechatcrawler = Wechatcrawler.WechatCrawler()
    wechatprocess = wechat()
    mongo = db.connect_mongo()
    collection = mongo.raw.new_rank
    accounts = list(collection.find({}))
    for account in accounts:

        if account.has_key("uuid") and account.has_key("nonce") and account.has_key("xyz") and \
            account["uuid"] is not None and account["nonce"] is not None and account["xyz"] is not None:

            # link = "http://www.newrank.cn/xdnphb/detail/getAccountArticle?flag=true&uuid=%s&nonce=%s&xyz=%s" % (
            #     account["uuid"], account["nonce"], account["xyz"])
            link = "https://www.newrank.cn/xdnphb/detail/getAccountArticle"
            pdata = {
                "flag": "true",
                "uuid": account["uuid"],
                "nonce": account["nonce"],
                "xyz": account["xyz"]

            }
            data = urllib.urlencode(pdata)
            logger.info("post: %s", data)
            cnt = get_article_links(crawler, data, link, account["wechatId"], account["name"], wechatcrawler, wechatprocess)

            if cnt > 0 and account["checked"]  is None:
                collection.update_one({"_id": account["_id"]},{"$set": {"checked": True}})
    mongo.close()


def get_article_links(crawler, data, nr_link, wechatId, wechatName, wechatcrawler, wechatprocess):
    cnt  = 0
    while True:
        headers = {"Cookie": 'token=38015FF097133FCD6C2E8BD112BD1826'}
        result = crawler.crawl(nr_link, postdata=data, agent=True, headers=headers)
        if result['get'] == 'success':
            # logger.info(result["redirect_url"])
            try:
                cnt = process(result['content'], wechatId, wechatName, wechatcrawler, wechatprocess)
            except Exception, ex:
                logger.info(result["content"])
                logger.exception(ex)
            break
    return cnt

def process(content, wechatId, wechatName, wechatcrawler, wechatprocess):
    j = json.loads(content)
    infos = j["value"]["lastestArticle"]
    logger.info("Got %s news", len(infos))
    cnt = 0
    download_crawler = download.DownloadCrawler(use_proxy=False)
    if len(infos) == 0:
        return cnt
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    for info in infos:

            wexinlink = info["url"]
            readNum = int(info["clicksCount"])
            likeNum = int(info["likeCount"])
            title = info["title"]
            try:
                publicTime = datetime.datetime.strptime(info["publicTime"],"%Y-%m-%d %H:%M:%S")- datetime.timedelta(hours=8)
            except:
                publicTime = datetime.datetime.now() - datetime.timedelta(hours=8)

            logger.info("link: %s", wexinlink)
            logger.info("article by: %s, read: %s, like: %s", wechatName, readNum, likeNum)

            item = collection_news.find_one({"link": wexinlink})
            item2 = collection_news.find_one({"title": title})

            if item is None and item2 is None:
                if wexinlink.find("https") == -1:
                    wexinlink = wexinlink.replace("http","https")
                dnews = wechatprocess.crawler_news(wechatcrawler, wexinlink, download_crawler, wechatId='微信公众号')
                # for a in dnews:
                #     logger.info("%s _> %s", a, dnews[a])
                dnews["date"] = publicTime
                dnews["clicksCount"] = readNum
                dnews["likeCount"] = likeNum
                # dnews["wechatId"] = wechatId
                dnews["wechatName"] = wechatName
                dnews["processStatus"] = 0
                dnews["imgChecked"] = True
                # dnews["sectors"] = [20]

                if dnews["result"] == 'SUCCESS' and len(dnews["contents"])>=1 and dnews["title"] is not None and \
                        dnews["title"].strip() != "":
                    dnews.pop('result')
                    try:
                        collection_news.insert(dnews)
                        cnt += 1
                    except Exception, e:
                        logger.info(e)
                        pass
            else:
                if item is not None and item.has_key("source") is True and item["source"] == 13840:
                    logger.info("Update click/update: %s/%s", readNum, likeNum)
                    collection_news.update_one({"_id": item["_id"]}, {"$set": {"clicksCount": readNum, "likeCount": likeNum}})

    mongo.close()

    return cnt


if __name__ == "__main__":
    while True:
        get()
        time.sleep(200*60)
