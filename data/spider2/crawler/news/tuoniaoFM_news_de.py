# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import GlobalValues_news

reload(sys)
sys.setdefaultencoding("utf-8")


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
import loghelper,extract,db,util,url_helper,download

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_tuoniaoFM", stream=True)
logger = loghelper.get_logger("crawler_tuoniaoFM")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news


class tuoniaoCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    #实现
    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)

        if title.find("您请求的页面不存在") >=0 or title.find("Object moved")>=0:
            return True
        if title.find("未找到页面") >= 0:
            return True
        if title.find("鸵鸟") >= 0:
            return True
        return False


def has_content(content):
    d = pq(html.fromstring(content))
    title = d('head> title').text().strip()
    #logger.info("title: " + title)
    if title.find("未找到页面") >= 0:
        return False
    if title.find("鸵鸟") >= 0:
        return True
    return False


def process(g, crawler, url, key, content):
    if has_content(content):
        download_crawler = download.DownloadCrawler(use_proxy=False)
        try:
            columns = pq(content)("meta[name='keywords']").attr("content").split(",")
        except:
            columns = []
        # brief = pq(content)("meta[name='description']").attr("content").strip()
        breif = None
        main = pq(content)('div.data-article')
        d = pq(main)
        title = pq(content)('div.da-title> h2').text()
        type = 60001
        categoryNames = []
        if "上海" in columns:
            columns = []
            category = None
        else:
            if "融资" in columns or "融资发布" in columns or title.find("融资") >= 0:
                category = 60101
                categoryNames.append("融资")
            elif "鸵鸟干货" in columns:
                type = 60003
                category = 60107
            elif "投资人专访" in columns:
                category = 60104
                categoryNames.append("投资人观点")
            elif "苹果" in columns or "大公司" in columns:
                category = 60105
                categoryNames.append("大公司")
            elif "工具软件" in columns or \
                "智能科技" in columns or \
                "软件" in columns or \
                "企业服务" in columns or \
                "本地生活" in columns:
                category = 60102
                categoryNames.append("产品")
            else:
                category = None
        news_time = pq(content)('div.article-author> span.article-time').eq(0).text()
        if news_time is not None and news_time.strip() != "":
            logger.info("here :%s",news_time)
            try:
                news_time = datetime.datetime.strptime(news_time.strip(), "%Y-%m-%d %H:%M")
            except:
                news_time = datetime.datetime.now()
        else:
            news_time = datetime.datetime.now()
        contents = extract.extractContents(url, content)

        dcontents = []
        # article_img = d('div.article-img-box> img').attr("src")
        # if article_img is not None:
        #     dc = {
        #         "rank": 1,
        #         "content": "",
        #         "image": "",
        #         "image_src": article_img,
        #     }
        #     dcontents.append(dc)
        logger.info("%s, %s, %s, %s, %s", key, title, news_time, category, ":".join(columns))
        # logger.info(article_img)
        # for t in contents:
        #     logger.info(t["data"])
        #
        #item = collection_news.find_one({"source": g.SOURCE, "key_int": int(key)})
        if collection_news.find_one({"source": g.SOURCE, "key_int": int(key)}) is not None:
            collection_news.delete_one({"source": g.SOURCE, "key_int": int(key)})

        craw = True
        newses = list(collection_news.find({"title": title, "source": {"$ne": g.SOURCE}}))
        for news in newses:
            if news.has_key("type") and news["type"] > 0:
                craw = False
                break
        if craw:
            if collection_news.find_one({"title": title, "source": {"$ne": g.SOURCE}}) is not None:
                collection_news.delete_many({"title": title, "source": {"$ne": g.SOURCE}})
            flag, domain = url_helper.get_domain(url)
            dnews = {
                "date": news_time - datetime.timedelta(hours=8),
                "title": title,
                "link": url,
                "createTime": datetime.datetime.now(),
                "source": g.SOURCE,
                "key": key,
                "key_int": int(key),
                "type": type,
                "original_tags":columns,
                "processStatus":0,
                # "companyId": None,
                "companyIds":[],
                "category": category,
                "domain": domain,
                "categoryNames": categoryNames
            }

            rank = len(dcontents)+1
            for c in contents:
                if c["data"].find("发表评论")>=0:
                    break
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
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, g.SOURCE, key, "news")
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
                logger.info(c["data"])
                dcontents.append(dc)
                rank += 1
            dnews["contents"] = dcontents

            brief = util.get_brief_from_news(dcontents)
            post = util.get_posterId_from_news(dcontents)
            dnews["postId"] = post
            dnews["brief"] = brief
            # mid = collection_news.insert(dnews)
            # logger.info("*********Done: %s", mid)
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)

        g.latestIncr()


def crawl(crawler, key ,g):
    url = "http://tuoniao.fm/p/%s.html" % key
    while True:
        result = crawler.crawl(url, agent=True)
        if result['get'] == 'success':
            #logger.info(result["content"])
            try:
                process(g, crawler, url, key, result['content'])
            except Exception,ex:
                logger.exception(ex)
            break

def run(g, crawler):
    while True:
        if g.finish(num=1000):
            return
        key = g.nextKey()
        crawl(crawler, key, g)


def start_run(concurrent_num, flag):
    while True:
        logger.info("TuoniaoFM news %s start...", flag)
        g = GlobalValues_news.GlobalValues(13801, 0, flag, back=0)

        threads = [gevent.spawn(run, g, tuoniaoCrawler()) for i in xrange(concurrent_num)]
        gevent.joinall(threads)

        logger.info("TuoniaoFM news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*15)        #30 minutes
        else:
            gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "incr":
            start_run(1, "incr")
        elif param == "all":
            start_run(1, "all")
        else:
            key = str(int(param))
            g = GlobalValues_news.GlobalValues(13801, 0, "incr", back=0)
            crawl(tuoniaoCrawler(), key, g)
    else:
        start_run(1, "incr")