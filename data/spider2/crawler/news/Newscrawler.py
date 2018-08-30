# -*- coding: utf-8 -*-
import os, sys, datetime, re, json
from lxml import html
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

import pencil_news_v2
import lieyun_news
import iyiou_news
import huxiu_news
import leiphone_news
import Wechatcrawler
import kr36_news


#logger
loghelper.init_logger("crawler_news", stream=True)
logger = loghelper.get_logger("crawler_news")


class NewsDownloader:
    def __init__(self, TYPE=60005, SOURCE=13900, RETRY=20, CATEGORY=None, FORCE=False):
        self.TYPE = TYPE
        self.SOURCE = SOURCE
        self.RETRY = RETRY
        self.CATEGORY = CATEGORY
        self.FORCE = FORCE

    def has_news_content(self, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        if len(title) > 0 and title.find("404") == -1:
            return True
        else:
            return False


    def process_news(self, newsurl, content, download_crawler):
        if self.has_news_content(content):
            try:
                d = pq(html.fromstring(content.decode("utf-8")))
            except:
                d = pq(html.fromstring(content))

            key = newsurl.split("/")[-1].replace(".shtml","").replace(".html","")
            try:
                key_int = int(key)
            except:
                key_int = None

            news_time = extractArticlePublishedDate.extractArticlePublishedDate(newsurl, content)
            if news_time is None:
                news_time = datetime.datetime.now()

            title = extract.extractTitle(content)

            contents = extract.extractContents(newsurl, content)

            tags = []
            try:
                articletags = d("meta[name='keywords']").attr("content")
                if articletags is not None:
                    for tag in articletags.split():
                        if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                            tags.append(tag)
            except:
                pass

            logger.info("News: %s, %s, %s", key, title, news_time)

            # mongo = db.connect_mongo()
            # collection_news = mongo.article.news
            # if collection_news.find_one({"link": newsurl}) is not None:
            #     mongo.close()
            #     return

            flag, domain = url_helper.get_domain(newsurl)
            dnews = {
                "date": news_time - datetime.timedelta(hours=8),
                "title": title,
                "link": newsurl,
                "createTime": datetime.datetime.now(),
                "source": self.SOURCE,
                "key": key,
                "key_int": key_int,
                "type": self.TYPE,
                "original_tags": tags,
                "processStatus": 0,
                # "companyId": None,
                "companyIds": [],
                "category": self.CATEGORY,
                "domain": domain,
                "categoryNames": []
            }
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
                    if download_crawler is None:
                        dc = {
                            "rank": rank,
                            "content": "",
                            "image": "",
                            "image_src": c["data"],
                        }
                    else:
                        # imgurl = parser_mysql_util.get_logo_id(c["data"], download_crawler, self.SOURCE, key, "news")
                        (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler,
                                                                                    self.SOURCE,
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

                logger.info(c["data"])
                dcontents.append(dc)
                rank += 1
            dnews["contents"] = dcontents

            brief = util.get_brief_from_news(dcontents)
            post = util.get_poster_from_news(dcontents)
            if download_crawler is None:
                dnews["post"] = post
            else:
                dnews["postId"] = post
            dnews["brief"] = brief

            # if news_time > datetime.datetime.now() or news_time < datetime.datetime.now() - datetime.timedelta(days=30):
            #     logger.info("Time: %s is not correct with current time", news_time)
            #     dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

            if news_time > datetime.datetime.now():
                logger.info("Time: %s is not correct with current time", news_time)
                dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
            if len(dnews["contents"])> 2:
                # mongo = db.connect_mongo()
                # collection_news = mongo.article.news
                # collection_news.insert(dnews)
                # mongo.close()
                nid = parser_mongo_util.save_mongo_news(dnews)
                logger.info("Done: %s", nid)
            logger.info("*************DONE*************")


    def crawler_news(self, crawler, newsurl, download_crawler=None):
        retry = 0
        while True:
            # headers = {"Cookie": "_ga=fff"}
            result = crawler.crawl(newsurl, agent=True)
            if result['get'] == 'success' and result.get("code") == 200:
                #logger.info(result["redirect_url"])
                try:
                    self.process_news(newsurl, result['content'], download_crawler)
                    return {"result": "SUCCESS"}
                except Exception,ex:
                    logger.exception(ex)
                    return {"result": "FAILED"}

            if retry > self.RETRY:
                return {"result": "FAILED"}
            retry+=1


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    # 实现
    def is_crawl_success(self, url, content):
        d = pq(html.fromstring(content))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)
        # if title.find("页面未找到404") >= 0:
        #     return False
        # if title.find("您所请求的网址（URL）无法获取") >= 0:
        #     return False
        # if title.find("403 Forbidden") >= 0:
        #     return False
        # if title.find("ERROR: The requested URL could not be retrieved") >= 0:
        #     return False
        # if content.find("421 Server too busy") >= 0:
        #     return False
        # if content.find("铅笔道") >= 0:
        #     return True
        # return False
        return True


def crawlerNews(link, pdate = None):
    download_crawler = download.DownloadCrawler(use_proxy=False)
    download_crawler_n = None

    if link.find("pencilnews.cn") >= 0:
        pencil_news_v2.crawler_news({}, pencil_news_v2.NewsCrawler(), link, None, download_crawler)
    elif link.find("lieyunwang.com") >= 0:
        lieyun_news.run_news(lieyun_news.LieyunNewsCrawler(), link)
    elif link.find("iyiou.com") >= 0:
        iyiou_news.crawler_news({}, iyiou_news.NewsCrawler(), link)
    elif link.find("huxiu.com") >= 0:
        huxiu_news.crawler_news({}, huxiu_news.NewsCrawler(), link, None, download_crawler)
    elif link.find("leiphone.com") >= 0:
        leiphone_news.process(leiphone_news.Contentcrawler(), link)
    elif link.find("36kr.com") >= 0 :
        kr36_news.run_news(kr36_news.kr36NewsCrawler(), link)
    elif link.find("mp.weixin.qq.com") >= 0:
        wechatcrawler = Wechatcrawler.WechatCrawler()
        wechatprocess = Wechatcrawler.NewsDownloader()
        dnews = wechatprocess.crawler_news(wechatcrawler, link, download_crawler, wechatId="微信公众号")
        # dnews["wechatId"] = "微信公众号"
        # dnews["wechatName"] = "微信公众号"
        # try:
        #     dnews["date"] = datetime.datetime.strptime(pdate,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=8)
        # except:
        #     dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        if dnews["result"] == 'SUCCESS' and dnews.has_key("contents") is True and len(dnews["contents"]) >= 1:
            dnews.pop('result')
            try:
                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                id = collection_news.insert(dnews)
                mongo.close()
                logger.info("Done %s", id)
                # collection_news.insert(dnews)
            except Exception, e:
                logger.info(e)
                pass
    else:

        # download_crawler = download.DownloadCrawler(use_proxy=False)
        crawler = NewsDownloader()
        result = crawler.crawler_news(NewsCrawler(), link, download_crawler)
        logger.info(result)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        link = param

        # #download crawler for pic
        # download_crawler = download.DownloadCrawler(use_proxy=False)
        # download_crawler_n = None
        #
        # if link.find("www.pencilnews.cn")>=0:
        #     pencil_news_v2.crawler_news({}, pencil_news_v2.NewsCrawler(), link, None, download_crawler)
        # elif link.find("www.lieyunwang.com") >= 0:
        #     lieyun_news.run_news(lieyun_news.LieyunNewsCrawler(), link)
        # elif link.find("www.iyiou.com") >= 0:
        #     iyiou_news.crawler_news({},iyiou_news.NewsCrawler(), link)
        # elif link.find("www.huxiu.com") >= 0:
        #     huxiu_news.crawler_news({}, huxiu_news.NewsCrawler(), link, None, download_crawler_n)
        # elif link.find("www.leiphone.com") >= 0:
        #     leiphone_news.process(leiphone_news.Contentcrawler(), link)
        # else:
        #
        #     # download_crawler = download.DownloadCrawler(use_proxy=False)
        #     crawler = NewsDownloader()
        #     result = crawler.crawler_news(NewsCrawler(), link)
        #     logger.info(result)

        crawlerNews(link)
    else:
        logger.info("No link provided")