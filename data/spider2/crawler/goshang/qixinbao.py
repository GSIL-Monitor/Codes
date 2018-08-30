# -*- coding: utf-8 -*-
import os, sys,datetime,time
from lxml import html
from pyquery import PyQuery as pq
import urllib
import urllib2
import json
import httplib
import socks
import cookielib
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import loghelper
import util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

#logger
loghelper.init_logger("crawler_gonshang_qixinbao", stream=True)
logger = loghelper.get_logger("crawler_gonshang_qixinbao")


class SocksiPyConnection(httplib.HTTPConnection):
    def __init__(self, proxytype, proxyaddr, proxyport = None, rdns = True, username = None, password = None, *args, **kwargs):
        self.proxyargs = (proxytype, proxyaddr, proxyport, rdns, username, password)
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        self.sock = socks.socksocket()
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


class QixinbaoSearchCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)
        self.socks_proxy = None

    # 实现
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if content.find("完成上面的验证后继续使用") > 0:
            return False
        if title.find("启信宝") == -1:
            return False
        if title.find("全国企业工商信息查询|企业信息查询|启信宝，全国企业信用信息查询") > 0:
            return False

        return True


    def has_content(self, content):
        d = pq(html.fromstring(content))
        #if content.find("很抱歉，没有找到相关结果") == -1:
        #    return False
        return True

    def get_proxy(self):
        proxy = {"$or":[{'type': 'socks4'},{'type': 'socks5'}], 'anonymity': 'high'}
        proxy_ip = None
        while proxy_ip is None:
            proxy_ip = proxy_pool.get_single_proxy(proxy)
            if proxy_ip is None:
                time.sleep(30)
        return proxy_ip

    def init_http_session(self, url, redirect=True):
        if self.opener is not None:
            self.opener.close()

        self.socks_proxy = self.get_proxy()
        logger.info("Proxy: %s -- %s:%s" ,self.socks_proxy["type"], self.socks_proxy["ip"], self.socks_proxy["port"])

        self.cookiejar = cookielib.CookieJar()

        if self.socks_proxy["type"] == "socks4":
            handlers = [SocksiPyHandler(socks.PROXY_TYPE_SOCKS4, self.socks_proxy["ip"], self.socks_proxy["port"]),
                        urllib2.HTTPCookieProcessor(self.cookiejar)
                    ]
        else:
            handlers = [SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, self.socks_proxy["ip"], self.socks_proxy["port"]),
                        urllib2.HTTPCookieProcessor(self.cookiejar)
                        ]


        self.opener = urllib2.build_opener(*handlers)

    def parse_query(self, content):
        items = []
        if self.has_content(content):
            #logger.info(content)
            d = pq(html.fromstring(content.decode("utf-8")))

            #infos = d('a.search-result-company-name')
            infos = d('div.search-ent-row')
            for info in infos:
                #Only get info when href and company name is real
                try:
                    d = pq(info)
                    #logger.info(d)
                    href=d('div.is-follow').attr('ms-attr-eid').replace("\'","")
                    link = "http://www.qixin.com/company/%s" % href
                    company = d('a.search-result-company-name').text().replace(" ", "")

                    if company.find("name") >= 0:
                        continue


                    item = {
                        "company_name" : company,
                        "link": link,
                    }
                    for i in item:
                        logger.info("%s->%s",i,item[i])

                    items.append(item)
                except:
                    pass

        return items



    def query_by_url(self, url):
        while True:
            #logger.info(url)
            result = self.crawl(url)
            if result['get'] == 'success':
                #logger.info(result["content"])
                items = self.parse_query(result["content"])
                return items
                break


    def query_by_company(self, company):
        data = {
            "key": company,
            "type": "enterprise",
            "method": "all"
        }
        data = urllib.urlencode(data)
        url="http://www.qixin.com/search?%s" % data
        return self.query_by_url(url)


class QixinbaoCompanyCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if content.find("系统繁忙请稍后再试") > 0:
            return True

        if content.find("完成上面的验证后继续使用") > 0:
            return False
        if title.find("全国企业工商信息查询|企业信息查询|启信宝，全国企业信用信息查询") > 0:
            return False
        if title.find("启信宝") == -1:
            return False
        return True

    def has_content(self, content):
        d = pq(html.fromstring(content))
        if content.find("组织机构代码") == -1:
            return False
        if content.find("注册资本") == -1:
            return False
        return True

    def parse_query(self, content):
        items = []
        if self.has_content(content):
            #logger.info(content)
            d = pq(html.fromstring(content.decode("utf-8")))
            item = {}

            item["name"] = d('div.company-name').text().strip()


            tds_basic = d('div.basic-info> div> table> tr> td')

            item["socialCreditCode"] = pq(tds_basic[1]).text().replace("-", "").strip()
            item["instituteCode"] = pq(tds_basic[3]).text().replace("-", "").strip()
            item["regNumber"] = pq(tds_basic[5]).text().replace("-", "").strip()
            item["regStatus"] = pq(tds_basic[7]).text().replace("-", "").strip()
            item["CompanyOrgType"] = pq(tds_basic[9]).text().replace("-", "").strip()
            establishTime = pq(tds_basic[11]).text().strip()
            try:
                item["establishTime"] = datetime.datetime.strptime(establishTime, "%Y-%m-%d")
            except:
                # item["establishTime"] = establishTime
                item["establishTime"] = None
            item["legalPersonName"] = pq(tds_basic[13])('a').eq(0).text().replace("-", "").strip()
            periods = pq(tds_basic[15]).text().strip().split(" - ")
            if len(periods) == 2:
                if periods[0] != "-":
                    item["fromTime"] = datetime.datetime.strptime(periods[0], "%Y-%m-%d")
                if periods[1] != "-" and periods[1] != "长期" and periods[1] != "永续经营":
                    try:
                        item["toTime"] = datetime.datetime.strptime(periods[1], "%Y-%m-%d")
                    except:
                        pass
            item["regCapital"] = pq(tds_basic[17]).text().replace("-", "").strip()
            item["regInstitute"] = pq(tds_basic[21]).text().replace("-", "").strip()
            item["regLocation"] = pq(tds_basic[23]).text().replace("-", "").strip()
            item["businessScope"] = pq(tds_basic[25]).text().replace("-", "").strip()

            divs = d('div.panel-default> div.panel-body')

            members = []
            investors = []
            for div in divs:
                text = pq(div).text()
                #check investor
                if text.find("股东") >= 0:
                    trs_inv = pq(div)('tbody> tr')
                    for tr in trs_inv:
                        investor = {}
                        investor["type"] = pq(tr)('td').eq(0).text().strip()
                        investor["name"] = pq(tr)('td').eq(1).text().strip()

                        investors.append(investor)
                #check member
                if text.find("董事") >= 0:
                    lis = pq(div)('ul.major-person-list> li')
                    for li in lis:
                        print
                        member = {}
                        member["name"] = pq(li)('span.job-title').text().strip()
                        member["position"] = pq(li)('span.company-basic-info-name').text().strip()

                        members.append(member)

            #logger.info(json.dumps(members, ensure_ascii=False))
            #logger.info(json.dumps(investors, ensure_ascii=False))

            item["members"] = members
            item["investors"] = investors

            items.append(item)

        else:
            logger.info(content)

        return items

    def query_by_url(self, url):
        while True:
            # logger.info(url)
            result = self.crawl(url)
            if result['get'] == 'success':
                # logger.info(result["content"])
                items = self.parse_query(result["content"])
                return items
                break

    def query_by_company_url(self, company_url):
        url = company_url
        return self.query_by_url(url)


if __name__ == "__main__":
    crawler = QixinbaoSearchCrawler()
    company = "上海汇翼信息科技有限公司"
    #items = crawler.query_by_company(company)
    #logger.info(json.dumps(items, ensure_ascii=False, cls=util.CJsonEncoder))

    crawler = QixinbaoCompanyCrawler()
    #company_url = "http://www.qixin.com/company/5f9992b2-c37c-4cb2-a609-94f3687c6a88"
    company_url = "http://www.qixin.com/company/acfc641c-b43c-4781-998f-36866411e641"
    items = crawler.query_by_company_url(company_url)
    if len(items) ==1:
        logger.info(json.dumps(items[0], ensure_ascii=False, cls=util.CJsonEncoder))
    else:
        logger.info(items)