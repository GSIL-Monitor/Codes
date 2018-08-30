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
loghelper.init_logger("eastmoney_report2", stream=True)
logger = loghelper.get_logger("eastmoney_report2")



class esCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        try:
            logger.info(content)
            j = json.loads(content)
            if j.has_key("IsSuccess") is True:
                return True
            else:
                return False
        except Exception, ex:
            # logger.info(Exception, ":", ex)
            return False



def crawler_rp(nurl, nctitle, ndate, sourceId, source):
    filelink = nurl
    if filelink is not None and filelink.find("pdf") >= 0:
        fileTime = extract.extracttime(ndate)

        content = {
            'stockExchangeId': 1,
            'source': source,
            'stockSymbol': str(sourceId),
            'title': nctitle,
            'link': filelink,
            "date": fileTime - datetime.timedelta(hours=8),
            'createTime': fileTime - datetime.timedelta(hours=8),
        }
        logger.info(json.dumps(content, ensure_ascii=False, cls=util.CJsonEncoder))
        mongo = db.connect_mongo()
        collection = mongo.stock.announcement
        collection.insert(content)
        mongo.close()
        #

def process(content, sourceId, source, key):
    j = json.loads(content)
    infos = j["result"]
    mongo = db.connect_mongo()

    collection = mongo.stock.announcement
    for info in infos:
        ntitle = info["title"]
        ndate = info["date"].replace("T", " ")
        fileTime = extract.extracttime(ndate)

        nurl = info["attachUrl"]
        cleantitle = "[临时公告]"+ ntitle
        cleantitle1 = "[定期报告]" + ntitle
        cleantitle2 = "[临时报告]" + ntitle
        logger.info("%s-%s-%s", ntitle,cleantitle,ndate)
        if fileTime > datetime.datetime(2017, 01, 11):
            logger.info("******we have")
            continue
        item = collection.find_one({"title": {'$in':[cleantitle1,cleantitle2,cleantitle]}})
        item1 = collection.find_one({"title": ntitle})
        if item is not None or item1 is not None:
            logger.info("******already exists")
        else:
            logger.info("******missing, get it")
            crawler_rp(nurl,cleantitle,ndate,sourceId,source)


    if j.has_key("TotalPage") and j["TotalPage"] > key:
        cnt = 1
    else:
        cnt = 0
    mongo.close()

    return cnt



def run(crawler, sourceId, source):
    key = 1
    while True:

        url = 'http://xinsanban.eastmoney.com/api/Article/GetGGListData?nrType=F013&securitycodes=%s.OC&text=&date=&page=%s&pagesize=20&sortType=&sortRule=1' % (sourceId, key)
        # data = '{"code":"%s","part":{"brief":"{brief}"}}' % sourceId
        headers = {"Accept": "application/json, text/javascript, */*; q=0.01"}

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
        collection_neeq = mongo.stock.neeq
        neeqstocks = list(collection_neeq.find({"processStatus": {"$in": [2, 3]}},{"sourceId":1}))

        for stock in neeqstocks:
            # run(crawler, "835413", 13400)
            # break
            cnt2 = run(crawler, stock["sourceId"], 13400)


        logger.info("eastmoney end.", )
        mongo.close()
        break

if __name__ == "__main__":
    start_run()