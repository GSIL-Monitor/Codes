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
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/recruit/lagou'))
import lagou_job_parser_2

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("crawler_lagou_job_2", stream=True)
logger = loghelper.get_logger("crawler_lagou_job_2")
cnt = 0
SC=[]

#mongo
# mongo = db.connect_mongo()
# collection = mongo.job.job
# collection_company = mongo.job.company



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


class LagouJobCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        if content.find('操作成功') == -1:
            logger.info(content)
            return False
        r = "companyId=(.*?)&pageSize"
        result = util.re_get_result(r, url)
        (id,) = result
        try:
            j = json.loads(content)
            rjobs = j['content']['data']['page']['result']
            if len(rjobs) == 0:
                logger.info("Failed due to 0 jobs under url: %s", url)
                return False
            if len(rjobs) > 0 and rjobs[0].has_key("companyId"):
                companyId = rjobs[0]["companyId"]
                logger.info("Url companyid: %s <-> lagou return companyId: %s", id, companyId)
                if str(companyId) != id:
                    logger.info("Failed due to different companyId: got: %s from request :%s", companyId, url)
                    return False
            return True
        except:
            return True


def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) != 3:
        return False
    if temp[0].strip() == "找工作":
        return False
    return True


def has_job_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False

        if j.has_key("message") and j["message"] == "操作成功":
            return True
        else:
            logger.info("wrong json content")
            logger.info(content)
            return False
    else:
        logger.info("Fail to get content")

    return False

def set_offline():
    mongo = db.connect_mongo()
    collection = mongo.job.job
    # collection_company = mongo.job.company
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    tendaysago = today - datetime.timedelta(days=15)
    collection.update_many({"modifyTime": {"$lt": tendaysago}, "offline":'N'}, {'$set': {"offline": 'Y'}})
    mongo.close()


def save_job_mongo(jobs):
    mongo = db.connect_mongo()
    collection = mongo.job.job
    # collection_company = mongo.job.company
    for job in jobs:
        jobitems = list(collection.find({"source":13050, "sourceId": job["sourceId"], "offline": 'N'}))
        if len(jobitems) == 0:
            jobitems = list(collection.find({"source":13050, "recruit_company_id":job["recruit_company_id"], "offline": 'N'}))

        newflag = True
        try:
            job["updateDate"]=datetime.datetime.strptime(job["updateDate"],"%Y-%m-%d %H:%M")
        except:
            job["updateDate"] = datetime.datetime.strptime(job["updateDate"], "%Y-%m-%d")

        for jobitem in jobitems:
            if jobitem["position"]==job["position"] and jobitem["salary"]==job["salary"] and \
               jobitem["educationType"]==job["educationType"] and jobitem["locationId"]==job["locationId"] and \
               jobitem["workYearType"]==job["workYearType"]:

                logger.info("Same job for existed and we got, update updateTime for job:%s for company:%s",
                            job["position"], job.get("recruit_company_id","no_id"))
                updateflag = True
                newflag = False

                if jobitem.has_key("jobNature") is False:
                    logger.info("*********adding more info! great!!!!")
                    collection.update_one({"_id": jobitem["_id"]},
                                          {'$set': {"sourceId": job["sourceId"],
                                                    "jobNature": job["jobNature"],
                                                    "positionAdvantage": job["positionAdvantage"],
                                                    "companyLabelList": job["companyLabelList"],
                                                    "financeStage": job["financeStage"],
                                                    "district": job["district"],
                                                    "recruit_company_id": job["recruit_company_id"]
                                                    },
                                           })


                for updatetime in jobitem["updateDates"]:
                    if (updatetime+datetime.timedelta(hours=8)).date() == job["updateDate"].date(): updateflag = False; break
                if updateflag is True:
                    logger.info("update updatetime now")


                    collection.update_one({"_id": jobitem["_id"]},
                                          {'$set': {"modifyTime": datetime.datetime.now(),
                                                    "updateDate":job["updateDate"] - datetime.timedelta(hours=8)},
                                           '$addToSet': {"updateDates": job["updateDate"] - datetime.timedelta(hours=8)}})

                else:
                    collection.update_one({"_id": jobitem["_id"]},{'$set': {"modifyTime": datetime.datetime.now()}})
                break

        if newflag is True:
            logger.info("add new job:%s for company:%s", job["position"], job["recruit_company_id"])
            item = {"source": 13050, "sourceId": job["sourceId"], "recruit_company_id": job["recruit_company_id"],
                    "position": job["position"], "salary": job["salary"],
                    "description": job["description"], "domain": int(job["domain"]),
                    "locationId": int(job["locationId"]), "educationType": int(job["educationType"]),
                    "workYearType": int(job["workYearType"]),
                    "jobNature":job["jobNature"],"positionAdvantage": job["positionAdvantage"],
                    "companyLabelList": job["companyLabelList"],"financeStage": job["financeStage"], "district": job["district"],
                    "startDate": job["updateDate"] - datetime.timedelta(hours=8), "offline": "N",
                    "updateDate": job["updateDate"] - datetime.timedelta(hours=8),
                    "updateDates": [job["updateDate"] - datetime.timedelta(hours=8)],
                    "createTime": datetime.datetime.now(), "modifyTime": datetime.datetime.now(),
                    "active": None, "verify": None, "createUser": None, "modifyUser": None}
            collection.insert(item)
    mongo.close()

def process(crawler_job, key, content, source_company_id):
    #logger.info(content)
    if has_content(content):
        d = pq((html.fromstring(content.decode("utf-8"))))
        position_types = d('div.item_con_filter> ul> li').text().split(" ")
        logger.info(json.dumps(position_types, ensure_ascii=False, cls=util.CJsonEncoder))
        jobs = {}
        for type in position_types:
            if type == '全部' or type.strip() == "":
                continue
            #each page has only 10 jobs, we need to re-fetch url with different pageNo
            pagenum = 1
            job_result =[]
            referurl = "https://www.lagou.com/gongsi/j%s.html" % key
            headers = {"Cookie": 'user_trace_token=20161221142700-7aded37d-c746-11e6-841f-525400f775ce;LGUID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;LGRID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;',
                       "Referer": referurl}
            while True:
                job_url = "https://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000&positionFirstType=%s&pageNo=%s" % (key, urllib.quote(type.encode('utf-8')), pagenum)
                result_job = crawler_job.crawl(job_url, headers=headers, agent=True)
                retry_job_times = 0
                while True:
                    if result_job['get'] == 'success' and has_job_content(result_job["content"]):
                        break
                    else:
                        result_job = crawler_job.crawl(job_url, headers=headers, agent=True)
                        retry_job_times += 1
                        if retry_job_times >= 15:
                            break
                        continue

                # content_job = result_job["content"]
                if result_job['get'] == 'success' and has_job_content(result_job["content"]):
                    content_job = result_job["content"]
                    totalCount = json.loads(content_job)['content']['data']['page']['totalCount']
                    job_result.append(json.loads(content_job))
                    js = json.loads(content_job)['content']['data']['page']['result']
                    logger.info("%s/%s(total) jobs under url: %s", len(js),totalCount, job_url)
                    if int(totalCount) - (pagenum * 10) > 0:
                        pagenum += 1
                    else:
                        break
                else:
                    break

            if len(job_result) > 0:

                jobs[type] = job_result
                jobs["version"] = 2

        logger.info(json.dumps(jobs, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(len(jobs))
        if len(jobs) > 0:
            result = {}
            result["content"] = jobs
            currentjobs = lagou_job_parser_2.parse_companyjobs(source_company_id, result, key)
            #logger.info(json.dumps(source_jobs, ensure_ascii=False, cls=util.CJsonEncoder))
            if len(currentjobs) > 0:
                #parser_db_util.save_jobs_standard(source_jobs)

                save_job_mongo(currentjobs)


def run(crawler,crawler_job):
    while True:
        if len(SC) == 0:
            return
        info = SC.pop(0)
        key = info["sourceId"]
        source_company_id = info["id"]
        url = "https://www.lagou.com/gongsi/j%s.html" % info["sourceId"]
        logger.info(url)
        retry_times = 0
        retry_times_2 = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success' and result["redirect_url"] == url:
                #logger.info(result["content"])
                try:
                    process(crawler_job, key, result['content'], source_company_id)
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'redirect':
                logger.info("Redirect: %s", result["url"])
                pass

            if result['get'] == 'success' and result['content'] is not None and result['content'].strip() != "":

                dt = pq(html.fromstring(result["content"].decode("utf-8")))
                title = dt('head> title').text().strip()
                if title == "找工作-互联网招聘求职网-拉勾网":
                    if retry_times_2 >= 2:
                        break
                    retry_times_2 += 1

            retry_times += 1
            if retry_times > 20:
                break
                #break



def start_run(concurrent_num):
    while True:
        mongo = db.connect_mongo()
        # collection = mongo.job.job
        collection_company = mongo.job.company
        logger.info("Lagou job start.....")
        dt = datetime.date.today()
        today = datetime.datetime(dt.year, dt.month, dt.day)
        daysago = today - datetime.timedelta(days=10)

        # source_companies = list(collection_company.find(
        #     {"$or": [{"jobCheckTime": None}, {"jobCheckTime": {"$lt": daysago}}]}).sort("_id", pymongo.DESCENDING).limit(1000))

        source_companies = list(collection_company.find({"jobChecked": None,
                                                         "source":13050}).sort("_id", pymongo.DESCENDING).limit(1000))


        for source_company in source_companies:

            logger.info("sourceId %s", source_company['sourceId'])

            info ={
                "sourceId" : source_company["sourceId"],
                "id": source_company["_id"],
            }
            SC.append(info)
            collection_company.update_one({"_id": source_company["_id"]},{"$set":{"jobChecked":True}})
        #run(g, LagouCrawler())
        threads = [gevent.spawn(run, LagouCrawler(), LagouJobCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou has finished")
        # exit()

        if len(source_companies) == 0:
            # break
            set_offline()
            collection_company.update_many({"source":13050,"jobChecked": {'$ne': None}},{'$set':{"jobChecked": None}})
            logger.info("Lagou job end...")
            gevent.sleep(30 * 60)
            # exit()
        mongo.close()
        #break

if __name__ == "__main__":
    start_run(10)