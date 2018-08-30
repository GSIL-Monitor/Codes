# -*- coding: utf-8 -*-
import os, sys,random
import datetime
import urllib2
import urllib
import json
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
import lagou_job_parser

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

#logger
loghelper.init_logger("crawler_lagou_job", stream=True)
logger = loghelper.get_logger("crawler_lagou_job")
cnt = 0
SC=[]
class LagouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
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

crawler_job = LagouJobCrawler()

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
    conn = db.connect_torndb()
    # job_ids.sort()
    # for id in job_ids:
    #     logger.info(id)
    # if len(job_ids)> 0:
    #     logger.info("Current have %s jobs", len(job_ids))
    #     jobs = conn.query("select id from job where companyId=%s and offline=%s", company_id, 'N')
    #
    #     for job in jobs:
    #         jobId = job["id"]
    #
    #         if jobId not in job_ids:
    #             logger.info("Current job %s is expired", jobId)
    #             sql = "update job set offline='Y', modifyTime=now() where id =%s"
    #             conn.update(sql, jobId)

    # check job with -5 days and set offline
    cutoffdate = datetime.date.today() + datetime.timedelta(-10)
    cutofftime = datetime.datetime(cutoffdate.year, cutoffdate.month, cutoffdate.day)
    conn.update("update job set offline='Y', modifyTime=now() where offline='N' and modifyTime<%s", cutofftime)
    conn.close()

def save_job(company_id, jobs):
    conn = db.connect_torndb()
    job_ids =[]
    for job in jobs:

        sql = 'select * from job where companyId=%s and position=%s and salary=%s and educationType=%s and workYearType=%s and locationId=%s and offline=%s limit 1'
        result = conn.get(sql, company_id, job['position'], job["salary"], job['educationType'], job['workYearType'], job['locationId'], 'N')
        if result is None:
            sql = 'insert job(companyId, position, salary, description, domain,' \
                  ' locationId, educationType, workYearType, startDate, updateDate,' \
                  'createTime, modifyTime, source) values(' \
                  '%s, %s, %s, %s, %s,' \
                  '%s, %s, %s, %s, %s,' \
                  'now(), now(), %s)'
            job_id = conn.insert(sql, company_id, job['position'], job['salary'], job['description'], job['domain'],
                    job['locationId'], job['educationType'], job['workYearType'], job['updateDate'], job['updateDate'], 13050)
            job_ids.append(job_id)
        else:
            job_id = result['id']
            sql = 'update job set updateDate = %s, modifyTime=now(), source=%s where id =%s'
            conn.update(sql, job['updateDate'], 13050, job_id)
            job_ids.append(job_id)

    #set_offline(company_id, job_ids)

    # conn.update('update source_job set jobId = %s where id=%s', job_id, job['id'])
    conn.close()


def process(key, content, source_company_id, company_id):
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
            while True:
                job_url = "https://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000&positionFirstType=%s&pageNo=%s" % (key, urllib.quote(type.encode('utf-8')), pagenum)
                result_job = crawler_job.crawl(job_url)
                retry_job_times = 0
                while True:
                    if result_job['get'] == 'success' and has_job_content(result_job["content"]):
                        break
                    else:
                        result_job = crawler_job.crawl(job_url)
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
            currentjobs = lagou_job_parser.parse_companyjobs(source_company_id, result, key)
            #logger.info(json.dumps(source_jobs, ensure_ascii=False, cls=util.CJsonEncoder))
            if len(currentjobs) > 0:
                #parser_db_util.save_jobs_standard(source_jobs)
                if company_id is not None:
                    save_job(company_id, currentjobs)


def run(crawler):
    while True:
        if len(SC) == 0:
            return
        info = SC.pop(0)
        key = info["sourceId"]
        source_company_id = info["id"]
        company_id = info["companyId"]
        url = "https://www.lagou.com/gongsi/j%s.html" % info["sourceId"]
        logger.info(url)
        retry_times = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success' and result["redirect_url"] == url:
                #logger.info(result["content"])
                try:
                    process(key, result['content'], source_company_id, company_id)
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'redirect':
                logger.info("Redirect: %s", result["url"])
                pass

            retry_times += 1
            if retry_times > 10:
                break
                #break



def start_run(concurrent_num):
    global cnt
    while True:
        logger.info("Lagou job start.....")
        conn = db.connect_torndb()
        source_companies = conn.query("select * from source_company where source=13050 and id>%s order by id limit 4000", cnt)
        #source_companies = conn.query("select * from source_company where id=193867")
        conn.close()

        for source_company in source_companies:
            if source_company["id"] > cnt:
                cnt = source_company["id"]
            logger.info("sourceId %s", source_company['sourceId'])
            if source_company["sourceId"] is None or source_company["companyId"] is None:
                continue
            info ={
                "sourceId" : source_company["sourceId"],
                "id": source_company["id"],
                "companyId": source_company["companyId"]
            }
            SC.append(info)
        #run(g, LagouCrawler())
        threads = [gevent.spawn(run, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou has finished %s", cnt)
        #exit()
        if len(source_companies) == 0:
            set_offline()
            cnt = 0
            logger.info("Lagou job end...")
            gevent.sleep(30 * 60)
            # exit()

        #break

if __name__ == "__main__":
    start_run(25)