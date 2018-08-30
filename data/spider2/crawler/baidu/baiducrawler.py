# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
from lxml import html
from pyquery import PyQuery as pq
import urllib

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util

#logger
loghelper.init_logger("crawler_baidu", stream=True)
logger = loghelper.get_logger("crawler_baidu")


class NewsDownloader:
    def __init__(self, TYPE=60001, SOURCE=13080, RETRY=20, CATEGORY=None, FORCE=False):
        self.TYPE = TYPE
        self.SOURCE = SOURCE
        self.RETRY = RETRY
        self.CATEGORY = CATEGORY
        self.FORCE = FORCE

    def has_news_content(self, content):
        d = pq(html.fromstring(content.decode("utf-8",'ignore')))
        title = d('head> title').text().strip()

        if len(title) > 0 and title.find("百度") == -1:
            return True
        else:
            return False

    def extractWechatContents(self,article):
        d=pq(html.fromstring(article))
        wechatContents=[]
        pretext = None
        for p in d('p,img'):
            wechatContent={}
            if d(p).text():
                wechatContent['type']='text'
                wechatContent['data']=d(p).text()
                if pretext is not None and pretext == d(p).text():
                    continue
                else:
                    pretext = d(p).text()
            elif d(p)('img'):
                if d(p).attr('data-src'):
                    wechatContent['type'] = 'image'
                    wechatContent['data'] = d(p).attr('data-src')
            if len(wechatContent)>0:wechatContents.append(wechatContent)
        return wechatContents

    def process_news(self, newsurl, content, download_crawler):
        dnews = {}
        if self.has_news_content(content):
            try:
                d = pq(html.fromstring(content.decode("utf-8")))
            except:
                d = pq(html.fromstring(content))


        #     logger.info("*************DONE*************")
        # return dnews


    def crawler_news(self, crawler, keyword, newstitle=True,newsfocus=True):
        retry = 0
        if newstitle is True:
            tn = urllib.urlencode({"tn":"newstitle"})
        else:
            tn = urllib.urlencode({"tn": "news"})

        if newsfocus is True:
            ct = "1"
        else:
            ct = "0"

        keyword_Str = urllib.urlencode({"word": keyword})
        newsurl = "http://news.baidu.com/ns?%s&pn=20&cl=2&ct=%s&%s&rn=20&ie=utf-8&bt=0&et=0" %(keyword_Str,ct,tn)
        while True:
            result = crawler.crawl(newsurl, agent=True)

            if result['get'] == 'success' and result.get("code") == 200:
                try:
                    self.process_news(newsurl, result['content'], download_crawler)
                    return {"result": "SUCCESS"}
                except Exception, ex:
                    logger.exception(ex)
                    return {"result": "FAILED"}

            logger.info("******************Retry: %s", retry)
            if retry > self.RETRY:
                return {"result": "FAILED"}
            retry += 1


class BaiduNewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        # logger.info("round num:%s",self.roundn)
        d = pq(html.fromstring(content.decode("utf-8",'ignore')))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)

        if title.find("百度") >= 0:
            return True

        return True



if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        link = param
        download_crawler = download.DownloadCrawler(use_proxy=False)
        crawler = NewsDownloader()
        result = crawler.crawler_news(BaiduNewsCrawler(), link, newstitle=False,newsfocus=True)
        logger.info(result)
    else:
        logger.info("No link provided")

    # crawler = NewsDownloader()
    # link='http://mp.weixin.qq.com/s?__biz=MjM5NTczMDEwMQ==&mid=2651053087&idx=1&sn=272509575865a712a5d23cdfffa91ccb&chksm=bd037bc58a74f2d3c5815acdb0a9c4b2ac3dcca860a0c25b1b10b0ed6d82cb5923089c868f4a#rd'
    # link='http://mp.weixin.qq.com/s?__biz=MjM5Mzc3NzU2MA==&mid=2656168620&idx=1&sn=4c20fc81987c8f43eeda68bfe3aaee7c&chksm=bd34985b8a43114d42e2ca29431e587dea179cddcaae3f1ff2746246dc3fedc1b3714a2553c4#rd'
    #
    # result = crawler.crawler_news(WechatCrawler(), link)
