# -*- coding: utf-8 -*-
import random, math
import urllib
import os, sys, datetime, re, json, time
from lxml import html
from pyquery import PyQuery as pq
import pycurl
import StringIO


reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../news'))
import Wechatcrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import proxy_pool


#logger
loghelper.init_logger("sogou_news", stream=True)
logger = loghelper.get_logger("sogou_news")
PS = []
PROXY ={
    "PROXY": None,
    "TIMES": 0
}
columns = [
    {"keyword": 'A\+轮', "max": [1]},
    {"keyword": 'B\+轮', "max": [1]},
    # {"keyword": 'C\+轮', "max": [1]},
    {"investor": "启明创投", "keywords": ["启明","投资"], "max":[1],"wxid":"oIWsFtx_lV2JEYP6D6oGzdrrqVmQ"},
    {"investor": "红杉汇", "keywords": ["红杉","融资"], "max":[1],"wxid":"oIWsFt2Zjv8Bu4IZ8Q_iaAenHhWs"},
    {"investor": "IDG资本", "keywords": ["IDG","融资"], "max":[1],"wxid":"oIWsFt45dA9zzC0JyIpOIxD0-iUU"},
    {"investor": "经纬创投", "keywords": ["经纬","融资"], "max":[1],"wxid":"oIWsFt6vpRBJ_F8r9cxZpPVvjwBA"},
    {"investor": "真格基金", "keywords": ["真格","融资"], "max":[1],"wxid":"oIWsFt6OXLcFtT7tA3CFVwkxlgdc"},
    {"investor": "创新工场", "keywords": ["融资","投资"], "max":[1],"wxid":"oIWsFt9ERP5nv-GPUOVKo_hv0rQ0"},
    {"investor": "华兴有个Alpha", "keywords": ["投资","融资"], "max":[1],"wxid":"oIWsFt_1QHLeIj9brwA2LaB4y4bo"},
    {"investor": "梅花天使创投", "keywords": ["投资","融资"], "max":[1],"wxid":"oIWsFt7AZ97bF7xsdhNW5IfF9v2A"},
    {"investor": "达晨创投", "keywords": ["投资","融资"], "max":[1],"wxid":"oIWsFtwmpfDIjaNpaYlUJ5si8jE8"},
    {"investor": "洪泰帮", "keywords": ["洪泰","融资"], "max":[1],"wxid":"oIWsFtzUDmUIvIH1X2pcLJBXIT64"},
    {"investor": "云启资本YUNQI", "keywords": ["投资","融资","云启"], "max":[1],"wxid":"oIWsFt_oAB3KS5ZTLJaQ5kG53jzg"},
    {"investor": "顺为资本", "keywords": ["顺为","融资"], "max":[1],"wxid":"oIWsFt6Ejw_Jpw7ppavGwdB8pHqo"},
    {"investor": "凯辉通讯", "keywords": ["凯辉", "融资"], "max": [1], "wxid": "oIWsFt7rupKgzjyrGsJwQwne8wN4"},
    {"investor": "阿米巴资本", "keywords": ["阿米巴", "融资"], "max": [1], "wxid": "oIWsFt3Yb-u2xruqPxUR2L6thzjM"},
    {"investor": "创投分析", "keywords": ["投资"], "max": [1], "wxid": "oIWsFtx7_0yhlA7zJXhR9sqzfsSs"},
    {"investor": "黑哨兵", "keywords": ["投资"], "max": [1], "wxid": "oIWsFt98KP31ADvuTsGiOL-MXIPA"},
    {"keyword": "天使轮", "max": [1,2]},
    {"keyword": "战略投资", "max": [1,2]},
    {"keyword": "A轮", "max": [1,2]},
    {"keyword": "B轮", "max": [1,2]},
    {"keyword": "C轮", "max": [1,2]},
    {"keyword": "D轮", "max": [1,2]},
    {"keyword": "种子轮", "max": [1,2]},
    {"keyword": "领投", "max": [1,2]},
    {"keyword": "获投", "max": [1]},
    {"keyword": "融资", "max": [1]},
    {"keyword": "千万 融资", "max": [1]},
    {"keyword": "债权融资", "max": [1]},
    {"keyword": "竺道", "max": [1]},


]


def get_ps():
    rule = {'type': 'SOCKS4', 'anonymous': 'high'}
    proxy_ips = proxy_pool.get_single_proxy_x(rule, 1000)
    # PS = proxy_ips
    del PS[:]
    for pi in proxy_ips:
        PS.append(pi)

def get_proxy():
    proxy = {"$or": [{'type': 'socks4'}, {'type': 'socks3'}], 'anonymity': 'high'}
    proxy_ip = None
    while proxy_ip is None:
        proxy_ip = proxy_pool.get_single_proxy(proxy)
        if proxy_ip is None:
            logger.info("No proxy !!!!!!!!!!!!!!!!!!!")
            time.sleep(30)
    return proxy_ip

def get_proxy_http():
    proxy = {'type': 'http', 'anonymity': 'high'}
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
    # logger.info(content)
    title = d('head> title').text().strip()
    if title.find("搜狗微信搜索") >= 0 and title.find(keyword)>=0:
        logger.info("COOOOOOOOOOOOOOR")
        return True
    return False

class wechat(Wechatcrawler.NewsDownloader):
    def __init__(self, TYPE=60005, SOURCE=13847, RETRY=20):
        Wechatcrawler.NewsDownloader.__init__(self, TYPE = TYPE, SOURCE=SOURCE, RETRY=RETRY)



def get(hour):
    # crawler =  nrCrawler()
    wechatcrawler = Wechatcrawler.WechatCrawler()
    wechatprocess = wechat()
    mongo = db.connect_mongo()

    for column in columns:
        for nday in column["max"]:
            if column.has_key("investor") is False:
                logger.info("crawler: %s,%s, %s", column["keyword"],urllib.urlencode({"query":column["keyword"]}), nday)
                if nday == 1:
                    link = "http://weixin.sogou.com/weixin?type=2&ie=utf8&%s&tsn=1&ft=&et=&interation=&wxid=&usip=" \
                       % urllib.urlencode({"query":column["keyword"]})
                    # link = "http://weixin.sogou.com/weixin?type=2&s_from=input&%s&ie=utf8&_sug_=n&_sug_type_=" \
                    #      % urllib.urlencode({"query":column["keyword"]})
                else:
                    link = 'http://weixin.sogou.com/weixin?usip=&%s&ft=&tsn=1&et=&interation=&type=2&wxid=&page=%s&ie=utf8' \
                           % (urllib.urlencode({"query": column["keyword"]}), nday)
                hdata = {"Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                         "Host": 'weixin.sogou.com',
                         "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
                         # "Referer": 'http://weixin.sogou.com/weixin?type=2&s_from=input&%s&ie=utf8&_sug_=n&_sug_type_=1'
                         #          % urllib.urlencode({"query":column["keyword"]}),
                         "Referer": 'http://weixin.sogou.com/weixin?type=2&%s&ie=utf8&s_from=input&_sug_=n&_sug_type_=1' % urllib.urlencode({"query": column["keyword"]}),
                         # "Referer": 'http://weixin.sogou.com/weixin?type=2&%s&ie=utf8&s_from=input&_sug_=n&_sug_type_=1'
                         }
                logger.info("link: %s", link)
                hhdata = ""
                for h in hdata:
                    hhdata += "-H \'" + h + ": " + hdata[h] + "\' "
                logger.info("hdata: %s", hhdata)
                cnt = get_article_links(column["keyword"], hdata, link, wechatcrawler, wechatprocess, hour)
                time.sleep(45)
            else:
                if hour in [15]:

                    for keyword  in column["keywords"]:
                        logger.info("crawler: %s,%s, %s", keyword, urllib.urlencode({"query": keyword}),
                                    column["investor"])
                        link = "http://weixin.sogou.com/weixin?type=2&ie=utf8&%s&tsn=1&ft=&et=&interation=" \
                               "&wxid=%s&%s" \
                               % (urllib.urlencode({"query": keyword}),column["wxid"],
                                  urllib.urlencode({"usip": column["investor"]}))
                        hdata = {"Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                 "Host": 'weixin.sogou.com',
                                 "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko/20100101 Firefox/60.0',
                                 "Referer": "http://weixin.sogou.com/weixin?type=2&ie=utf8&%s&tsn=1&ft=&et=&interation=&wxid=%s&%s" \
                                            % (urllib.urlencode({"query": keyword}),column["wxid"],
                                               urllib.urlencode({"usip": column["investor"]}))}
                        cnt = get_article_links(keyword, hdata, link, wechatcrawler, wechatprocess, hour)
                        time.sleep(45)
        #     if cnt>0:
        #         time.sleep(3*60)
        #     else:
        #         time.sleep(1*60)
        # time.sleep(5*60)
    del PS[:]
    mongo.close()


def get_article_links(keyword, data, nr_link, wechatcrawler, wechatprocess, hour):
    cnt1 = 0
    while True:
        logger.info(PROXY)
        # result = crawler.crawl(nr_link, headers=data)
        # if result['get'] == 'success':
        #     logger.info(result['content'])
        #     # logger.info(result["redirect_url"])
        #     try:
        #         pass
        #          # cnt = process(result['content'], wechatcrawler, wechatprocess)
        #     except Exception, ex:
        #         logger.exception(ex)
        # r = requests.get(nr_link, headers=data,
        #                  proxies=dict(http='socks5h://218.201.98.196:1080',
        #                               https='socks5h://218.201.98.196:1080')
        #                  )
        # logger.info(r.text)
        if PROXY["PROXY"] is not None and PROXY["TIMES"] < 4:
            socks = PROXY["PROXY"]
            logger.info("socks SAME: %s, %s, %s", socks["ip"], socks["port"], PROXY['TIMES'])
        else:
            PROXY["PROXY"] = None
            PROXY["TIMES"] = 0
            if len(PS) == 0:
                get_ps()
            socks = PS.pop(0)

            # if hour in [12,15,18, 9, 16]:
            #     socks = get_proxy()
            #     logger.info("socks %s: %s, %s",socks["type"], socks["ip"], socks["port"])
            # else:
            #     socks = get_proxy_http()
            #     logger.info("http: %s, %s", socks["ip"], socks["port"])

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
        # if socks["http_type"].lower() == "socks4":
        #     c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
        # elif socks["http_type"].lower() == "socks5":
        #     c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        if socks["type"] == "SOCKS4":
            c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
        elif socks["type"] == "SOCKS5":
            c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        try:
            c.perform()
            status = c.getinfo(c.HTTP_CODE)
            logger.info(status)
            bbody = b.getvalue()
            logger.info(bbody)
            c.close()
            if status == 200 and bbody is not None and len(bbody) > 0:
                if is_crawl_success(bbody, keyword):
                    cnt1 = process(bbody, wechatcrawler, wechatprocess)
                    PROXY["PROXY"] = socks

                    PROXY["TIMES"] = PROXY["TIMES"] + 1
                    break
                # pass
        except Exception, e:
            logger.info(e)
            PROXY["PROXY"] = None
            PROXY["TIMES"] = 0
            c.close()

        time.sleep(3)
        # break
    return cnt1

def process(content, wechatcrawler, wechatprocess):
    # j = json.loads(content)
    # infos = j["value"]
    # logger.info("Got %s news", len(infos))
    cnt = 0
    d = pq(html.fromstring(content.decode("utf-8")))
    title = d('head> title').text().strip()
    logger.info("title: %s", title)

    download_crawler = download.DownloadCrawler(use_proxy=False)

    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    for li in d('div.news-box> ul.news-list>li'):
        try:

            title = d(li)('h3> a').text()
            title = "".join(title.split(" "))
            wexinlink =  d(li)('h3> a').attr("href").strip()
            post_time = d('div.s-p').attr("t")
            logger.info(post_time)
            try:

                post_time = time.localtime(int(post_time))
                news_time = datetime.datetime(post_time.tm_year, post_time.tm_mon, post_time.tm_mday, post_time.tm_hour,
                                         post_time.tm_min, post_time.tm_sec)
                if news_time is None:
                    news_time = datetime.datetime.now()
            except:
                news_time = datetime.datetime.now()
            logger.info("link: %s", wexinlink)
            logger.info("article : %s,%s", title, news_time)

            item = collection_news.find_one({"link": wexinlink})
            item2 = collection_news.find_one({"title": title})
            # # item2 = collection_news.find_one({"title": title})
            # logger.info(item)
            # logger.info(item2)
            if item is None and item2 is None:
                logger.info("here crawler")
                if wexinlink.find("https") == -1:
                    wexinlink = wexinlink.replace("http","https")
                dnews = wechatprocess.crawler_news(wechatcrawler, wexinlink, download_crawler, wechatId="微信公众号")

                # dnews["wechatId"] = wechatId
                # dnews["wechatName"] = wechatName
                dnews["title"] = title
                dnews["date"] = news_time - datetime.timedelta(hours=8)
                dnews["processStatus"] = 0
                dnews["imgChecked"] = True
                dnews["category"] = None

                if dnews["result"] == 'SUCCESS' and len(dnews["contents"])>=1:
                    dnews.pop('result')
                    try:
                        id = collection_news.insert(dnews)
                        logger.info("**************: %s", id)
                        cnt += 1
                    except Exception, e:
                        logger.info(e)
                        pass
        except:
            pass

    mongo.close()
    return cnt


if __name__ == "__main__":
    while True:
        dt = datetime.datetime.now()
        logger.info("now hour is %s", dt.hour)
        if dt.weekday() in [0,1,2,3,4] and dt.hour in [15 ]:
            get(dt.hour)
            time.sleep(60*60)
        elif dt.weekday() in [5,6] and dt.hour in [15]:
            get(dt.hour)
            time.sleep(60*60)
        time.sleep(60)
