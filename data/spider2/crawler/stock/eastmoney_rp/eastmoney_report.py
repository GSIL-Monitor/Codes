# -*- coding: utf-8 -*-
import os, sys
from lxml import html
from pyquery import PyQuery as pq

import  json,time,datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,extract,util

#logger
loghelper.init_logger("eastmoney_report", stream=True)
logger = loghelper.get_logger("eastmoney_report")



class esCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content,redirect_url):
        if content.find("var") >= 0:
            r = "var  = (.*?);"

            result = util.re_get_result(r, content)
            (b,) = result
            logger.info(b)
            try:
                c = b.decode("gbk", "ignore")
                j = json.loads(c)
                if j.has_key("data") is True:
                    return True
                else:
                    return False
            except Exception,E:
                logger.info("here")
                logger.info(E)

        # logger.info(code)
        # logger.info(content)
        # elif redirect_url.find("pdf") >= 0:
        #     logger.info("get: %s", redirect_url)
        #     return True
        # return False

class espCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content,redirect_url):
        if redirect_url.find("pdf") >= 0:
            logger.info("get: %s", redirect_url)
            return True
        else:

            if content.find("</html>") == -1:
                return False
            # logger.info(content)
            d = pq(html.fromstring(content.decode("gbk","ignore")))
            title = d('head> title').text().strip()
            logger.info("title: " + title + " " + url)

            if title.find("公告") >= 0:
                return True
        # logger.info(content)
        return False

espcralwer = espCrawler()
def crawler_rp(nurl, nctitle, ndate, sourceId, source):
    retry = 0
    while True:
        result = espcralwer.crawl(nurl, agent=True)
        if result['get'] == 'success':
            if result["redirect_url"].find("pdf") >= 0:
                logger.info("we got pdf : %s ",result["redirect_url"])
                fileTime = extract.extracttime(ndate.split("+")[0])
                content = {
                    'stockExchangeId': 2 if source == 13401 else 3,
                    'source': source,
                    'stockSymbol': str(sourceId),
                    'title': nctitle,
                    'link': result["redirect_url"],
                    "date": fileTime - datetime.timedelta(hours=8),
                    'createTime': fileTime - datetime.timedelta(hours=8),
                }

                mongo = db.connect_mongo()
                collection = mongo.stock.announcement
                collection.insert(content)
                mongo.close()
            else:
                try:
                    d = pq(html.fromstring(result["content"].decode('gbk', 'ignore')))
                    filelink = d('div.detail-header> h1> span> a').attr("href")
                    if filelink is not None and filelink.find("pdf") >= 0:
                        fileTime = extract.extracttime(ndate.split("+")[0])

                        content = {
                            'stockExchangeId': 2 if source == 13401 else 3,
                            'source': source,
                            'stockSymbol': str(sourceId),
                            'title': nctitle,
                            'link': filelink,
                            "date": fileTime - datetime.timedelta(hours=8),
                            'createTime': fileTime - datetime.timedelta(hours=8),
                        }

                        mongo = db.connect_mongo()
                        collection = mongo.stock.announcement
                        collection.insert(content)
                        mongo.close()
                        # exit()
                except Exception, ex:
                    logger.exception(ex)
            break

        retry += 1
        if retry > 8: break

def process(content, sourceId, source, key):
    r = "var  = (.*?);"

    result = util.re_get_result(r, content)
    (b,) = result
    logger.info(b)
    c = b.decode("gbk", "ignore")
    j = json.loads(c)
    infos = j["data"]
    mongo = db.connect_mongo()

    collection = mongo.stock.announcement
    for info in infos:
        ntitle = info["NOTICETITLE"]
        ndate = info["NOTICEDATE"]
        nurl = info["Url"]
        cleantitle = ntitle.replace(":","").replace(str(sourceId),"").strip()
        logger.info("%s-%s-%s", ntitle,cleantitle,ndate)

        item = collection.find_one({"title": cleantitle})
        item1 = collection.find_one({"title": ntitle})
        if item is not None or item1 is not None:
            logger.info("******already exists")
        else:
            logger.info("******missing, get it")
            crawler_rp(nurl,cleantitle,ndate,sourceId,source)


    if j.has_key("TotalCount") and j["TotalCount"] > (50 * key):
        cnt = 1
    else:
        cnt = 0
    mongo.close()

    return cnt



def run(crawler, sourceId, source):
    key = 1
    while True:

        url = 'http://data.eastmoney.com/notices/getdata.ashx?StockCode=%s&CodeType=1&PageIndex=%s&PageSize=50&SecNodeType=0&FirstNodeType=2' % (sourceId, key)
        # data = '{"code":"%s","part":{"brief":"{brief}"}}' % sourceId
        # headers = {"Content-Type": "application/json"}

        cnt1 = 0
        while True:
            result = crawler.crawl(url,agent=True)
            if result['get'] == 'success':
                try:
                    # logger.info(result['content'], sourceId, source)
                    cnt1 = process(result['content'], sourceId, source, key)

                except Exception,ex:
                    logger.exception(ex)

                break
        if cnt1 > 0:
            key += 1
        else:
            break


#curl 'http://search.memect.cn/api/company' --data '{"code":"831277","part":{"brief":"{brief}"}}' -H 'Content-Type: application/json'


def start_run():

    while True:
        crawler = esCrawler()
        logger.info("eastmoney start")
        # collection_sse = mongo.stock.sse
        # ssestocks = list(collection_sse.find({"processStatus": 0}).limit(100))
        #
        # for stock in ssestocks:
        #     # run(crawler, 603929, 13401)
        #     cnt2 = run(crawler, stock["sourceId"], 13401)
        #     if cnt2 >0:
        #         collection_sse.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": 1}})
        #     else:
        #         collection_sse.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": -1}})
        # logger.info("memect end.",)

        mongo = db.connect_mongo()
        collection_sse = mongo.stock.sse
        collection_szse = mongo.stock.szse
        ssestocks = list(collection_sse.find({"processStatus": {"$in": [2, 3]}},{"sourceId":1}))
        szsestocks = list(collection_szse.find({"processStatus": {"$in": [2, 3]}},{"sourceId":1}))

        for stock in ssestocks:
            # run(crawler, "601318", 13401)
            # break
            cnt2 = run(crawler, stock["sourceId"], 13401)

        for stock in szsestocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(crawler, stock["sourceId"], 13402)

        logger.info("eastmoney end.", )
        mongo.close()
        break

if __name__ == "__main__":
    start_run()