# -*- coding: utf-8 -*-
import os, sys,datetime, time
import random, math
import urllib
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import pycurl
import StringIO


reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("sogou_index", stream=True)
logger = loghelper.get_logger("sogou_index")


columns = [
    {"name": "真格基金"},


]

def get_proxy():
    proxy = {"$or": [{'type': 'socks4'}, {'type': 'socks5'}], 'anonymity': 'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            logger.info("No proxy !!!!!!!!!!!!!!!!!!!")
            time.sleep(30)
    return proxy_ip


def is_crawl_success(content, keyword):
    if content.find("</html>") == -1:
        return False
    d = pq(html.fromstring(content.decode("utf-8")))
    logger.info(content)
    title = d('head> title').text().strip()
    if title.find("搜狗指数") >= 0 and content.find(keyword)>=0:
        logger.info("COOOOOOOOOOOOOOR")
        return True
    return False


def get():

    mongo = db.connect_mongo()

    for column in columns:
        if column.has_key("name") is True:
            logger.info("crawler: %s,%s", column["name"],urllib.urlencode({"query":column["name"]}))
            link = "http://zhishu.sogou.com/index/media/wechat?%s&timePeriodType=MONTH&dataType=" \
                   "MEDIA_WECHAT&queryType=INPUT" \
                   % urllib.urlencode({"kwdNamesStr":column["name"]})
            hdata = {"Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     "Host": 'zhishu.sogou.com',
                     "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
                     "Accept-Language": 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
                    }
            cnt = get_article_links(column["name"], hdata, link)

    mongo.close()


def get_article_links(keyword, data, nr_link):
    cnt1 = 0
    while True:

        socks = get_proxy()
        logger.info("socks: %s, %s",socks["ip"], socks["port"])
        HTTPHEADER = []
        for h in data:
            HTTPHEADER.append(h+":"+data[h])
        b = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, nr_link)
        c.setopt(pycurl.HTTPHEADER, HTTPHEADER)
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 1)
        c.setopt(pycurl.CONNECTTIMEOUT, 10)
        c.setopt(pycurl.TIMEOUT, 20)
        c.setopt(pycurl.PROXY, str(socks["ip"])+":"+str(socks["port"]))
        if socks["http_type"].lower() == "socks4":
            c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
        else:
            c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        try:
            c.perform()
            status = c.getinfo(c.HTTP_CODE)
            logger.info(status)
            bbody = b.getvalue()
            # logger.info(bbody)
            c.close()
            if status == 200 and bbody is not None and len(bbody) > 0:
                if is_crawl_success(bbody, keyword):
                    try:
                        cnt1 = process(bbody, keyword, nr_link)
                    except:
                        logger.info("wrong wrong here")
                    break
                # pass
        except Exception, e:
            logger.info("wrong")
            logger.info(e)
            c.close()
            # break

        # break
    return cnt1

def process(content, keyword, link):
    # j = json.loads(content)
    # infos = j["value"]
    logger.info(content)
    cnt = 0
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    logger.info("title: %s", title)

    ptype = None

    mongo = db.connect_mongo()
    collection = mongo.trend.index
    if link.find("MEDIA_WECHAT") >= 0:
        source = 13651 #搜狗微信热度
        sourceDesc = "搜狗微信热度"
        if collection.find_one({"source": source, "keyword": keyword}) is None:
            ptype = 1
        else:
            ptype = 2

    if ptype is None: return

    if ptype == 1:
        logger.info("here")
        r = "root.SG.wholedata\s=\s(.*)?\;.*\}\(this"
    else:
        r = "root.SG.data = (.*?);root.SG.wholedata"
    try:
        result = util.re_get_result(r, content)
    except:
        logger.info("wwwwwww")
        return

    logger.info(result)
    (b,) = result

    logger.info(b)
    base = json.loads(b, strict=False)
    for pv in base["pvList"]:
        logger.info(json.dumps(pv, ensure_ascii=False, cls=util.CJsonEncoder))

    mongo.close()
    return cnt


if __name__ == "__main__":
    # while True:
        get()
        # time.sleep(60*60)
