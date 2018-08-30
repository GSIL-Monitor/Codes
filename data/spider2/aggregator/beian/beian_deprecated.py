# -*- coding: utf-8 -*-
import os, sys
import time
import random
import urllib
import lxml.html
from tld import get_tld
from urlparse import urlsplit
import tldextract
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import util
import db
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../crawler'))
import BaseCrawler

#logger
loghelper.init_logger("beian", stream=True)
logger = loghelper.get_logger("beian")

login_users = [
    {"name":"daffy","pwd":"daffy123456"}
]

IDS = None
RUNNING = 0

class BeianCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        return True

    #实现
    '''
    def login(self, url, redirect):
        while True:
            self.init_http_session(url, redirect)
            idx = random.randint(0, len(login_users)-1)
            login_user = login_users[idx]

            data = {
                    "backurl":"	http://beian.links.cn",
                    "bsave": "1",
                    "opaction":"login",
                    "username":login_user["name"],
                    "password":login_user["pwd"],}
            postdata = urllib.urlencode(data)
            headers = {"Content-Type":"application/x-www-form-urlencoded"}
            result = self.crawl("http://my.links.cn/checklogin.asp", headers=headers, postdata=postdata, login=False)
            if result['get'] == 'success':
                try:
                    content = result["content"].decode("gb18030")
                except:
                    pass
                #logger.info(content)
                if content.find("<script>loaduserinfo();</script>") != -1:
                    return True
                else:
                    logger.info("loaduserinfo not found!")
    '''

def get_main_beianhao(beianhao):
    strs = beianhao.split("-")
    if len(strs[-1]) <=3:
        del strs[-1]
    main_beianhao = "-".join(strs)
    return main_beianhao


def parse_query(source_company_id,html):
    conn = db.connect_torndb()

    doc = lxml.html.fromstring(html)
    dms = doc.xpath("//tr[@bgcolor='#FFFFFF']")
    cnt = 0
    for dm in dms:
        try:
            temps = dm.xpath("td")
            if len(temps) == 3:
                #未备案
                idx = temps[0].xpath("text()")[0].strip()
                domain_name = temps[1].xpath("a/text()")[0].strip()
                logger.info("%s 未备案", domain_name)
                domain = conn.get("select * from source_domain where sourceCompanyId=%s and domain=%s limit 1",
                                  source_company_id, domain_name)
                if domain is None:
                    conn.insert("insert source_domain(sourceCompanyId,domain,createTime,modifyTime) \
                                values(%s,%s,now(),now())",
                            source_company_id,domain_name)
                cnt += 1
                continue

            if len(temps) < 8:
                continue

            idx = temps[0].xpath("text()")[0].strip()
            domain_name = temps[1].xpath("a/text()")[0].strip()

            expire = 'N'
            dels = dm.xpath("td/del")
            if len(dels) >=6:
                expire = 'Y'

            if expire == 'N':
                temp = temps[2].xpath("a/font/text()")
                if len(temp) > 0:
                    organizer_name = temp[0].strip()
                else:
                    temp = temps[2].xpath("a/text()")
                    if len(temp) > 0:
                        organizer_name = temp[0].strip()
                organizer_type = temps[3].xpath("text()")[0].strip()
                beianhao = temps[4].xpath("a/text()")[0].strip()
                if beianhao == "":
                    beianhao = temps[4].xpath("a/font/text()")[0].strip() + temps[4].xpath("a/text()")[1].strip()
                website_name = temps[5].xpath("a/text()")[0].strip()
                website_homepage = temps[6].xpath("text()")[0].strip()
                review_date = temps[7].xpath("text()")[0].strip()
            else:
                organizer_name = dels[0].xpath("a/text()")[0].strip()
                organizer_type = dels[1].xpath("text()")[0].strip()
                beianhao = dels[2].xpath("a/text()")[0].strip()

                website_name = dels[3].xpath("a/text()")[0].strip()
                website_homepage = dels[4].xpath("text()")[0].strip()
                review_date = dels[5].xpath("text()")[0].strip()
            main_beianhao = get_main_beianhao(beianhao)
            organizer_name = util.norm_company_name(organizer_name)
            logger.info("%s, %s, %s, %s, %s, %s, %s, %s" %
                        (idx, domain_name, organizer_name, organizer_type, beianhao,website_name,website_homepage,review_date))

            domain = conn.get("select * from source_domain where sourceCompanyId=%s and domain=%s", source_company_id, domain_name)
            if domain is None:
                conn.insert("insert source_domain(sourceCompanyId,domain,organizer,organizerType,\
                                        beianhao,mainBeianhao,websiteName,homepage,beianDate,expire,\
                                        createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())",
                            source_company_id,domain_name,organizer_name,organizer_type,
                            beianhao,main_beianhao,website_name,website_homepage,review_date,expire
                            )
            else:
                pass
            cnt += 1
        except Exception,ex:
            logger.exception(ex)

    conn.close()
    if cnt == 0:
        #logger.info(html)
        pass

def query_by_company_name(crawler, source_company_id, name):
    if name is None or name == "":
        return True

    #不是正常的中国公司名
    if name.find(".") != -1:
        return True

    name = name.replace("_","")
    idx = name.rfind(u"公司")
    if idx != -1:
        name = name[:(idx+len(u"公司"))]

    url = "http://beian.links.cn/zbdwmc_%s.html" % urllib.quote(name.encode("utf-8"))
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            try:
                content = result["content"].decode("gb18030")
                #logger.info(content)
                if content.find(u"工具简介") != -1 and content.find("<script>loaduserinfo();</script>") != -1:
                    break
            except:
                pass

    parse_query(source_company_id, content)

    return True


def query_by_domain(crawler, source_company_id, website):
    if website is None or website == "":
        return True

    s = urlsplit(website)
    if s.query != '' or s.fragment != '':
        return True
    if s.path != '' and s.path != '/':
        return True

    s = tldextract.extract(website)
    if s.subdomain != "www" and s.subdomain != "m" and s.subdomain != "":
        return True

    try:
        domain = get_tld(website)
    except:
        return True

    url = "http://beian.links.cn/beian.asp?beiantype=domain&keywords=%s" % domain
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            try:
                content = result["content"].decode("gb18030")
                #logger.info(content)
                if content.find(u"最近查询：") != -1 and content.find("<script>loaduserinfo();</script>") != -1:
                    break
            except:
                pass

    parse_query(source_company_id, content)

    return True


def query_by_beianhao(crawler, source_company_id, beianhao):
    if beianhao is None or beianhao == "":
        return True

    url = "http://beian.links.cn/beianhao_%s.html" % urllib.quote(beianhao.encode("utf-8"))
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            try:
                content = result["content"].decode("gb18030")
                #logger.info(content)
                if content.find(u"工具简介") != -1 and content.find("<script>loaduserinfo();</script>") != -1:
                    break
            except:
                pass

    parse_query(source_company_id, content)

    return True


def process(crawler, source_company_id):
    logger.info(source_company_id)
    conn = db.connect_torndb()
    conn.execute("delete from source_domain where sourceCompanyId=%s", source_company_id)
    source_company = conn.get("select * from source_company where id=%s", source_company_id)

    #check by company name
    flag = query_by_company_name(crawler, source_company_id,source_company["fullName"])

    #check by website
    artifacts = conn.query("select * from source_artifact where sourceCompanyId=%s and type=4010", source_company_id)
    for artifact in artifacts:
        link = artifact["link"]
        logger.info(link)
        flag = query_by_domain(crawler, source_company_id, link)

    #check by beianhao
    main_beianhaos = conn.query("select distinct mainBeianhao from source_domain where sourceCompanyId=%s", source_company_id)
    for main_beianhao in main_beianhaos:
        flag = query_by_beianhao(crawler, source_company_id, main_beianhao["mainBeianhao"])

    s_status = conn.get("select * from source_company_aggregate_status where type=45010 and sourceCompanyId=%s", source_company_id)
    if s_status is not None:
        conn.update("update source_company_aggregate_status set status=46020, modifyTime=now() \
                    where sourceCompanyId=%s and type=45010",
                source_company_id)
    else:
        conn.insert("insert source_company_aggregate_status(sourceCompanyId, type ,status, createTime) \
                    values(%s,%s,%s,now())",
                    source_company_id, 45010, 46020)
    conn.close()
    return True


def run(crawler, event):
    global RUNNING
    if len(IDS) == 0:
        if RUNNING == 0:
            event.set()
        logger.info("RUNNING=%s", RUNNING)
        return

    RUNNING += 1
    source_company_id = IDS.pop(0)
    logger.info("RUNNING=%s", RUNNING)

    try:
        process(crawler, source_company_id)
    except Exception,ex:
        logger.exception(ex)

    RUNNING -= 1
    gevent.spawn(run, crawler, event)


if __name__ == '__main__':
    concurrent_num = 10

    while True:
        logger.info("beian start...")
        IDS = []
        EVENT = Event()
        conn = db.connect_torndb()
        #目前仅处理新产品!
        scs = conn.query("select sc.id as sourceCompanyId from source_company sc \
                        left join source_company_aggregate_status status on sc.id=status.sourceCompanyId \
                        where sc.type=41020 and \
                        (status.status is null or status.status!=46020) and \
                         (status.type is null or status.type=45010)")
        conn.close()

        for sc in scs:
            IDS.append(sc["sourceCompanyId"])
        logger.info("count=%s", len(IDS))

        for i in range(concurrent_num):
            gevent.spawn(run, BeianCrawler(), EVENT)

        EVENT.wait()
        logger.info("beian end.")

        gevent.sleep(60)