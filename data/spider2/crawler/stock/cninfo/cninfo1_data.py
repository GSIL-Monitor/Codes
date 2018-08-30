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
loghelper.init_logger("cninfo", stream=True)
logger = loghelper.get_logger("cninfo")

rmap = [
    {
        "type": 1,
        "typeDesc":"资产负债表",
        "ue": "balancesheet",
    },
    {
        "type": 2,
        "typeDesc":"利润表",
        "ue": "incomestatements",
    },
    {
        "type": 3,
        "typeDesc":"现金流量表",
        "ue": "cashflow",
    },
]

freqtype = {
    0: "未知",
    1: "一季",
    2: "中期",
    3: "三季",
    4: "年度"
}

class meCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):

        code = url.replace("shmb","szcn").replace("szmb","szcn").replace("szsme","szcn").split("szcn")[-1].replace("html","")
        td = None
        if url.find("balancesheet") >= 0:
            td = "资产负债表"
        if url.find("incomestatements") >= 0:
            td = "利润表"
        if url.find("cashflow") >= 0:
            td = "现金流量表"

        c = content.decode("gbk", "ignore")
        d = pq(html.fromstring(c))
        title = d('head> title').text().strip()
        if title.find("error") >= 0:
            return True

        if content.find(code) >= 0 and td is not None:
            # return True
            # c = content.decode("gbk", "ignore")
            # d = pq(html.fromstring(c))
            right_title = d('div.zx_right_title').text()
            if right_title is not None and right_title.find(td) >= 0:
                return True

        return False

def process(content, sourceIdstr, source, tmap):
    se = 0
    if source == 13401:
        se = 2
    elif source == 13402:
        se = 3
    date = None
    datestr = None
    freq = 0
    fdata = []
    c = content.decode("gbk", "ignore")
    d = pq(html.fromstring(c))
    for tr in d('div.clear> table> tr'):
        tr_html = pq(tr)
        tds = tr_html('td')
        if len(tds) != 4:
            logger.info(tr)
            continue
        if pq(tds[0]).text() == "科目":
            if tmap["type"] == 1:
                datestr = pq(tds[1]).text().strip()
                date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
                if datestr.find("-03-31") >= 0:
                    freq = 1
                elif datestr.find("-06-30") >= 0:
                    freq = 2
                elif datestr.find("-12-31") >= 0:
                    freq = 4
                elif datestr.find("-09-30") >= 0:
                    freq = 3

            if tmap["type"] in [2,3]:
                datestr_a = pq(tds[1]).text().strip()
                if datestr_a.find("1-3月") >= 0:
                    freq = 1
                    datestr = datestr_a.replace("年1-3月", "-03-31")
                elif datestr_a.find("1-6月") >= 0:
                    freq = 2
                    datestr = datestr_a.replace("年1-6月", "-06-30")
                elif datestr_a.find("年度") >= 0:
                    freq = 4
                    datestr = datestr_a.replace("年度", "-12-31")
                elif datestr_a.find("1-9月") >= 0:
                    freq = 3
                    datestr = datestr_a.replace("年1-9月","-09-30")
                date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
            logger.info("%s/%s", datestr, freqtype[freq])

            if freq is not None and datestr is not None:
                continue

        if pq(tds[0]).text() is not None and pq(tds[0]).text().strip() != "":
            itemDesc = pq(tds[0]).text().strip()
            if pq(tds[1]).text() is not None and pq(tds[1]).text().strip() != "":
                try:
                    itemValue = float(pq(tds[1]).text().strip().replace(",",""))
                except:
                    logger.info("not float")
                    itemValue = pq(tds[1]).text().strip()
            else:
                itemValue = None
            logger.info("%s --- %s", itemDesc, itemValue)

            fdata.append({"itemDesc": itemDesc, "itemValue": itemValue})

    for tr in d('div.clear> table> tr'):
        tr_html = pq(tr)
        tds = tr_html('td')
        if len(tds) != 4:
            logger.info(tr)
            continue
        if pq(tds[0]).text() == "科目":
            # if tmap["type"] == 1:
            #     datestr = pq(tds[1]).text().strip()
            #     date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
            #     if datestr.find("-03-31") >= 0:
            #         freq = 1
            #     elif datestr.find("-06-30") >= 0:
            #         freq = 2
            #     elif datestr.find("-12-31") >= 0:
            #         freq = 4
            #     elif datestr.find("-09-30") >= 0:
            #         freq = 3
            # logger.info("%s/%s", datestr, freqtype[freq])
            #
            # if freq is not None and datestr is not None:
            #     continue
            continue

        if pq(tds[2]).text() is not None and pq(tds[2]).text().strip() != "":
            itemDesc = pq(tds[2]).text().strip()
            if pq(tds[3]).text() is not None and pq(tds[3]).text().strip() != "":
                try:
                    itemValue = float(pq(tds[3]).text().strip().replace(",",""))
                except:
                    logger.info("not float")
                    itemValue = pq(tds[3]).text().strip()
            else:
                itemValue = None
            logger.info("%s --- %s", itemDesc, itemValue)
            fdata.append({"itemDesc": itemDesc, "itemValue": itemValue})

    if freq is None and datestr is None:
        return 0

    item = {
        "type": tmap["type"],
        "typeDesc": tmap["typeDesc"],
        "stockSymbol": sourceIdstr,
        "stockExchangeId": se,
        "freq": freq,
        "freqDesc": freqtype[freq],
        "date": datetime.datetime.strptime(datestr, "%Y-%m-%d"),
        "dateStr": datestr,
        "createTime": datetime.datetime.now(),
        "financeData": fdata

    }
    # # logger.info(type(t))
    # # logger.info(type(datestr))
    mongo = db.connect_mongo()
    collection = mongo.stock.finance
    citem = collection.find_one({"stockExchangeId":item["stockExchangeId"], "stockSymbol": item["stockSymbol"],
                            "type": item["type"], "dateStr": item["dateStr"]})
    if citem is None:

        collection.insert(item)
        logger.info("saved")

    else:
        id = citem.pop("_id")
        if item["financeData"] != citem["financeData"]:
            logger.info("Saving new data")
            collection.update_one({"_id":id},{"$set":item})
        else:
            logger.info("same data, not saving")
    mongo.close()
    return 1


def run(crawler, sourceId, source):
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
        if sourceIdstr.startswith("002"):
            urlcode = 'szsme'+sourceIdstr
        elif sourceIdstr.startswith("30"):
            urlcode = 'szcn'+ sourceIdstr
        else:
            urlcode = 'szmb'+sourceIdstr
    else:
        sourceIdstr = str(sourceId)
        urlcode = "shmb"+ sourceIdstr

    for tt in rmap:
        retry = 0
        url = "http://www.cninfo.com.cn/information/%s/%s.html" % (tt["ue"], urlcode)
        while True:
            result = crawler.crawl(url,agent=True)
            if result['get'] == 'success':
                try:
                    # logger.info(result['content'])
                    cnt1 = process(result['content'], sourceIdstr, source, tt)
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
    return 1


#curl 'http://search.memect.cn/api/company' --data '{"code":"831277","part":{"brief":"{brief}"}}' -H 'Content-Type: application/json'


def start_run():

    while True:
        crawler = meCrawler()
        logger.info("cninfo start")
        # run(crawler, 300050, 13402)
        # run(crawler, 600000, 13401)
        # # run(crawler, 300047, 13402, t)
        # exit()
        mongo = db.connect_mongo()
        collection_sse = mongo.stock.sse
        collection_szse = mongo.stock.szse
        ssestocks = list(collection_sse.find({"processStatus": {"$in":[2,3]}}))
        szsestocks = list(collection_szse.find({"processStatus": {"$in":[2,3]}}))

        # for stock in ssestocks:
        #     # run(crawler, 603929, 13401)
        #     cnt2 = run(crawler, stock["sourceId"], 13401)


        for stock in szsestocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(crawler, stock["sourceId"], 13402)


        logger.info("cninfo end.",)
        #
        #
        mongo.close()
        break
        # time.sleep(5*60)   #3 days

if __name__ == "__main__":

    start_run()