# -*- coding: utf-8 -*-
import os, sys,datetime, random, time
from lxml import html
from pyquery import PyQuery as pq
import urllib
import json
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import loghelper
import util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler


#logger
loghelper.init_logger("download", stream=True)
logger = loghelper.get_logger("download")

class DownloadCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, max_crawl=1, timeout=30, use_proxy=True):
        BaseCrawler.BaseCrawler.__init__(self, max_crawl=max_crawl, timeout=timeout, use_proxy=use_proxy)

        self._agent = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]


    def get(self, max_retry=20, agent=True):
        retry_times = 0
        while retry_times < max_retry:
            #todo set cookie when report 521
            headers = {
                "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0',
                'Host': "www.miitbeian.gov.cn",
                "Cookie": '__jsluid=0ee1bc591151f9a95def24317782ba61; JSESSIONID=QTbLYX6Trm2K4Vy4YtDPv92T1vQw91fFp6JylQJJRXsMkn425hxk!1231645729; Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa=1477920639; Hm_lpvt_d7682ab43891c68a00de46e9ce5b76aa=1477920639; __jsl_clearance=1477966316.596|0|cgWdG4bBEc3r6Y4fWwt9qkeq0DI%3D'
            }
            url = "http://www.miitbeian.gov.cn/getVerifyCode?%s" % random.randint(10, 90)
            result = self.crawl(url, headers=headers)
            #print result
            if result['get'] == 'success':
                # logger.info(result["content"])
                try:
                    if result["content"].find("拦截") == -1:
                        return result["content"]
                    else:
                        logger.info("拦截!!!")
                        time.sleep(10)
                except Exception,e:
                    print e
                    pass
            self.init_http_session(url)
            retry_times += 1

        return None


if __name__ == "__main__":
    crawler = DownloadCrawler(use_proxy=False)
    for i in range(100):
        # url = "http://www.miitbeian.gov.cn/getVerifyCode?%s" % random.randint(10,90)
        filename = "vfimg/%s.jpeg" % i
        c = crawler.get()
        if c:
            f = open(filename, "wb")
            f.write(c)
            f.close()
        print filename
