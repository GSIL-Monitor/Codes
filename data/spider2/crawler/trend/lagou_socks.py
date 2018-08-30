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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("crawler_lagou_job", stream=True)
logger = loghelper.get_logger("crawler_lagou_job")
cnt = 0
SC=[]

#mongo
mongo = db.connect_mongo()
collection = mongo.trend.jobs



class SocksiPyConnection(httplib.HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport = None, rdns = True, username = None, password = None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        self.sock = socksa.socksocket()
        self.sock.setproxy(*self.proxyargs)
        if isinstance(self.timeout, float):
            self.sock.settimeout(self.timeout)
        self.sock.connect((self.host, self.port))

class SocksiPyHandler(urllib2.HTTPHandler):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kw = kwargs
        urllib2.HTTPHandler.__init__(self)

    def http_open(self, req):
        def build(host, port=None, strict=None, timeout=0):
            conn = SocksiPyConnection(*self.args, host=host, port=port, strict=strict, timeout=timeout, **self.kw)
            return conn
        return self.do_open(build, req)


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

    # def get_proxy(self):
    #     proxy = {"$or": [{'type': 'socks4'}, {'type': 'socks5'}], 'anonymity': 'high'}
    #     proxy_ip = None
    #     while proxy_ip is None:
    #         proxy_ip = proxy_pool.get_single_proxy(proxy)
    #         if proxy_ip is None:
    #             logger.info("No proxy !!!!!!!!!!!!!!!!!!!")
    #             time.sleep(30)
    #     return proxy_ip
    #
    # def init_http_session(self, url, redirect=True):
    #     if self.opener is not None:
    #         self.opener.close()
    #
    #     self.socks_proxy = self.get_proxy()
    #     logger.info("Proxy: %s -- %s:%s", self.socks_proxy["type"], self.socks_proxy["ip"], self.socks_proxy["port"])
    #
    #     self.cookiejar = cookielib.CookieJar()
    #
    #     if self.socks_proxy["type"] == "socks4":
    #         handlers = [SocksiPyHandler(socks.PROXY_TYPE_SOCKS4, self.socks_proxy["ip"], self.socks_proxy["port"]),
    #                     urllib2.HTTPCookieProcessor(self.cookiejar)
    #                     ]
    #     else:
    #         handlers = [SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, self.socks_proxy["ip"], self.socks_proxy["port"]),
    #                     urllib2.HTTPCookieProcessor(self.cookiejar)
    #                     ]
    #
    #     self.opener = urllib2.build_opener(*handlers)

# crawler_job = LagouJobCrawler()

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

def save_job_mongo(company_id, jobs):
    for job in jobs:
        jobitems = list(collection.find({"source":13050, "sourceId": job["sourceId"], "offline": 'N'}))
        if len(jobitems) == 0:
            jobitems = list(collection.find({"source":13050, "companyId":company_id, "offline": 'N'}))

        newflag = True
        try:
            job["updateDate"]=datetime.datetime.strptime(job["updateDate"],"%Y-%m-%d %H:%M")
        except:
            job["updateDate"] = datetime.datetime.strptime(job["updateDate"], "%Y-%m-%d")

        for jobitem in jobitems:
            if jobitem["companyId"]==company_id and jobitem["position"]==job["position"] and jobitem["salary"]==job["salary"] and \
            jobitem["educationType"]==job["educationType"] and jobitem["locationId"]==job["locationId"] and jobitem["workYearType"]==job["workYearType"]:
                logger.info("Same job for existed and we got, update updateTime for job:%s for company:%s", job["position"], company_id)
                updateflag = True
                newflag = False
                for updatetime in jobitem["updateDates"]:
                    if (updatetime+datetime.timedelta(hours=8)).date() == job["updateDate"].date(): updateflag = False; break
                if updateflag is True:
                    logger.info("update updatetime now")
                    collection.update_one({"_id": jobitem["_id"]},{'$set': {"sourceId":job["sourceId"], "modifyTime": datetime.datetime.now()},
                                                                   '$addToSet': {"updateDates": job["updateDate"]}})
                else:
                    collection.update_one({"_id": jobitem["_id"]},{'$set': {"sourceId": job["sourceId"], "modifyTime": datetime.datetime.now()}})
                break

        if newflag is True:
            logger.info("add new job:%s for company:%s", job["position"], company_id)
            item = {"source": 13050, "sourceId": job["sourceId"], "companyId": int(company_id),
                    "position": job["position"], "salary": job["salary"],
                    "description": job["description"], "domain": int(job["domain"]),
                    "locationId": int(job["locationId"]), "educationType": int(job["educationType"]),
                    "workYearType": int(job["workYearType"]),
                    "startDate": job["updateDate"] - datetime.timedelta(hours=8), "offline": "N",
                    "updateDates": [job["updateDate"] - datetime.timedelta(hours=8)],
                    "createTime": datetime.datetime.now(), "modifyTime": datetime.datetime.now(),
                    "active": None, "verify": None, "createUser": None, "modifyUser": None}
            collection.insert(item)


def process(crawler_job, key, content, source_company_id, company_id):
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
            headers = {"Cookie": 'user_trace_token=20161221142700-7aded37d-c746-11e6-841f-525400f775ce;LGUID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;LGRID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;'}
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
            currentjobs = lagou_job_parser.parse_companyjobs(source_company_id, result, key)
            #logger.info(json.dumps(source_jobs, ensure_ascii=False, cls=util.CJsonEncoder))
            if len(currentjobs) > 0:
                #parser_db_util.save_jobs_standard(source_jobs)
                if company_id is not None:
                    save_job(company_id, currentjobs)
                    save_job_mongo(company_id, currentjobs)


def run(crawler,crawler_job):
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
                    process(crawler_job, key, result['content'], source_company_id, company_id)
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'redirect':
                logger.info("Redirect: %s", result["url"])
                pass

            retry_times += 1
            if retry_times > 20:
                break
                #break



def start_run(concurrent_num):
    global cnt
    while True:
        logger.info("Lagou job start.....")
        conn = db.connect_torndb()
        source_companies = conn.query("select * from source_company where source=13050 and id>%s and (active is null or active='Y') order by id limit 4000", cnt)
        # source_companies = conn.query("select * from source_company where id=193867")
        conn.close()

        for source_company in source_companies:
            if source_company["id"] > cnt:
                cnt = source_company["id"]
            logger.info("sourceId %s", source_company['sourceId'])
            if source_company["sourceId"] is None or source_company["companyId"] is None:
                continue
            company = conn.get("select * from company where id=%s and (active is null or active='Y')", source_company["companyId"])
            if company is None:
                logger.info("company is inactive")
                continue
            info ={
                "sourceId" : source_company["sourceId"],
                "id": source_company["id"],
                "companyId": source_company["companyId"]
            }
            SC.append(info)
        #run(g, LagouCrawler())
        threads = [gevent.spawn(run, LagouCrawler(), LagouJobCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou has finished %s", cnt)
        # exit()
        if len(source_companies) == 0:
            set_offline()
            cnt = 0
            logger.info("Lagou job end...")
            gevent.sleep(30 * 60)
            # exit()

        #break

if __name__ == "__main__":
    start_run(10)