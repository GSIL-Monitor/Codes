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
import loghelper,db,extract

#logger
loghelper.init_logger("memect_desc", stream=True)
logger = loghelper.get_logger("memect_desc")



class meCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        try:
            logger.info(content)
            j = json.loads(content)
            if j.has_key("success") is True:
                return True
            else:
                return False
        except Exception, ex:
            # logger.info(Exception, ":", ex)
            return False


def process(content, sourceId, source):
    collection = None
    j = json.loads(content)
    # logger.info(j)
    infos = j["success"]["data"]
    cnt = 0
    if infos is None or infos.has_key("brief") is False:
        logger.info("%s,%s has no info %s", source, sourceId, content)
        return cnt
    mongo = db.connect_mongo()
    if source == 13401:
        collection = mongo.stock.sse
    elif source == 13400:
        collection = mongo.stock.neeq

    if collection is not None and collection.find_one({"sourceId": {"$in":[str(sourceId),sourceId]}}) is not None:
        collection.update_one({"sourceId": {"$in":[str(sourceId),sourceId]}}, {'$set': {"memectBrief": infos["brief"]}})
        logger.info("%s,%s has right info!!!!!!!", source, sourceId)
        cnt = 1
    else:
        logger.info("%s,%s has wrong info %s", source, sourceId, content)
    mongo.close()
    return cnt


def run(crawler, sourceId, source):

    url = 'http://search.memect.cn/api/company'
    data = '{"code":"%s","part":{"brief":"{brief}"}}' % sourceId
    headers = {"Content-Type": "application/json"}
    logger.info(data)
    cnt1 = 0
    while True:
        result = crawler.crawl(url,agent=True, headers=headers, postdata=data)
        if result['get'] == 'success':
            try:
                # logger.info(result['content'], sourceId, source)
                cnt1 = process(result['content'], sourceId, source)
                if cnt1 > 0:
                    logger.info("saved")
                else:
                    logger.info("not saved")
            except Exception,ex:
                logger.exception(ex)

            break
    return cnt1


#curl 'http://search.memect.cn/api/company' --data '{"code":"831277","part":{"brief":"{brief}"}}' -H 'Content-Type: application/json'


def start_run():

    while True:
        crawler = meCrawler()
        logger.info("memect start")
        mongo = db.connect_mongo()
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

        collection_neeq = mongo.stock.neeq
        neeqstocks = list(collection_neeq.find({"processStatus": 0}).limit(100))

        for stock in neeqstocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(crawler, stock["sourceId"], 13400)
            if cnt2 > 0:
                collection_neeq.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": 1}})
            else:
                collection_neeq.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": -1}})
        logger.info("memect end.", )

        mongo.close()
        time.sleep(2*60)   #3 days

if __name__ == "__main__":
    start_run()