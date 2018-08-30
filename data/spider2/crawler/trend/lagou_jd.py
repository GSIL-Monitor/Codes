# -*- coding: utf-8 -*-
import os, sys,random, time
import datetime
import urllib2
import urllib
import json
import httplib
import socksa
import socket
import cookielib
import pymongo
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config, util
import loghelper, extract

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/recruit/lagou'))
import lagou_job_parser_2

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("crawler_jd", stream=True)
logger = loghelper.get_logger("crawler_jd")
cnt = 0
SJ=[]

#mongo
mongo = db.connect_mongo()
collection_job = mongo.job.job
collection_company = mongo.job.company



class LagouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("访问验证") >= 0:
            return False
        if title.find("找工作-互联网招聘求职网-拉勾网") >= 0:
            return False
        if title.find("拉勾网") >= 0:
            return True
        #logger.info(content)
        return False



def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 3:
        return False
    if temp[0].strip() == "找工作":
        return False
    return True




def save_job_mongo(sid, contents, companyId):
    global cnt
    jobs = list(collection_job.find({"source":13050, "sourceId": sid}))
    if len(jobs) > 0:
        for job in jobs:
            collection_job.update_one({"_id": job["_id"]},
                                          {'$set': {"jdChecked":True,"contents": contents}})
            if companyId is not None and (job.has_key("recruit_company_id") is False or job["recruit_company_id"] == ""):
                # logger.info("herehrerhe**********")
                company = collection_company.find_one({"source":13050, "sourceId":str(companyId)})
                if company is None:
                    company = collection_company.find_one({"source": 13050, "sourceId": int(companyId)})
                if company is not None:
                    collection_job.update_one({"_id": job["_id"]},
                                              {"$set": {"recruit_company_id": str(company["_id"])}})
                    cnt += 1
                    logger.info("***************populate %s for source job: %s", cnt, sid)




def process(key, content, url):
    #logger.info(content)
    dcontents = []
    companyId = None
    if has_content(content):
        d = pq((html.fromstring(content.decode("utf-8"))))
        article = d('dl#job_detail.job_detail').html()
        # # logger.info(article)
        contents = extract.extractContents(url, article, document=False)
        rank = 1
        over = False
        for c in contents:
            if c["data"].find("职位发布者") >= 0 or over is True:
                break
            if c["data"].find("查看地图") >= 0:
                c["data"] = c["data"].replace("查看地图", "")
                over = True
            if c["type"] == "text":
                dc = {
                    "rank": rank,
                    "content": c["data"],
                    "image": "",
                    "image_src": "",
                }
            else:

                dc = {
                    "rank": rank,
                    "content": "",
                    "image": "",
                    "image_src": c["data"],
                }

            # logger.info(c["data"])
            dcontents.append(dc)
            rank += 1
        companyId = d('input#companyid').attr("value")
        # logger.info("companyId: %s",companyId)
        save_job_mongo(key,dcontents, companyId)

def run(crawler):
    while True:
        if len(SJ) == 0:
            return
        info = SJ.pop(0)
        key = info["sourceId"]
        url = "https://www.lagou.com/jobs/%s.html" % info["sourceId"]
        logger.info(url)
        retry_times = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success' and result["redirect_url"] == url:
                #logger.info(result["content"])
                try:
                    process(key, result['content'], url)
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'redirect':
                logger.info("Redirect: %s", result["url"])
                pass

            retry_times += 1
            if retry_times > 13:
                break
                #break



def start_run(concurrent_num):
    while True:
        logger.info("Lagou job descripition start.....")
        dt = datetime.date.today()


        sjobs = list(collection_job.find({"source":13050,"jdChecked": None}).limit(3000))
        # sjobs = [collection_job.find_one({"source":13050, "sourceId": 1255664})]

        for job in sjobs:

            if job.has_key('sourceId') is False or job["sourceId"] is None:
                # collection_job.update_one({"_id": job["_id"]}, {"$set": {"jdContents": []}})
                pass

            else:

                logger.info("job sourceId %s", job['sourceId'])

                info ={
                    "sourceId" : job["sourceId"],
                    "id": job["_id"],
                }
                SJ.append(info)
            collection_job.update_one({"_id": job["_id"]},{"$set":{"jdChecked":True, "contents":[]}})
        #run(g, LagouCrawler())
        threads = [gevent.spawn(run, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou has finished")
        # exit()

        if len(sjobs) == 0:

            logger.info("Lagou job end...")
            gevent.sleep(30 * 60)
            # exit()

        #break

if __name__ == "__main__":
    start_run(15)