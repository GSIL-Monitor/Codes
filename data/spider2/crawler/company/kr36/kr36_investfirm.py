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
loghelper.init_logger("crawler_36kr_investfirm", stream=True)
logger = loghelper.get_logger("crawler_36kr_investfirm")


def get_url(key):
    url = {}
    url["key"] = key
    url["staffs"] = "http://rong.36kr.com/api/organization/%s/user" % key
    url["former_members"] = "http://rong.36kr.com/api/organization/%s/former-member" % key

    return url

class kr36Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
            except:
                return False

            if j["msg"].strip() == "您请求的过于频繁，请稍后再试！":
                logger.info("code=%d, %s" % (j["code"], j["msg"]))
                return False
            else:
                return True
        return False


def has_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False

        if j["code"] == 0:
            return True
        else:
            logger.info("code=%d, %s" % (j["code"], j["msg"]))
    else:
        logger.info("Fail to get content")

    return False


def process(g, crawler, url, key, content):
    if has_content(content):
        investor={}
        investor_base = json.loads(content)
        investor["investor_base"] = investor_base
        #logger.info(investor_base["data"]["company"]["name"])
        url_map = get_url(key)
        for k in url_map.keys():
            if k != "key" and k != "investor_base":
                logger.info(url_map[k])
                result = crawler.crawl(url_map[k])
                while True:
                    if result['get'] == 'success':
                        break
                    else:
                        result = crawler.crawl(url_map[k])
                content_more =result['content']
                if has_content(content_more):
                    investor[k] = json.loads(content_more)
                    logger.info(investor[k])
                    # time.sleep(random.randint(3,8))

        #t.process(url_map["company_base"], key, company)
        crawler.save(g.SOURCE, g.TYPE, url, key, investor)
        g.latestIncr()


def run(g, crawler):
    while True:
        if g.finish(num=1000):
            return
        key = g.nextKey()
        url = "http://rong.36kr.com/api/organization/%s/basic" % key
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                try:
                    process(g, crawler, url, key, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break


def start_run(concurrent_num, flag):
    while True:
        logger.info("36kr investor %s start...", flag)

        g = GlobalValues.GlobalValues(13020, 36003, flag)

        threads = [gevent.spawn(run, g, kr36Crawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("36kr investor %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*30)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days

        #break

if __name__ == "__main__":
    start_run(1, "incr")
    #start_run(10, "all")