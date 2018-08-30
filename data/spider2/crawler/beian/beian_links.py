# -*- coding: utf-8 -*-
import os, sys
import datetime
import random
import json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import urllib, urllib2
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper, config, util

#logger
loghelper.init_logger("beian_links", stream=True)
logger = loghelper.get_logger("beian_links")

login_users = [
    {"name":"daffy","pwd":"daffy123456", "date":datetime.datetime.now()},
]

class BeianLinksCrawler(BaseCrawler.BaseCrawler):
    global login_users
    def __init__(self, timeout=90):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self,url, content):
        content = util.html_encode(content)

        if content.find("站长帮手网") > 0:
            return True
        if content.find("暂无数据") > 0:
            return True
        if content.find("为无效的域名格式") > 0:
            return True

        if content.find("HTTP Error 400. The request URL is invalid.") > 0:
            return True

        if content.find("您的查询量比较大") > 0:
            logger.info("您的查询量比较大")

            if len(login_users) < 100:
                while True:
                    opener = urllib2.build_opener()
                    username = util.id_generator(10)
                    data = {
                        "username":username,
                        "password": "ann123456",
                        "confirmpassword": "ann123456",
                        "opaction":"reg",
                        "qq":"",
                        "isqqopen":"1",
                        "email":"%s@mailinator.com" % username
                    }

                    data = urllib.urlencode(data)
                    logger.info(data)
                    headers = {
                        "Referer": "http://my.links.cn/reg.asp"
                    }
                    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
                    headers['User-Agent'] = user_agent

                    try:
                        request= urllib2.Request("http://my.links.cn/regpost.asp", data, headers)
                        r = opener.open(request, timeout=30)
                        try:
                            content = util.html_encode(r.read())
                            #logger.info(content)
                            login_users.append({"name":username, "pwd":"ann123456", "date":datetime.datetime.now()})
                            logger.info(login_users)
                            break
                        except Exception,e:
                            #pass
                            traceback.print_exc()
                    except Exception,e:
                        #pass
                        traceback.print_exc()
            return False

        #logger.info(content)
        return False

    def login(self, url, redirect=True):
        global login_users
        #logger.info(login_users)
        _login_users = []
        for user in login_users:
            date = user["date"]
            if (datetime.datetime.now() - date).seconds < 5*60:
                _login_users.append(user)
        login_users = _login_users
        if len(login_users) == 0:
            login_users.append({"name":"ann201","pwd":"ann123456", "date":datetime.datetime.now()})

        #logger.info(login_users)

        retries = 0
        while True:
            retries += 1
            if retries > 3:
                break

            self.init_http_session(url)

            while True:
                try:
                    idx = random.randint(0, len(login_users) - 1)
                    login_user = login_users[idx]
                    logger.info(login_user)
                    break
                except:
                    pass

            data = {
                "backurl":"	http://beian.links.cn",
                "bsave": "1",
                "opaction":"login",
                "username":login_user["name"],
                "password":login_user["pwd"],}

            data = urllib.urlencode(data)
            headers = {
                "Referer": "http://beian.links.cn"
            }
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
            headers['User-Agent'] = user_agent

            try:
                request= urllib2.Request("http://my.links.cn/checklogin.asp", data, headers)
                r = self.opener.open(request, timeout=30)
            except:
                continue

            try:
                content = util.html_encode(r.read())
            except:
                continue

            #logger.info(content)
            if content.find("loaduserinfo") > 0:
                break


    def parse_query(self, content):
        items = []
        d = pq(html.fromstring(content))
        trs = d("tr[bgcolor='#FFFFFF']")

        for tr in trs:
            item = {}
            e = pq(tr)
            tds = e('td')
            if len(tds) != 8:
                continue
            f = pq(tds[1])
            domain = f('a').eq(0).text().strip()
            #logger.info(domain)
            item["domain"] = domain
            f = pq(tds[2])
            organizer_name = f.text().strip()
            if organizer_name == '未备案':
                organizer_name = None   #TODO
                continue
            #logger.info(organizer_name)
            item["organizer"] = organizer_name
            item["organizerType"] = pq(tds[3]).text().strip()
            #item["mainBeianhao"] = pq(tds[4])('a').attr("href").replace("beianhao_","").replace(".html","")
            item["beianhao"] = pq(tds[4]).text().strip().replace(" ","")
            item["mainBeianhao"] = util.get_main_beianhao(item["beianhao"])
            item["websiteName"] = pq(tds[5]).text().strip()
            item["homepage"] = pq(tds[6]).text().strip()
            item["beianDate"] = datetime.datetime.strptime(pq(tds[7]).text().strip(),'%Y/%m/%d')

            # item["whoisChecked"] = True
            # whois_date = util.whois_creation_date(domain)
            # if whois_date is not None:
            #     if item["beianDate"] < whois_date:
            #         logger.info("%s may be expired!", domain)
            #         item["whoisExpire"] = "Y"
            #     else:
            #         item["whoisExpire"] = "N"
            # else:
            #     item["whoisExpire"] = "NA"
            items.append(item)

        return items

    def query_by_url(self, url):
        return []
        # retries = 0
        # items =[]
        # while True:
        #     result = self.crawl(url, agent=True)
        #     if result['get'] == 'success':
        #         content = util.html_encode(result["content"])
        #         #logger.info(content)
        #         items = self.parse_query(content)
        #         break
        #     if retries > 3:
        #         break
        #     retries += 1
        #
        # return items

    def query_by_domain(self, domain):
        url = "http://beian.links.cn/beian.asp?beiantype=domain&keywords=%s" % domain
        return self.query_by_url(url)


    def query_by_company_name(self,u_name):
        #logger.info("query_by_company_name: %s", u_name)
        url = "http://beian.links.cn/zbdwmc_%s.html" % urllib.quote(u_name.encode("utf-8"))
        return self.query_by_url(url)


    def query_by_main_beianhao(self,u_mainBeianhao):
        if u_mainBeianhao is None:
            return []
        if u_mainBeianhao.strip() == "":
            return []

        url = "http://beian.links.cn/beianhao_%s.html" % urllib.quote(u_mainBeianhao.encode("utf-8"))
        return self.query_by_url(url)

if __name__ == "__main__":
    crawler = BeianLinksCrawler()
    #domain = "92wy.com"
    #items = crawler.query_by_domain(domain)
    #logger.info(json.dumps(items, ensure_ascii=False, cls=util.CJsonEncoder))

    #name = u"上海汇翼信息科技有限公司"
    name = u"循宇信息技术（北京）有限公司"
    items = crawler.query_by_company_name(name)
    logger.info(json.dumps(items, ensure_ascii=False, cls=util.CJsonEncoder))

    '''
    beianhao = "豫ICP备15006536号"
    beianhao = "沪ICP备10220037号"
    items = crawler.query_by_main_beianhao(beianhao)
    logger.info(json.dumps(items, ensure_ascii=False, cls=util.CJsonEncoder))
    '''

    '''
    fp = open("sample_links1.html")
    content = fp.read()
    fp.close()
    content = util.html_encode(content)
    #logger.info(content)
    items = crawler.parse_query(content)
    logger.info(json.dumps(items, ensure_ascii=False, cls=util.CJsonEncoder))
    '''
