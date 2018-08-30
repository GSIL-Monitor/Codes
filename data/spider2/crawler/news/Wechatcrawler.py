# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, random
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

#logger
loghelper.init_logger("crawler_wechatnews", stream=True)
logger = loghelper.get_logger("crawler_wechatnews")


class NewsDownloader:
    def __init__(self, TYPE=60001, SOURCE=13840, RETRY=20, CATEGORY=None, FORCE=False):
        self.TYPE = TYPE
        self.SOURCE = SOURCE
        self.RETRY = RETRY
        self.CATEGORY = CATEGORY
        self.FORCE = FORCE

    def has_news_content(self, content):
        # d = pq(html.fromstring(content.decode("utf-8",'ignore')))
        # title = d('head> title').text().strip()
        #
        # if len(title) > 0 and title.find("404") == -1:
        #     return True
        # else:
        #     return False
        if content.find("profile_meta_value") >= 0:
            return True
        else:
            return False

    def extractWechatContents(self,article):
        d=pq(html.fromstring(article))
        wechatContents=[]
        pretext = None
        for p in d('p,img'):
            wechatContent={}
            if d(p).text():
                wechatContent['type']='text'
                wechatContent['data']=d(p).text()
                if pretext is not None and pretext == d(p).text():
                    continue
                else:
                    pretext = d(p).text()
            elif d(p)('img'):
                if d(p).attr('data-src'):
                    wechatContent['type'] = 'image'
                    wechatContent['data'] = d(p).attr('data-src')
            if len(wechatContent)>0:wechatContents.append(wechatContent)
        return wechatContents

    def process_news(self, newsurl, content, download_crawler):
        dnews = {}
        if self.has_news_content(content):
            try:
                d = pq(html.fromstring(content.decode("utf-8")))
            except:
                d = pq(html.fromstring(content))
            try:
                key = re.findall('sn=(.*)?&',newsurl)[0]
            except:
                key = newsurl

            try:
                key_int = int(key)
            except:
                key_int = None

            news_time = extractArticlePublishedDate.extractArticlePublishedDate(newsurl, content)

            if news_time is None:
                news_time = datetime.datetime.now()

            # title = extract.extractTitle(content)
            # title = d('.rich_media_title').eq(0).text()

            r = "var msg_title = \"(.*?)\".*var msg_desc"
            result = util.re_get_result(r, content)
            if result:
                # logger.info("Found brief")
                title, = result
                logger.info(title)
            else:
                title = None
            logger.info("title: %s",title)

            article = d('#page-content .rich_media_content').html()
            # contents = extract.extractContents(newsurl, article)
            contents=self.extractWechatContents(article)

            r = "var msg_desc = \"(.*?)\".*var msg_cdn_url"
            result = util.re_get_result(r, content)
            if result:
                # logger.info("Found brief")
                brief, = result
                logger.info(brief)
            else:
                brief  = None
            # logger.info(b)

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
            try:
                wechatId = d('span.profile_meta_value').eq(0).text().strip()
                wechatName = d('strong.profile_nickname').text().strip()
            except:
                wechatId = None
                wechatName = None
            logger.info("wechatId: %s, wechatName: %s", wechatId, wechatName)
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
                "categoryNames": [],
                "wechatId": wechatId,
                "wechatName": wechatName
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
                        (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, self.SOURCE, key, "news")
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
                # logger.info(c["data"])



                logger.info(c["data"])
                dcontents.append(dc)
                rank += 1
            dnews["contents"] = dcontents
            if brief is None:
                brief = util.get_brief_from_news(dcontents)
            post = util.get_posterId_from_news(dcontents)
            if download_crawler is None:
                dnews["post"] = post
            else:
                dnews["postId"] = post
            dnews["brief"] = brief.decode("utf-8")[:100]

            # if news_time > datetime.datetime.now() or news_time < datetime.datetime.now() - datetime.timedelta(days=30):
            #     logger.info("Time: %s is not correct with current time", news_time)
            #     dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
            # collection_news.insert(dnews)
            # mongo.close()

            # print dnews

            logger.info("*************DONE*************")
        return dnews


    def crawler_news(self, crawler, newsurl, download_crawler=None, wechatId=None):
        retry = 0
        while True:
            result = crawler.crawl(newsurl, agent=True)

            if result['get'] == 'success' and result.get("code") == 200:
                if result["content"].find("该内容已被发布者删除") >= 0:
                    logger.info("该内容已被发布者删除")
                    return {"result": "FAILED"}
                elif result["content"].find("此内容因违规无法查看") >= 0:
                    logger.info("此内容因违规无法查看")
                    return {"result": "FAILED"}
                elif result["content"].find("帐号已迁移") >= 0:
                    logger.info("帐号已迁移")
                    return {"result": "FAILED"}
                elif result["content"].find("class=\"account_desc_inner\"") >= 0:
                    logger.info("分享文章")
                    return {"result": "FAILED"}
                elif wechatId is not None and \
                    result["content"] is not None and (result["content"].find(wechatId) != -1 or wechatId == "微信公众号"):
                    #logger.info(result["redirect_url"])
                    try:
                        dnews = self.process_news(newsurl, result['content'], download_crawler)
                        dnews["result"] = "SUCCESS"
                        return dnews
                    except Exception,ex:
                        logger.exception(ex)
                        return {"result": "FAILED"}

                # elif result["content"].find("该内容已被发布者删除") >= 0:
                #     logger.info("该内容已被发布者删除")
                #     return {"result": "FAILED"}
                # elif result["content"].find("此内容因违规无法查看") >= 0:
                #     logger.info("此内容因违规无法查看")
                #     return {"result": "FAILED"}
                else:
                    # logger.info(result["content"])
                    pass
            logger.info("******************Retry: %s", retry)
            if retry > self.RETRY:
                return {"result": "FAILED"}
            retry += 1


class WechatCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)
        self.roundn = random.randint(0,100)

    # 实现
    def is_crawl_success(self, url, content):
        # logger.info("round num:%s",self.roundn)
        d = pq(html.fromstring(content.decode("utf-8",'ignore')))
        title = d('head> title').text().strip()
        logger.info("title: %s url: %s", title, url)

        share = d('div.account_desc_inner').text()
        if share is not None and share.find("分享")>= 0:
            logger.info("分享文章")
            return True
        if content.find("该内容已被发布者删除") >= 0:
            logger.info("该内容已被发布者删除")
            return True
        if content.find("此内容因违规无法查看") >= 0:
            logger.info("此内容因违规无法查看")
            return True
        if title.find("帐号已迁移") >= 0:
            logger.info("帐号已迁移")
            return True
        if content.find("WeChat ID") == -1 and content.find("微信号") == -1:
            return False
        # return False
        return True



if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        link = param
        download_crawler = download.DownloadCrawler(use_proxy=False)
        crawler = NewsDownloader()
        result = crawler.crawler_news(WechatCrawler(), link, wechatId="微信公众号")
        logger.info(result)
    else:
        logger.info("No link provided")

    # crawler = NewsDownloader()
    # link='http://mp.weixin.qq.com/s?__biz=MjM5NTczMDEwMQ==&mid=2651053087&idx=1&sn=272509575865a712a5d23cdfffa91ccb&chksm=bd037bc58a74f2d3c5815acdb0a9c4b2ac3dcca860a0c25b1b10b0ed6d82cb5923089c868f4a#rd'
    # link='http://mp.weixin.qq.com/s?__biz=MjM5Mzc3NzU2MA==&mid=2656168620&idx=1&sn=4c20fc81987c8f43eeda68bfe3aaee7c&chksm=bd34985b8a43114d42e2ca29431e587dea179cddcaae3f1ff2746246dc3fedc1b3714a2553c4#rd'
    #
    # result = crawler.crawler_news(WechatCrawler(), link)
