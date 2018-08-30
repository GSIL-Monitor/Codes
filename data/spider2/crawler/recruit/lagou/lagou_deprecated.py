# -*- coding: utf-8 -*-
import os, sys,random
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
import loghelper

#logger
loghelper.init_logger("crawler_lagou_company", stream=True)
logger = loghelper.get_logger("crawler_lagou_company")


class LagouCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=15):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    # 实现
    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("拉勾网") >= 0:
            return True
        #logger.info(content)
        return False

class LagouJobCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)


    def is_crawl_success(self, url, content):
        if content.find('操作成功') == -1:
            return False
        return True

crawler_job = LagouJobCrawler()

def has_content(content):
    d = pq(html.fromstring(content))
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

        return True
    else:
        logger.info("Fail to get content")

    return False


def process(g, crawler, url, key, content):
    #logger.info(content)
    if has_content(content):
        logger.info(key)
        crawler.save(g.SOURCE, g.TYPE, url, key, content)
        #logger.info(content)
        g.latestIncr()
        job_url = "http://www.lagou.com/gongsi/searchPosition.json?companyId=%s&pageSize=1000" % key
        result = crawler_job.crawl(job_url)
        while True:
            if result['get'] == 'success':
                 break
            else:
                result = crawler_job.crawl(job_url)
                continue
        content_job =result['content']
        if has_job_content(content_job):
            jobs = json.loads(content_job)
            #job=json.dumps(jobs, ensure_ascii=False)
            #logger.info(content_job)
            #logger.info(job)
            # time.sleep(random.randint(3,8))
            crawler.save(g.SOURCE,36010, job_url, key, jobs)


def run(g, crawler):
    while True:
        if g.finish(num=50):
            return
        key = g.nextKey()
        #key ="133338"
        url = "http://www.lagou.com/gongsi/%s.html" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(g, crawler, url, key, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            elif result['get'] == 'redirect':
                break



def start_run(concurrent_num, flag):
    while True:
        logger.info("Lagou company %s start...", flag)

        g = GlobalValues.GlobalValues(13050, 36001, flag)

        threads = [gevent.spawn(run, g, LagouCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("Lagou company %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

        #break

if __name__ == "__main__":
    start_run(20, "incr")