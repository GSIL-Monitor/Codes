# -*- coding: utf-8 -*-
import os, sys, datetime, re
from lxml import html
from pyquery import PyQuery as pq
import activity_simhash
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import GlobalValues_news

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util


#logger
loghelper.init_logger("crawler_welian_activity", stream=True)
logger = loghelper.get_logger("crawler_welian_activity")
download_crawler = download.DownloadCrawler(use_proxy=False)

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

MAX_PAGE_ALL = 100
MAX_PAGE_INCR = 1
CURRENT_PAGE = 1

TYPE = 60002
SOURCE =13802

citymap = {
    131: "北京",
    289: "上海",
    257: "广州",
    340: "深圳",
    179: "杭州",
    -1:  "其他"
}

class WelianCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)

        if title.find("_微链") >= 0:
            return True
        return False


def has_content(content):

    #logger.info("title: " + title)
    if content.find("主办方") == -1:
        logger.info("False")
        return False
    return True


def process(content, citykey, crawler):
    cnt = 0
    if has_content(content):
        DT = datetime.date.today()
        TODAY = datetime.datetime(DT.year, DT.month, DT.day)
        #logger.info(content)
        d = pq(html.fromstring(content.decode("utf-8")))
        lis =  d('div.wrap> div> div> ul.ativities> li.item')
        for li in lis:
            c = pq(li)
            img = c('a> img').attr("src").strip().replace("|130w","")
            if img is not None:
                # logger.info("poster: %s", poster)
                # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
                (posturl, width, height) = parser_mysql_util.get_logo_id_new(img, download_crawler, SOURCE, key,
                                                                             "news")
                if posturl is not None:
                    poster = str(posturl)
                else:
                    poster = None
            title = c('h3.title> a').text()
            link = c('h3.title> a').attr("href")
            if link.find("http") ==-1:
                 continue
            key = link.split("/")[-1]
            key_int = int(key)
            location = c('div.intro> div.address').text()
            sponors = c('div.intro> div.sponors> span').text().replace(","," ").replace("，"," ").split()
            spans = c('div.intro> div.time> span')
            if len(spans) == 3:
                date = c('div.intro> div.time> span').eq(0).text()
                times = c('div.intro> div.time> span').eq(2).text().split("~")
                beginTime = date+" "+times[0]
                endTime = date+" "+times[1]
            elif len(spans) == 5:
                date = c('div.intro> div.time> span').eq(0).text()
                year = date.split("-")[0]
                times = c('div.intro> div.time> span').eq(2).text().split("~")
                beginTime = date+" "+times[0]
                endTime = year+"-"+times[1]+" "+c('div.intro> div.time> span').eq(4).text()
            else:
                continue
            try:
                beginDate = datetime.datetime.strptime(beginTime, "%Y-%m-%d %H:%M")
                endDate = datetime.datetime.strptime(endTime, "%Y-%m-%d %H:%M")
            except:
                beginDate = None

            if beginDate is None or beginDate < TODAY or key_int is None:
                # Not save active activity
                continue

            result = crawler.crawl(link)
            while True:
                if result['get'] == 'success':
                    break
                else:
                    result = crawler.crawl(link)
            if has_content(result['content']):
                contents = extract.extractContents(link, result['content'])
                flag, domain = url_helper.get_domain(link)
                dact = {
                    "beginDate": beginDate - datetime.timedelta(hours=8),
                    "endDate": endDate - datetime.timedelta(hours=8),
                    "date": beginDate - datetime.timedelta(hours=8),
                    "title": title,
                    "link": link,
                    "createTime": datetime.datetime.now(),
                    "source": SOURCE,
                    "key": key,
                    "key_int": key_int,
                    "type": TYPE,
                    "original_tags": [],
                    "processStatus": 0,
                    "companyIds": [],
                    "location": location,
                    "city": citymap[citykey],
                    "sponors": sponors,
                    "post": poster,
                    "domain": domain,
                    "categoryNames": []
                }
                dcontents = []
                rank = 1
                for c in contents:
                    if c["type"] == "text":
                        if c["data"].find("我要报名") >= 0:
                            logger.info("************************over")
                            break
                        dc = {
                            "rank": rank,
                            "content": c["data"],
                            "image": "",
                            "image_src": "",
                        }
                    else:
                        # dc = {
                        #     "rank": rank,
                        #     "content": "",
                        #     "image": "",
                        #     "image_src": c["data"],
                        # }
                        (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"],download_crawler, SOURCE,
                                                                                    key, "news")
                        if imgurl is not None:
                            dc = {
                                "rank": rank,
                                "content": "",
                                "image": str(imgurl),
                                "image_src": "",
                                "height": int(height),
                                "width": int(width)
                            }
                        else:
                            continue
                    dcontents.append(dc)
                    rank += 1
                dact["contents"] = dcontents
                value = activity_simhash.get_simhash_value(dcontents)
                dact["simhashValue"] = value

                record = collection_news.find_one({"source": SOURCE, "key_int": key_int})
                if record is not None:
                    city = record["city"]
                    if record["beginDate"] == dact["beginDate"] and record["endDate"] == dact["endDate"] and record["title"] == dact["title"] and record["city"] == citymap[citykey] and record["location"] == dact["location"]:
                        logger.info("%s activity already existed", title)
                        cnt += 1
                        continue
                    else:
                        collection_news.delete_one({"source": SOURCE, "key_int": key_int})
                        if city != citymap[citykey]:
                            logger.info("%s has two city : %s and %s with location %s, something is wrong", title, city, citymap[citykey], location)
                            cnt += 1
                            continue

                        collection_news.insert(dact)
                        logger.info("%s, %s, %s->%s, %s, %s, %s, %s", key, title, beginDate, endDate, ":".join(sponors),location, link, img)
                else:
                    if activity_simhash.check_same_act(dact) is True:
                        pass
                    else:
                        collection_news.insert(dact)
                        logger.info("%s, %s, %s->%s, %s, %s, %s, %s", key, title, beginDate, endDate, ":".join(sponors), location, link, img)
                cnt += 1
                logger.info("************Done***************")
    logger.info("*******%s activities has been checked or recorded", cnt)
    return cnt



def run(flag, citykey):
    global CURRENT_PAGE
    crawler = WelianCrawler()
    cnt = 1
    while True:
        key = CURRENT_PAGE
        #logger.info("key=%s", key)
        if flag == "all":
            if key > MAX_PAGE_ALL:
                return
        else:
            if cnt == 0:
                return

        CURRENT_PAGE += 1
        url = "http://active.welian.com/active/index?ct=%s&p=%s" % (citykey, key)
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                try:
                    cnt = process(result['content'], citykey, crawler)
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break


def start_run(flag):
    global CURRENT_PAGE
    while True:
        logger.info("Welian activity %s start...", flag)
        for citykey in citymap:

            CURRENT_PAGE = 1
            run(flag, citykey)

        logger.info("Welian activity %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*60)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days

if __name__ == "__main__":
    flag = "incr"

    start_run(flag)