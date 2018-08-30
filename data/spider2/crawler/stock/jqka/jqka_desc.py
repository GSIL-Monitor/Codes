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
loghelper.init_logger("jqka_desc", stream=True)
logger = loghelper.get_logger("jqka_desc")



class meCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("gbk")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("同花顺") >= 0:
            return True
        # logger.info(content)
        return False

def process(content, sourceId, source):
    collection = None
    # j = json.loads(content)
    # # logger.info(j)
    # infos = j["success"]["data"]
    cnt = 0
    d = pq(html.fromstring(content.decode("gbk")))
    title = d('head> title').text().strip()
    (brief, desc, chairman) = (None,None,None)
    if title.find(str(sourceId))>0 :
        trs = d('div.m_tab_content2> table> tbody> tr')
        for tr in trs:
            d1 = pq(tr)
            strong = d1('strong.hltip').eq(0).text()
            if strong.find("主营业务") >= 0:
                brief = d1('span').eq(0).text()
            elif strong.find("董事长") >= 0:
                chairman = d1('span').eq(0).text()
            elif strong.find("公司简介") >= 0:
                desc = d1('p.tip').eq(0).text()
                if desc.find("查看全部")>=0:
                    desc = d1('p.tip').eq(1).text()

    logger.info("%s\n%s\n%s", brief,chairman, desc)

    if (desc is None or desc.strip() == "-") and (chairman is None or chairman.strip() == "-"):
        logger.info("%s,%s has no info", source, sourceId)
        # exit()
        return cnt

    # exit()
    if brief is not None and brief.strip() == "-": brief = None
    infos ={
        "brief": brief,
        "chairman": chairman,
        "desc": desc.replace("收起▲","").strip()
    }
    mongo = db.connect_mongo()
    if source == 13401:
        collection = mongo.stock.sse
    elif source == 13400:
        collection = mongo.stock.neeq
    elif source == 13402:
        collection = mongo.stock.szse

    if collection is not None and collection.find_one({"sourceId": {"$in":[str(sourceId),sourceId]}}) is not None:
        collection.update_one({"sourceId": {"$in":[str(sourceId),sourceId]}}, {'$set': {"jqkaBrief": infos}})
        logger.info("%s,%s has right info!!!!!!!", source, sourceId)
        cnt = 1
    else:
        logger.info("Saving was wrong %s, %s", source, sourceId)
    mongo.close()
    return cnt


def run(crawler, sourceId, source):
    if source == 13402:
        sourceIdstr = str(sourceId)
        for i in range(0,6-len(str(sourceId))):
            sourceIdstr = "0" + sourceIdstr
        url = 'http://basic.10jqka.com.cn/%s/company.html#stockpage' % sourceIdstr
    else:
        url = 'http://basic.10jqka.com.cn/%s/company.html#stockpage' % sourceId
    # data = '{"code":"%s","part":{"brief":"{brief}"}}' % sourceId
    # headers = {"Content-Type": "application/json"}
    # logger.info(data)
    cnt1 = 0
    retry = 0
    while True:
        result = crawler.crawl(url,agent=True)
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
        if retry > 40:
            break
        retry += 1
    return cnt1


#curl 'http://search.memect.cn/api/company' --data '{"code":"831277","part":{"brief":"{brief}"}}' -H 'Content-Type: application/json'


def start_run():

    while True:
        crawler = meCrawler()
        logger.info("jqka start")
        # run(crawler, 600000, 13401)
        # exit()
        mongo = db.connect_mongo()
        collection_sse = mongo.stock.sse
        collection_szse = mongo.stock.szse
        ssestocks = list(collection_sse.find({"processStatus": 0}).limit(100))
        szsestocks = list(collection_szse.find({"processStatus": 0}).limit(100))

        for stock in ssestocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(crawler, stock["sourceId"], 13401)
            if cnt2 >0:
                collection_sse.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": 1}})
            else:
                collection_sse.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": -1}})
        logger.info("jqka end.",)

        for stock in szsestocks:
            # run(crawler, 603929, 13401)
            cnt2 = run(crawler, stock["sourceId"], 13402)
            if cnt2 >0:
                collection_szse.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": 1}})
            else:
                collection_szse.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": -1}})
        logger.info("jqka end.",)

        collection_neeq = mongo.stock.neeq
        neeqstocks = list(collection_neeq.find({"processStatus": -1}).limit(100))

        for stock in neeqstocks:

            cnt2 = run(crawler, stock["sourceId"], 13400)
            if cnt2 > 0:
                collection_neeq.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": 1}})
            else:
                collection_neeq.update_one({"_id": stock["_id"]}, {'$set': {"processStatus": -2}})
        logger.info("jqka end.", )

        mongo.close()
        time.sleep(2*60)   #3 days

if __name__ == "__main__":
    start_run()