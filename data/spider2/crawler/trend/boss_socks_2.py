# -*- coding: utf-8 -*-
import os, sys,random, time
import datetime
import urllib2
import urllib
import json

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
import proxy_pool

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/recruit/boss'))
import boss_job_parser_2

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

#logger
loghelper.init_logger("crawler_boss_job_2", stream=True)
logger = loghelper.get_logger("crawler_boss_job_2")
cnt = 0
SC=[]

#mongo
# mongo = db.connect_mongo()
# collection = mongo.job.job
# collection_company = mongo.job.company



class BossCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=25):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)
        self.pps = []

    def get_proxy(self, http_type):
        if len(self.pps) > 0:
            proxy_ip = self.pps.pop(0)

        else:
            proxy = {'type': "HTTPS",'anonymous': 'high'}

            while len(self.pps) == 0:
                logger.info("Start proxy_pool.get_single_proxy %s", self.num)
                proxy_ips = proxy_pool.get_single_proxy_x(proxy, 10000)
                if len(proxy_ips) == 0:
                    logger.info("proxy_pool.get_single_proxy return None")

                    time.sleep(30)
                else:
                    for pi in proxy_ips:
                        self.pps.append(pi)
            proxy_ip = self.pps.pop(0)
        logger.info("ppps: %s", proxy_ip)
        return proxy_ip

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("BOSS直聘验证码") >= 0:
            #logger.info(content)
            return False
        if title.find("BOSS直聘-互联网招聘神器！") >= 0:
            return False
        if title.find("BOSS直聘") >= 0:
            return True
        #logger.info(content)
        return False


class BossJobCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=25):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("BOSS直聘验证码") >= 0:
            #logger.info(content)
            return False
        if title.find("BOSS直聘-互联网招聘神器！") >= 0:
            return False
        if title.find("BOSS直聘") >= 0:
            return True
        #logger.info(content)
        return False


def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 2:
        return False
    if temp[0].strip() == "BOSS直聘":
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
        jobitems = list(collection.find({"source":13055, "sourceId": job["sourceId"], "offline": 'N'}))
        if len(jobitems) == 0:
            jobitems = list(collection.find({"source":13055, "recruit_company_id":job["recruit_company_id"], "offline": 'N'}))

        newflag = True
        # try:
        #     job["updateDate"]=datetime.datetime.strptime(job["updateDate"],"%Y-%m-%d %H:%M")
        # except:
        #     job["updateDate"] = datetime.datetime.strptime(job["updateDate"], "%Y-%m-%d")

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
            item = {"source": 13055, "sourceId": job["sourceId"], "recruit_company_id": job["recruit_company_id"],
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
        position_types = d('div.job-category-items> a')

        jobs = {}
        for ptype in position_types:

            ptype_t = pq(ptype)('a').text()
            ptype_link = pq(ptype)('a').attr("href")

            ptype_domain = ptype_t.split(" ")[0].strip()
            ptype_total = ptype_t.split(" ")[1].replace("(","").replace(")","").strip()
            pagetotal = int(ptype_total) / 15
            if int(ptype_total) >= 15:
                if int(ptype_total) % 15 != 0: pagetotal += 1
            else:
                pagetotal += 1

            logger.info("%s --- %s --- %s --- %s", ptype_domain, ptype_total, pagetotal, ptype_link)
            if ptype_domain.find('全部')>=0 or ptype_domain.strip() == "":
                continue
            #each page has only 10 jobs, we need to re-fetch url with different pageNo
            job_result =[]
            page = 0
            while True:
                if page >= pagetotal: break
                page += 1
                job_url = "https://www.zhipin.com%s?page=%s&ka=page-%s" % (ptype_link, page, page)
                result_job = crawler_job.crawl(job_url, agent=True)
                retry_job_times = 0
                while True:
                    if result_job['get'] == 'success' and has_content(result_job["content"]):
                        break
                    else:
                        result_job = crawler_job.crawl(job_url, agent=True)
                        retry_job_times += 1
                        if retry_job_times >= 15:
                            break
                        continue

                # content_job = result_job["content"]
                if result_job['get'] == 'success' and has_content(result_job["content"]):
                    content_job = result_job["content"]
                    job_result.append(content_job)


            if len(job_result) > 0:

                jobs[ptype_domain] = job_result
                jobs["version"] = 2

        logger.info(json.dumps(jobs, ensure_ascii=False, cls=util.CJsonEncoder))
        logger.info(len(jobs))
        if len(jobs) > 0:
            result = {}
            result["content"] = jobs
            currentjobs = boss_job_parser_2.parse_companyjobs(source_company_id, result, key)
            if len(currentjobs) > 0:

                save_job_mongo(currentjobs)


def run(crawler,crawler_job):
    while True:
        if len(SC) == 0:
            return
        info = SC.pop(0)
        key = info["sourceId"]
        source_company_id = info["id"]
        # todo sourceId2
        if info["sourceId2"] is not None:
            url = "https://www.zhipin.com/gongsir/%s.html" % info["sourceId2"]
        else:
            url = "https://www.zhipin.com/gongsir/%s.html" % info["sourceId"]
        logger.info(url)
        retry_times = 0
        retry_times_2 = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(crawler_job, key, result['content'], source_company_id)
                except Exception,ex:
                    logger.exception(ex)
                break

            else:
                if result.has_key("content") is False or result["content"] is None or result["content"].strip() == "" or \
                                result["content"].find("</html>") == -1:
                    continue
                d = pq(html.fromstring(result["content"]))
                title = d('head> title').text().strip()
                if title == "BOSS直聘-互联网招聘神器！":
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
        logger.info("boss job start.....")
        dt = datetime.date.today()
        today = datetime.datetime(dt.year, dt.month, dt.day)
        daysago = today - datetime.timedelta(days=10)

        source_companies = list(collection_company.find({"jobChecked": None,
                                                         "source":13055}).sort("_id", pymongo.DESCENDING).limit(1000))
        # source_companies = list(collection_company.find({"sourceId": '1810',"source":13055}))
        for source_company in source_companies:

            logger.info("sourceId %s", source_company['sourceId'])

            info ={
                "sourceId" : source_company["sourceId"],
                "sourceId2": source_company["sourceId2"] if source_company.has_key("sourceId2") and source_company["sourceId2"] is not None else None,
                "id": source_company["_id"],
            }
            SC.append(info)
            collection_company.update_one({"_id": source_company["_id"]},{"$set":{"jobChecked":True}})

        threads = [gevent.spawn(run, BossCrawler(), BossCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)
        # break
        logger.info("boss has finished")
        # exit()

        if len(source_companies) == 0:
            # break
            # set_offline()
            collection_company.update_many({"source":13055,"jobChecked": {'$ne': None}},{'$set':{"jobChecked": None}})
            logger.info("boss job end...")
            gevent.sleep(30 * 60)

        mongo.close()
            # exit()

        #break

if __name__ == "__main__":
    start_run(15)