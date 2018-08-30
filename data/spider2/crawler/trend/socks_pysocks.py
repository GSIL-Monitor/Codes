# -*- coding: utf-8 -*-
import os, sys,random, time
import cookielib
import httplib
import json
import urllib2
# import requesocks


reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import db, config, util
import loghelper

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

#logger
loghelper.init_logger("crawler_lagou_job", stream=True)
logger = loghelper.get_logger("crawler_lagou_job")


class LagouJobCrawler():
    def __init__(self, timeout=20):
        self.timeout=timeout
        self.opener = None
        self.socks_proxy = {"type": "socks4", "ip": "180.173.153.98", "port": 1080}

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


    def crawler(self, url, redirect=True):
        if self.opener is not None:
            self.opener.close()

        logger.info("Proxy: %s -- %s:%s", self.socks_proxy["type"], self.socks_proxy["ip"], self.socks_proxy["port"])

        # self.cookiejar = cookielib.CookieJar()

        if self.socks_proxy["type"] == "socks4":
            handlers = [SocksiPyHandler(socks.SOCKS4, self.socks_proxy["ip"], self.socks_proxy["port"]),
                        ]
        else:
            handlers = [SocksiPyHandler(socks.SOCKS5, self.socks_proxy["ip"], self.socks_proxy["port"]),
                        ]

        self.opener = urllib2.build_opener(*handlers)
        headers = {
            "Cookie": 'user_trace_token=20161221142700-7aded37d-c746-11e6-841f-525400f775ce;LGUID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;LGRID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;'}

        # request = urllib2.Request(url)
        r = self.opener.open(url)
        logger.info(r)



class SocksiPyConnection(httplib.HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport = None, rdns = True, username = None, password = None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        self.sock = data.spider2.crawler.trend.socksa.socksocket()
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


if __name__ == '__main__':
    url = 'https://www.lagou.com/gongsi/searchPosition.json?companyId=6502&pageSize=1000&positionFirstType=%E5%B8%82%E5%9C%BA%E4%B8%8E%E9%94%80%E5%94%AE&pageNo=1'
    # url = "http://www.sometime.com"
    # crawl = LagouJobCrawler()
    # crawl.crawler(url)a
    import urllib2
    import socket
    import socks

    socks.set_default_proxy(socks.PROXY_TYPE_SOCKS4, "180.173.153.98", 1080)
    socket.socket = socks.socksocket

    r= urllib2.urlopen("http://www.baidu.com/", timeout=20)  # All requests will pass through the SOCKS proxy
    print r.read()
    # import urllib2
    # import socksa
    # # from sockshandler import SocksiPyHandler
    #
    # opener = urllib2.build_opener(SocksiPyHandler(socksa.PROXY_TYPE_SOCKS4, ".17.153.98",1080))
    # headers = {
    #     "Cookie": 'user_trace_token=20161221142700-7aded37d-c746-11e6-841f-525400f775ce;LGUID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;LGRID=20161221142700-7aded745-c746-11e6-841f-525400f775ce;'}
    # request = urllib2.Request(url, headers=headers)
    # r= opener.open(request)  # All requests made by the opener will pass through the SOCKS proxy
    # print r.read()




