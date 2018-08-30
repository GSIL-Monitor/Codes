# -*- coding: utf-8 -*-
import os, sys, random, time
import datetime
import urllib2
import urllib
import json

import pymongo
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey;

monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config, util
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

# logger
loghelper.init_logger("crawler_liepin_job", stream=True)
logger = loghelper.get_logger("crawler_liepin_job")
cnt = 0
SC = []
SOURCE = 13056

# mongo
mongo = db.connect_mongo()
collection = mongo.job.job
collection_company = mongo.job.company


class liepinCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        try:
            # logger.info(content)
            j = json.loads(content)
            if j['data']['totalCount'] < 10000: return True
        except:
            logger.info('success failed')
            return False


class liepinJobCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)

        if title.find("liepin直聘验证码") >= 0:
            # logger.info(content)
            return False
        if title.find("liepin直聘-互联网招聘神器！") >= 0:
            return False
        if title.find("liepin直聘") >= 0:
            return True
        # logger.info(content)
        return False


def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    # logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 2:
        return False
    if temp[0].strip() == "liepin直聘":
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
    dt = datetime.date.today()
    today = datetime.datetime(dt.year, dt.month, dt.day)
    tendaysago = today - datetime.timedelta(days=15)
    collection.update_many({"modifyTime": {"$lt": tendaysago}, "offline": 'N'}, {'$set': {"offline": 'Y'}})


def save_job_mongo(jobs):
    for job in jobs:
        jobitems = list(collection.find({"source": SOURCE, "sourceId": job["sourceId"], "offline": 'N'}))
        if len(jobitems) == 0:
            jobitems = list(
                collection.find({"source": SOURCE, "recruit_company_id": job["recruit_company_id"], "offline": 'N'}))

        newflag = True
        # try:
        #     job["updateDate"]=datetime.datetime.strptime(job["updateDate"],"%Y-%m-%d %H:%M")
        # except:
        #     job["updateDate"] = datetime.datetime.strptime(job["updateDate"], "%Y-%m-%d")

        for jobitem in jobitems:
            if jobitem["position"] == job["position"] and jobitem["salary"] == job["salary"] and \
                    jobitem["educationType"] == job["educationType"] and jobitem["locationId"] == job["locationId"] and \
                    jobitem["workYearType"] == job["workYearType"]:

                logger.info("Same job for existed and we got, update updateTime for job:%s for company:%s",
                            job["position"], job.get("recruit_company_id", "no_id"))
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
                    if (updatetime + datetime.timedelta(hours=8)).date() == job[
                        "updateDate"].date(): updateflag = False; break
                if updateflag is True:
                    logger.info("update updatetime now")

                    collection.update_one({"_id": jobitem["_id"]},
                                          {'$set': {"modifyTime": datetime.datetime.now(),
                                                    "updateDate": job["updateDate"] - datetime.timedelta(hours=8)},
                                           '$addToSet': {
                                               "updateDates": job["updateDate"] - datetime.timedelta(hours=8)}})

                else:
                    collection.update_one({"_id": jobitem["_id"]}, {'$set': {"modifyTime": datetime.datetime.now()}})
                break

        if newflag is True:
            logger.info("add new job:%s for company:%s", job["position"], job["recruit_company_id"])
            item = {"source": SOURCE, "sourceId": job["sourceId"], "recruit_company_id": job["recruit_company_id"],
                    "position": job["position"], "salary": job["salary"],
                    "description": job["description"], "domain": int(job["domain"]),
                    "locationId": int(job["locationId"]), "educationType": int(job["educationType"]),
                    "workYearType": int(job["workYearType"]),
                    "jobNature": job["jobNature"], "positionAdvantage": job["positionAdvantage"],
                    "companyLabelList": job["companyLabelList"], "financeStage": job["financeStage"],
                    "district": job["district"],
                    "startDate": job["updateDate"] - datetime.timedelta(hours=8), "offline": "N",
                    "updateDate": job["updateDate"] - datetime.timedelta(hours=8),
                    "updateDates": [job["updateDate"] - datetime.timedelta(hours=8)],
                    "createTime": datetime.datetime.now(), "modifyTime": datetime.datetime.now(),
                    "active": None, "verify": None, "createUser": None, "modifyUser": None}
            collection.insert(item)


def process(crawler_job, key, content, source_company_id):
    # logger.info(content)
    # if has_content(content):
    if 1:
        j = json.loads(content)
        positions = j['data']['list']
        domain = 0

        jobs = []
        for p in positions:
            logger.info(p['url'])
            key = p['url'].split('job/')[-1].split('.shtml')[0]

            location_id = 0
            location_new = parser_db_util.get_location(p['city'].split('-')[0])
            if location_new != None:
                location_id = location_new["locationId"]

            education = p['eduLevel']
            education_type = 0
            if '大专' in education:
                education_type = 6020
            elif '本科' in education:
                education_type = 6030
            elif '硕士' in education:
                education_type = 6040
            elif '博士' in education:
                education_type = 6050

            work_year = p['workYear']
            workYear_type = 7000
            if '应届' in work_year:
                workYear_type = 7010
            elif '1年以下' in work_year:
                workYear_type = 7020
            elif '1年以上' in work_year or '2年以上' in work_year:
                workYear_type = 7030
            elif '3年以上' in work_year:
                workYear_type = 7040
            elif '5年以上' in work_year or '6年以上' in work_year or '8年以上' in work_year:
                workYear_type = 7050
            elif '10年以上' in work_year:
                workYear_type = 7060

            update_time = datetime.datetime.strptime(p['time'], "%Y年%m月%d日")

            source_job = {
                "source": SOURCE,
                "sourceId": key,
                "recruit_company_id": str(source_company_id),
                "position": p['title'],
                "salary": p['salary'],
                "description": None,
                "domain": domain,
                "locationId": location_id,
                "educationType": education_type,
                "workYearType": workYear_type,
                "startDate": update_time,
                "updateDate": update_time,
                "jobNature": None,
                "positionAdvantage": None,
                "companyLabelList": None,
                "financeStage": None,
                "district": None,
            }

            logger.info(json.dumps(source_job, ensure_ascii=False, cls=util.CJsonEncoder))
            jobs.append(source_job)

        logger.info(len(jobs))
        if len(jobs) > 0:
            save_job_mongo(jobs)


def run(crawler, crawler_job):
    while True:
        if len(SC) == 0:
            return
        info = SC.pop(0)
        key = info["sourceId"]
        source_company_id = info["id"]

        # url = "https://www.liepin.com/company/%s" % info["sourceId"]
        url = "https://www.liepin.com/company/sojob.json"
        logger.info(url)
        retry_times = 0
        retry_times_2 = 0

        headers = {
            # 'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            'x-requested-with': "XMLHttpRequest",
        }

        payload = {
            'ecompIds': key,
            'pageSize': 10000,
            'curPage': 0,
        }
        payload = urllib.urlencode(payload)

        while True:
            result = crawler.crawl(url, agent=True, postdata=payload, headers=headers)
            if result['get'] == 'success':
                # logger.info(result["content"])
                try:
                    process(crawler_job, key, result['content'], source_company_id)
                except Exception, ex:
                    logger.exception(ex)
                break

            retry_times += 1
            if retry_times > 20:
                break
                # break


def start_run(concurrent_num):
    while True:
        logger.info("liepin job start.....")
        dt = datetime.date.today()
        today = datetime.datetime(dt.year, dt.month, dt.day)
        daysago = today - datetime.timedelta(days=10)

        source_companies = list(collection_company.find({"jobChecked": None,
                                                         "source": SOURCE}).sort("_id", pymongo.DESCENDING).limit(1000))
        # source_companies = list(collection_company.find({"sourceId": '1093224',"source":SOURCE}))
        for source_company in source_companies:
            logger.info("sourceId %s", source_company['sourceId'])

            info = {
                "sourceId": source_company["sourceId"],
                "id": source_company["_id"],
            }
            SC.append(info)
            collection_company.update_one({"_id": source_company["_id"]}, {"$set": {"jobChecked": True}})

        threads = [gevent.spawn(run, liepinCrawler(), liepinJobCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)
        # break
        logger.info("liepin has finished")
        # exit()

        if len(source_companies) == 0:
            # break
            set_offline()
            collection_company.update_many({"source": SOURCE, "jobChecked": {'$ne': None}},
                                           {'$set': {"jobChecked": None}})
            logger.info("liepin job end...")
            gevent.sleep(30 * 60)
            # exit()

        # break


if __name__ == "__main__":
    start_run(4)
