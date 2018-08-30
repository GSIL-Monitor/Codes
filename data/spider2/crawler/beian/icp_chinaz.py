# -*- coding: utf-8 -*-
import os, sys,datetime
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
loghelper.init_logger("crawler_beian_icp", stream=True)
logger = loghelper.get_logger("crawler_beian_icp")

DOMAIN=[]

class IcpchinazCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " "+ url)

        if title.find("备案查询 - 站长工具") >= 0:
            return True

        if content.find("发生了系统错误, 错误信息已经被记录") >= 0:
            return True

        #logger.info(content)
        return False


    def has_content(self, content):
        d = pq(html.fromstring(content))
        if content.find("主办单位名称") ==-1:
            return False
        if content.find("网站备案/许可证号") ==-1:
            return False
        return True



    def parse_query(self, content):
        items = []
        if self.has_content(content):
            #logger.info(content)
            d = pq(html.fromstring(content.decode("utf-8")))
            infos = d('div.pr> ul.bor-t1s> li')
            #logger.info(infos)
            (organizer,organizertype,beianhao,mainBeianhao,websitename,homepage,beianDate)=(None,None,None,None,None,None,None)

            for li in infos:
                d1 = pq(li)
                info = d1('li> p').text()
                infos = info.split(" ")
                if d1('li> span').text() == "主办单位名称":
                    organizer = infos[0]
                    #logger.info(organizer)
                if d1('li> span').text() == "主办单位性质":
                    organizertype = infos[0]
                    #logger.info(organizertype)
                if d1('li> span').text() == "网站备案/许可证号":
                    beianhao = infos[0].replace(" ", "")
                    #temp = beianhao.split("-")
                    #mainBeianhao = temp[0]
                    mainBeianhao = util.get_main_beianhao(beianhao)

                if d1('li> span').text() == "网站名称":
                    websitename = infos[0]

                if d1('li> span').text() == "网站首页网址":
                    homepages0 = info
                    #domain = homepage.replace("www.","")

                if d1('li> span').text() == "审核时间":
                    datestr = infos[0]
                    beianDate = datetime.datetime.strptime(datestr,"%Y-%m-%d")

            for homepage in homepages0.split(" "):
                domain = homepage.replace("www.", "").strip()
                item = {
                        "domain": domain,
                        "organizer": organizer,
                        "organizerType": organizertype,
                        "beianhao": beianhao,
                        "mainBeianhao": mainBeianhao,
                        "websiteName": websitename,
                        "homepage": homepage,
                        "beianDate": beianDate,

                }
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

            try:

                trs = d('tbody#result_table> tr')

                for tr in trs:

                    d2 = pq(tr)
                    #logger.info(d2)
                    tds = d2('td')
                    #logger.info(len(tds))
                    if len(tds)!=4:
                        continue
                    beianhao_new = pq(tds[0]).text().strip().replace(" ","")
                    websiteName_new = pq(tds[1]).text().strip()
                    homepages_new= pq(tds[2]).text()
                    #domain_new = homepage_new.replace("www.", "")
                    datestr_new= pq(tds[3]).text().strip()
                    beianDate_new = datetime.datetime.strptime(datestr_new, "%Y-%m-%d")

                    if beianhao_new != beianhao:

                        for homepage_new in homepages_new.split(" "):
                            homepage_new = homepage_new.strip()
                            domain_new = homepage_new.replace("www.", "")

                            item_new = {
                                "domain": domain_new,
                                "organizer": organizer,
                                "organizerType": organizertype,
                                "beianhao": beianhao_new,
                                "mainBeianhao": mainBeianhao,
                                "websiteName": websiteName_new,
                                "homepage": homepage_new,
                                "beianDate": beianDate_new,

                            }
                            # item_new["whoisChecked"] = True
                            # whois_date = util.whois_creation_date(domain_new)
                            # if whois_date is not None:
                            #     if item["beianDate"] < whois_date:
                            #         logger.info("%s may be expired!", domain_new)
                            #         item["whoisExpire"] = "Y"
                            #     else:
                            #         item["whoisExpire"] = "N"
                            # else:
                            #     item["whoisExpire"] = "NA"
                            #for i in item_new:
                                #logger.info("%s->%s",i,item_new[i])
                            items.append(item_new)



            except:
                pass


        return items



    def query_by_url(self, url, data):
        while True:
            logger.info(data)
            result = self.crawl(url, postdata=data, agent=True)
            if result['get'] == 'success':
                #logger.info(result["content"])
                items = self.parse_query(result["content"])
                return items
                break



    def query_by_domain(self, domain):
        url = "http://icp.chinaz.com"
        data = {
            "hidesel": "网站域名",
            "s": domain,
        }
        data = urllib.urlencode(data)
        return self.query_by_url(url, data)

    def query_by_main_beianhao(self, mainBeianhao):
        logger.info("mainBeianhao: %s", mainBeianhao)
        url = "http://icp.chinaz.com"
        data = {
            "hidesel": "备案编号",
            "s": mainBeianhao.encode("utf-8"),
        }
        data = urllib.urlencode(data)
        logger.info(data)
        return self.query_by_url(url, data)


if __name__ == "__main__":
    crawler = IcpchinazCrawler()
    domain = "teambition.com"
    # domain = "20085.com"
    items = crawler.query_by_domain(domain)
    for item in items:
        logger.info(json.dumps(item, ensure_ascii=False, cls=util.CJsonEncoder))


    #beianhao = "沪ICP备11014111号"
    beianhao = "沪ICP备10220037号"
    items = crawler.query_by_main_beianhao(beianhao)
    logger.info(json.dumps(items, ensure_ascii=False, cls=util.CJsonEncoder))

