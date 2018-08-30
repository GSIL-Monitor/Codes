# -*- coding: utf-8 -*-
import os, sys, urllib, httplib
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
loghelper.init_logger("cninfo_desc", stream=True)
logger = loghelper.get_logger("cninfo_desc")

cid = 'a0da4076c4134e86a0fd92743921c2c6'
cse = '8f25e35bf70c496ba724f48ddacdb613'
token = None

def gettoken(client_id, client_secret):
    url = 'http://api.before.com/api-cloud-platform/oauth2/token'  # api.before.com需要根据具体访问域名修改
    post_data = "grant_type=client_credentials&client_id=%s&client_secret=%s" % (client_id, client_secret)
    req = urllib.urlopen(url, post_data)
    responsecontent = req.read()
    responsedict = json.loads(responsecontent)
    token = responsedict["access_token"]
    return token

def apiget(scode, tokent):
    url = "http://apitest2.com/api/stock/p_stock2100?scode=%s&access_token=%s"  # apitest2.com需要根据具体访问域名修改
    conn = httplib.HTTPConnection("apitest2.com")
    conn.request(method="GET", url=url % (scode, tokent))
    response = conn.getresponse()
    rescontent = response.read()
    responsedict = json.loads(rescontent)
    resultcode = responsedict["resultcode"]
    print responsedict["resultmsg"], responsedict["resultcode"]
    if (responsedict["resultmsg"] == "success" and len(responsedict["records"]) >= 1):
        print responsedict["records"]  # 接收到的具体数据内容
    else:
        print 'no data'
    return resultcode

def apipost(scode, tokent):
    url = "http://apitest2.com/api/stock/p_stock2300"  # apitest2.com需要根据具体访问域名修改
    post_data = "scode=%s&access_token=%s" % (scode, tokent)
    req = urllib.urlopen(url, post_data)
    content = req.read()
    responsedict = json.loads(content)
    resultcode = responsedict["resultcode"]
    print responsedict["resultmsg"], responsedict["resultcode"]
    if (responsedict["resultmsg"] == "success" and
                responsedict["resultcode"] == 200 and len(responsedict["records"]) >= 1):
        return responsedict["records"]  # 接收到的具体数据内容
    else:
        # print 'no data'
        return []
    # return resultcode


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


def run(sourceId, source):
    global token
    if source == 13402:
        sourceIdstr = str(sourceId)
        for i in range(0,6-len(str(sourceId))):
            sourceIdstr = "0" + sourceIdstr

    else:
        sourceIdstr = str(sourceId)

    cnt1 = 0
    retry = 0
    while True:
        try:
            if token is None:
                token = gettoken(cid, cse)

            results = apipost(sourceIdstr,token)
            if len(results) > 0:
                for result in results:
                    pass

            else:
                pass


                # break
            if retry > 40:
                break
            retry += 1
        except:
            pass
    return cnt1


#curl 'http://search.memect.cn/api/company' --data '{"code":"831277","part":{"brief":"{brief}"}}' -H 'Content-Type: application/json'


def start_run():

    while True:
        logger.info("cninfo start")
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
            cnt2 = run(stock["sourceId"], 13401)

        logger.info("qtimg end.",)

        for stock in szsestocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(stock["sourceId"], 13402)


        logger.info("qtimg end.",)
        #
        #
        mongo.close()
        break
        # time.sleep(5*60)   #3 days

if __name__ == "__main__":
    start_run()