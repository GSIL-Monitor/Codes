# -*- coding: utf-8 -*-
import os, sys,random, datetime
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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import GlobalValues

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,util

#logger
loghelper.init_logger("crawler_lagou_company", stream=True)
logger = loghelper.get_logger("crawler_lagou_company")

DATE = None

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
            #logger.info(content)
            return False
        if title.find("找工作-互联网招聘求职网-拉勾网") >= 0:
            return False
        if title.find("拉勾网") >= 0:
            return True
        #logger.info(content)
        return False

class LagouJobCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)


    def is_crawl_success(self, url, content):
        if content.find('操作成功') == -1:
            logger.info(content)
            return False
        return True

crawler_job = LagouJobCrawler()

def has_content(content):
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)

    temp = title.split("-")

    if len(temp) < 2:
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


def process(g, crawler, url, key, content):
    #logger.info(content)
    if has_content(content):
        logger.info(key)
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        g.latestIncr()
        # jobs_url = "http://www.lagou.com/gongsi/j%s.html" % key
        # #job_url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000" % key
        # retry_times_job = 0
        # result = crawler.crawl(jobs_url)
        # while True:
        #     if result['get'] == 'success' and result["redirect_url"] == jobs_url:
        #          break
        #     else:
        #         result = crawler.crawl(jobs_url)
        #         #continue
        #     retry_times_job += 1
        #
        #     if retry_times_job > 20:
        #         result["content"] = "no_content"
        #         break
        #
        # d = pq((html.fromstring(result['content'].decode("utf-8"))))
        # position_types = d('div.item_con_filter> ul> li').text().split(" ")
        # logger.info(json.dumps(position_types, ensure_ascii=False, cls=util.CJsonEncoder))
        # jobs = {}
        # for type in position_types:
        #     if type == '全部' or type.strip() == "":
        #         continue
        #     job_url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000&positionFirstType=%s" % (key, urllib.quote(type.encode('utf-8')))
        #     result_job = crawler_job.crawl(job_url)
        #     while True:
        #         if result_job['get'] == 'success':
        #             break
        #         else:
        #             result_job = crawler_job.crawl(job_url)
        #             continue
        #     content_job = result_job["content"]
        #     if has_job_content(content_job):
        #         jobs[type] = json.loads(content_job)
        #         jobs["version"] = 2
        #
        # logger.info(json.dumps(jobs, ensure_ascii=False, cls=util.CJsonEncoder))
        # logger.info(len(jobs))
        # if len(jobs) > 0:
        #     crawler.save(g.SOURCE, 36010, jobs_url, key, jobs)
        '''
        if has_job_content(content_job):
            jobs = json.loads(content_job)
            #job=json.dumps(jobs, ensure_ascii=False)
            #logger.info(content_job)
            #logger.info(job)
            # time.sleep(random.randint(3,8))
            crawler.save(g.SOURCE,36010, job_url, key, jobs)
        '''
def crawl(crawler, key, g):
    url = "https://www.lagou.com/gongsi/%s.html" % key
    retry_times = 0
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            # logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception, ex:
                logger.exception(ex)
            break
        elif result['get'] == 'redirect':
            logger.info("Redirect: %s", result["url"])
            break

        retry_times += 1
        if retry_times > 10:
            break

def run(g, crawler):
    while True:
        if g.finish(num=500):
            return
        key = g.nextKey()
        crawl(crawler, key, g)



def start_run(concurrent_num, flag):
    global DATE
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        date_num = int(datestr) % 10
        logger.info("Lagou last back is %s", DATE)
        logger.info("Lagou company %s start for %s", flag, datestr)
        
        if datestr != DATE and date_num == 4:
            logger.info("%s is 4! back to 2000", datestr)
            g = GlobalValues.GlobalValues(13050, 36001, flag, back=2000)
            DATE = datestr
        else:
            g = GlobalValues.GlobalValues(13050, 36001, flag, back=8)

        #run(g, LagouCrawler())
        threads = [gevent.spawn(run, g, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

        #break

if __name__ == "__main__":


    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(23, "all")
        else:
            key = str(int(param))
            g = GlobalValues.GlobalValues(13050, 36001, "incr", back=0)
            crawl(LagouCrawler(), key, g)
    else:
        start_run(1, "incr")