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
loghelper.init_logger("qtimg_desc", stream=True)
logger = loghelper.get_logger("qtimg_desc")



class meCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):

        code = url.replace("sh","sz").split("sz")[-1]
        if content.find(code) >= 0:
            # return True
            c = content.decode("gbk", "ignore")
            items = c.split("~")
            if len(items) >= 47:
                return True
        # logger.info(code)
        # logger.info(content)
        return False

def process(content, sourceId, source, t):
    cnt = 0
    # logger.info(content)
    # logger.info(content.decode("gbk", "ignore"))
    se = 0
    if source == 13401:
        se = 2
    elif source == 13402:
        se = 3
    c = content.decode("gbk", "ignore")
    items = c.split("~")
    stockName = items[1]
    stockCode = items[2]
    price = items[3]
    preClosePrice = items[4]
    openPrice = items[5]
    PE = items[39]
    investMarketValue = items[44]
    marketValue = items[45]
    PB = items[46]

    logger.info("%s-%s-%s-%s-%s-%s-%s-%s-%s", stockName,stockCode,price,preClosePrice,openPrice,PE,
                investMarketValue,marketValue,PB)
    dt = datetime.datetime.today()
    datestr = datetime.datetime.strftime(dt, '%Y-%m-%d')
    item = {
        "type": t,
        "typeDesc": "盘后" if t == 2 else "盘中",
        "stockName": stockName,
        "stockSymbol": stockCode,
        "stockExchangeId": se,
        "price": float(price),
        "preClosePrice": float(preClosePrice),
        "openPrice": float(openPrice),
        "PE": float(PE),
        "investMarketValue": float(investMarketValue),
        "marketValue": float(marketValue),
        "PB": float(PB),
        "date": datetime.datetime.strptime(datestr, "%Y-%m-%d"),
        "dateStr": datestr,
        "createTime": datetime.datetime.now()

    }
    # logger.info(type(t))
    # logger.info(type(datestr))
    mongo = db.connect_mongo()
    collection = mongo.stock.dailyData

    if collection.find_one({"stockExchangeId":item["stockExchangeId"], "stockSymbol": item["stockSymbol"],
                            "type": item["type"], "dateStr": item["dateStr"]}) is None:

        collection.insert(item)
        logger.info("saved")
        cnt = 1
    else:
        logger.info("Saving was wrong %s, %s", source, sourceId)
    mongo.close()
    return cnt


def run(crawler, sourceId, source, t):
    co = None
    if source == 13401:
        co = "sh"
    elif source == 13402:
        co = "sz"

    if co is None:
        return

    if source == 13402:
        sourceIdstr = str(sourceId)
        for i in range(0,6-len(str(sourceId))):
            sourceIdstr = "0" + sourceIdstr
        url = 'http://qt.gtimg.cn/q=%s%s' % (co,sourceIdstr)
    else:
        url = 'http://qt.gtimg.cn/q=%s%s' % (co,sourceId)

    cnt1 = 0
    retry = 0
    while True:
        result = crawler.crawl(url,agent=True)
        if result['get'] == 'success':
            try:
                # logger.info(result['content'], sourceId, source)
                cnt1 = process(result['content'], sourceId, source, t)
                if cnt1 > 0:
                    logger.info("saved")
                else:
                    logger.info("not saved")
                break
            except Exception,ex:
                logger.info(result['content'])
                logger.exception(ex)

            # break
        if retry > 40:
            break
        retry += 1
    return cnt1


#curl 'http://search.memect.cn/api/company' --data '{"code":"831277","part":{"brief":"{brief}"}}' -H 'Content-Type: application/json'


def start_run(ty):
    t = None
    if ty == "1":
        t = 1
    elif ty == "2":
        t = 2

    if t is None:
        return
    while True:
        crawler = meCrawler()
        logger.info("qtimg start")
        # run(crawler, 300050, 13402, t)
        # run(crawler, 300048, 13402, t)
        # run(crawler, 300047, 13402, t)
        # exit()
        mongo = db.connect_mongo()
        collection_sse = mongo.stock.sse
        collection_szse = mongo.stock.szse
        ssestocks = list(collection_sse.find({"processStatus": {"$in":[2,3]}}))
        szsestocks = list(collection_szse.find({"processStatus": {"$in":[2,3]}}))

        for stock in ssestocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(crawler, stock["sourceId"], 13401, t)

        logger.info("qtimg end.",)

        for stock in szsestocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(crawler, stock["sourceId"], 13402, t)


        logger.info("qtimg end.",)
        #
        #
        mongo.close()
        break
        # time.sleep(5*60)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        typ = sys.argv[1]
        start_run(typ)