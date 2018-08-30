# -*- coding: utf-8 -*-
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_feixiaohao", stream=True)
logger = loghelper.get_logger("crawler_feixiaohao")

NEWSSOURCE = "feixiaohao"

URLS = []
CURRENT_PAGE = 1
linkPattern = "feixiaohao.com/currencies"
Nocontents = [
]
columns = [
    # {"column": "jmd", "max": 2},
    {"column": "None", "max": 30},
]
SOURCE = 13511
url_maps = ["currencies", "coindetails"]


class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=10):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

        # 实现
    def is_crawl_success(self, url, content):
        # if content.find("</html>") == -1:
        #    return False

        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("非小号") >= 0:
            return True

        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        # if content.find("</html>") == -1:
        #    return False

        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        if title.find("非小号") >= 0:
            return True
        if title.find("页面没有找到") >= 0:
            return True
        return False


def process_news(column, newsurl, contents, title, topic, download_crawler):

    logger.info('here')
    d_main = pq(html.fromstring(contents["currencies"].decode("utf-8","ignore")))
    d_detail = pq(html.fromstring(contents["coindetails"].decode("utf-8","ignore")))

    lis_main = d_main('div.secondPark> ul> li')
    lis_cq = d_main('div.firstPart> div.cell')
    coinName = title
    alias = []
    alias.append(coinName)
    coinEnglishName = None
    coinChineseName = None
    publishDateStr = None
    description = None
    whitebookLink = None
    cq = None
    websites = []
    blockchainWebsites = []
    logo_url = d_main('div.cell> h1> img').attr("src")
    if logo_url is not None and logo_url.strip()!= "" and logo_url.find("http") < 0:
        logo_url = "https:" + logo_url
    for li in lis_main:
        d_d = pq(li)
        tit = d_d('span.tit').text()
        value = d_d('span.value').text()
        if tit is not None and tit.strip() != "":
            if tit.find("英文名") >= 0 and value is not None and value.strip() not in ["","--","－"]:
                coinEnglishName = value
                for name in coinEnglishName.split("/"):
                    if name not in alias:
                        alias.append(name)
            if tit.find("中文名") >= 0 and value is not None and value.strip() not in ["","--","－"]:
                coinChineseName = value
                if coinEnglishName not in alias: alias.append(coinChineseName)
            if tit.find('发行时间') >= 0 and value is not None and value.strip() not in ["","--","－"]:
                publishDateStr = value
            if tit.find('白皮书') >= 0 and value is not None and value.strip() not in ["","--","－"]:
                whitebookLink = value

            if tit.find("网站") >= 0:
                for a in d_d('a'):
                    d_d_w = pq(a)
                    website = d_d_w('a').attr("href")
                    if website is not None and website not in websites and website.find("http") >= 0:
                        websites.append(website)

            if tit.find("区块站") >= 0:
                for a in d_d('a'):
                    d_d_w = pq(a)
                    website = d_d_w('a').attr("href")
                    if website is not None and website not in blockchainWebsites and website.find("http") >= 0:
                        blockchainWebsites.append(website)

    description = d_detail('div.artBox').text()
    if description.strip() == "": description = None

    for dc in lis_cq:
        dc_d = pq(dc)
        tit = dc_d('div.tit').eq(1).text()
        value = dc_d('div.value').eq(1).text()
        if tit is not None and tit.strip() != "":
            if tit.find("总发行量") >= 0 and value is not None and value.strip() not in ["","--","－"]:
                cq = value.split(" ")[0].replace(",","")
                try:
                    cq = long(cq)
                except:
                    cq = None


    item = {
        "bz_code": coinName.split("-")[0],
        "coinName" : coinName,
        "coinEnglishName": coinEnglishName.split("/")[0],
        "coinChineseName": coinChineseName,
        "alias": alias,
        "publishDateStr": publishDateStr,
        "description": description,
        "whitebookLink": whitebookLink,
        "websites": websites,
        "blockchainWebsites": blockchainWebsites,
        "source": SOURCE,
        "url": newsurl,
        "processStatus":0,
        "logo_url": logo_url,
        "cq":cq
    }

    for i in item:
        logger.info("%s - %s", i, item[i])
    parser_mongo_util.save_mongo_blockchain(SOURCE, coinName, item)
    logger.info("******************saved")




def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["title"], None, download_crawler)

def crawler_news(column, crawler, newsurl, title, topic, download_crawler):
    contents = {}
    for urlm in url_maps:
        retry = 0
        while True:
            if urlm == "currencies":
                result = crawler.crawl(newsurl, agent=True)
            else:
                if newsurl.find("particl") >= 0 or \
                        newsurl.find("patientory") >= 0 or \
                        newsurl.find("international-diamond") >= 0 or \
                        retry > 50:
                    result = {
                        "get": "success",
                        "content": '<html lang="zh-cn"></html>'
                    }
                else:
                    result = crawler.crawl(newsurl.replace("currencies","coindetails"), agent=True)

            if result['get'] == 'success':
                #logger.info(result["redirect_url"])
                contents[urlm] = result["content"]
                break

            retry += 1

    try:
        process_news(column, newsurl, contents, title, topic, download_crawler)
    except Exception, ex:
        logger.exception(ex)


def process(content, flag):
    if content.find("feixiaohao") >= 0:
        d = pq(html.fromstring(content.decode("utf-8","ignore")))
        for a in d('div.new-main-box> table> tbody> tr'):
            # try:
                link = d(a)('td> a').eq(0).attr("href")
                title = d(a)('td> a').eq(0).text()
                link = "https://www.feixiaohao.com" + link
                if re.search(linkPattern, link) and title is not None and title.strip() != "":
                    # logger.info("Link: %s is right news link %s", link, title)
                    # title = d(a)('h3> a').text()
                    sort = None
                    logger.info("Link: %s is right news link %s|%s", link, title, sort)
                    mongo = db.connect_mongo()
                    collection_bc = mongo.raw.blockchain
                    item = collection_bc.find_one({"link": link})
                    item2 = collection_bc.find_one({"source": SOURCE, "coinName": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": link,
                            "title": title.strip(),
                        }
                        URLS.append(linkmap)

                else:
                    # logger.info(link)
                    pass
            # except Exception, e:
            #     logger.info(e)
            #     logger.info("cannot get link")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler, concurrent_num):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE

        if flag == "all":
            if key > column["max"]:
                return
        else:
            if key > column["max"]:
                return

        CURRENT_PAGE += 1
        # pdata = "action=loadpost&offset=%s" % (key-1)
        url = "https://www.feixiaohao.com/list_%s.html" % key
        while True:
            result = listcrawler.crawl(url, agent=True)
            # result = listcrawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh currencies", url, cnt)
                        logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler=None) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, newscrawler, download_crawler=None)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break
        # exit()
        # elif result['get'] == 'redirect' and r


def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            gevent.sleep(60*60)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            link = param
            download_crawler = None
            crawler_news({}, NewsCrawler(), link, 'BTC-比特币', [], download_crawler)
    else:
        start_run(1, "all")