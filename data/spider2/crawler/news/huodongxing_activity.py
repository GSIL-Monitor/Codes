# -*- coding: utf-8 -*-
import os, sys, datetime, time
from lxml import html
from pyquery import PyQuery as pq
import activity_simhash
import GlobalValues_news

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,db,extract,util,url_helper,simhash,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util

#logger
loghelper.init_logger("crawler_huodongxing_activity", stream=True)
logger = loghelper.get_logger("crawler_huodongxing_activity")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news
download_crawler = download.DownloadCrawler(use_proxy=False)

TYPE = 60002
SOURCE =13804

CITIES = [
    "北京",
    "上海",
    "广州",
    "深圳",
    "杭州",
    "成都",
    "南京",
    "苏州",
    "武汉",
    "天津",
    "重庆",
    "西安",
    "厦门",
    "宁波",
    "郑州",
    "青岛",
    "东莞",
    "佛山",
    "长沙",
    "石家庄"]

TAGS = [
    "投资",
    "创业",
    "科技",
]

class HuodongxingPageCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
           return False

        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        #logger.info("title: %s url: %s", title, url)

        if title.find("活动行") >= 0:
            return True
        return False


crawler = HuodongxingPageCrawler()

def process_activity(key, content):
    if has_content_detail(content):
        #logger.info(content)
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('h2.media-heading').text()
        #logger.info("title: %s", title)

        tags = []
        exclude_tags = ["活动详情","报名人数","时间","图片海报","活动地图","票价","票务说明","主办方","活动论坛"]
        keywords = d('meta[name="keywords"]').attr("content").split(",")
        for keyword in keywords:
            if keyword not in exclude_tags:
                tags.append(keyword)
        #logger.info(tags)


        record = collection_news.find_one({"source": SOURCE, "key_int": int(key)})
        if record is not None:
            return

        poster = None
        postraw = None
        result = util.re_get_result('\'pic\':\'(.*?)\'', content)
        if result:
            postraw, = result
        if postraw is not None:
        #logger.info("poster: %s", poster)
            # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
            (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key, "news")
            if posturl is not None:
                poster = str(posturl)
            else:
                poster = None

        strTime = d('div.jumbotron> div.media-body> div').eq(0).text()
        #logger.info(strTime)
        strTimes = strTime.split("～")
        #2016年8月16日 14:00
        beginDate = datetime.datetime.strptime(strTimes[0].strip(),'%Y年%m月%d日 %H:%M')
        #logger.info(beginDate)
        endDate = datetime.datetime.strptime(strTimes[1].strip(),'%Y年%m月%d日 %H:%M')
        #logger.info(endDate)
        location = d('div.address').text()
        #logger.info(location)

        prov = None
        result = util.re_get_result('var prov = "(.*?)";', content)
        if result:
            prov, = result

        city = None
        result = util.re_get_result('var city = "(.*?)";', content)
        if result:
            city, = result

        if prov == "北京" or prov == "天津" or prov == "上海" or prov == "重庆":
            city = prov

        #logger.info("city: %s", city)

        sponors = d('div.jumbotron> div.media-body> div> a').eq(1).text()
        #logger.info(sponors)

        desc = d('div#event_desc_page').html()
        #logger.info(desc)
        contents = extract.extractContents("http://www.huodongxing.com", desc)
        dcontents = []
        rank = 1
        for c in contents:
            if c["type"] == "text":
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
                if download_crawler is None:
                    dc = {
                        "rank": rank,
                        "content": "",
                        "image": "",
                        "image_src": c["data"],
                    }
                else:
                    # imgurl = parser_mysql_util.get_logo_id(c["data"], download_crawler, SOURCE, key, "news")
                    # if imgurl is not None:
                    #     dc = {
                    #         "rank": rank,
                    #         "content": "",
                    #         "image": str(imgurl),
                    #         "image_src": "",
                    #     }
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE,
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

        key_int = int(key)
        link = "http://www.huodongxing.com/event/%s" % key
        flag, domain = url_helper.get_domain(link)
        value = activity_simhash.get_simhash_value(dcontents)
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
            "original_tags": tags,
            "processStatus": 0,
            "companyIds": [],
            "location": location,
            "city": city,
            "sponors": [sponors],
            "post": poster,
            "contents": dcontents,
            "domain": domain,
            "simhashValue": value,
            "categoryNames": [],
            "imgChecked": True
        }

        record = collection_news.find_one({"source": SOURCE, "key_int": key_int})
        if record is not None:
            if record["beginDate"] == dact["beginDate"] and record["endDate"] == dact["endDate"] and record["title"] == dact["title"] and \
                            record["city"] == dact["city"] and record["location"] == dact["location"]:
                logger.info("%s activity already existed", title)
            else:
                collection_news.delete_one({"source": SOURCE, "key_int": key_int})
                collection_news.insert(dact)
                logger.info("Information changed for %s", title)
                logger.info("%s, %s, %s, %s, %s, %s, %s", key, title, beginDate, endDate, location, ";".join(tags), sponors)
        else:
            if activity_simhash.check_same_act(dact) is True:
                pass
            else:
                collection_news.insert(dact)
                logger.info("%s, %s, %s, %s, %s, %s, %s", key, title, beginDate, endDate, location, ";".join(tags), sponors)
        #exit()


def process(city, content):
    #logger.info(content)
    d = pq(html.fromstring(content.decode("utf-8")))
    lis =  d('div.search-tab-content-item> div')
    for li in lis:
        key = None
        c = pq(li)
        url = c('a').eq(0).attr("href")
        result = util.re_get_result('/event/(\d+)', url)
        if result:
            key, = result
        if key is None:
            continue

        url = "http://www.huodongxing.com/event/%s" % key
        logger.info(url)
        maxretry = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                break
            elif result['get'] == 'fail' and result["content"] is not None:
                logger.info(result["content"])
                if result["content"].find("系统载入中") > 0:
                    break
            if maxretry > 30:
                result["content"] = " "
                break
            maxretry += 1

        try:
            process_activity(key, result['content'])
        except Exception,ex:
            logger.exception(ex)


def has_content_page(content):
    if content.find("找不到活动") > 0:
        return False
    return True

def has_content_detail(content):
    if content.find("系统载入中") > 0:
        return False
    return True

def start_run():
    for tag in TAGS:
        for city in CITIES:
            page = 1
            while True:
                url = "http://www.huodongxing.com/eventlist?orderby=n&tag=%s&city=%s&page=%s" % (tag, city, page)

                while True:
                    result = crawler.crawl(url, agent=True)
                    if result['get'] == 'success':
                        break
                    # elif result['get'] == 'fail' and result["content"] is not None:
                    #     logger.info(result["content"])
                    #     if result["content"].find("系统载入中") > 0:
                    #         break


                if has_content_page(result["content"]):
                    try:
                        logger.info("here")
                        process(city, result['content'])
                    except Exception,ex:
                        logger.exception(ex)
                else:
                    break

                page += 1
                if page > 30:
                    break


if __name__ == "__main__":
    while True:
        logger.info("Huodongxing activity start...")
        start_run()
        logger.info("Huodongxing activity end.")

        time.sleep(12*60*60)