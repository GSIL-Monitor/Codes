# -*- coding: utf-8 -*-
import os, sys, datetime
from lxml import html
from pyquery import PyQuery as pq
import gevent
from gevent.event import Event
from gevent import monkey; monkey.patch_all()
import json

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
loghelper.init_logger("crawler_Kr36_news", stream=True)
logger = loghelper.get_logger("crawler_Kr36_news")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

newsid =[]
b_id =""

TYPE = 60001

def find_companyId(sourceId):
    if sourceId== "0" or sourceId==0:
        return None
    conn = db.connect_torndb()
    sc = conn.get("select * from source_company where source=%s and sourceId=%s", 13020, sourceId)
    if sc is not None:
        if sc["companyId"] is not None:
            return sc["companyId"]
    return None



class kr36Crawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                logger.info(j)
            except:
                return False

            if j.has_key("data"):
                return True

        return False

class kr36NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self, url, content):
        if content.find("</html>") == -1:
            return False
        d = pq(html.fromstring(content.decode("utf-8")))
        title = d('head> title').text().strip()
        logger.info("title: " + title + " " + url)
        if title.find("36氪_为创业者提供最好的产品和服务") != -1:
            return False
        if title.find("36氪") >= 0:
            return True
        # logger.info(content)
        return False


def has_content(content):
    if content is not None:
        try:
            j = json.loads(content)
        except:
            logger.info("Not json content")
            logger.info(content)
            return False
        if j["code"] == 0:
            return True
        else:
            logger.info("code=%d, %s" % (j["code"], j["msg"]))
    else:
        logger.info("Fail to get content")
    return False

def has_news_content(content):
    if content.find("服务器出错") > 0:
        return False
    return True


def process_news(id, url, content):
    if has_news_content(content):
        #r = "<script>var props=\{\"detailArticle\|post\"\:(.*?)\}(\;.*?|,)locationnal"
        if content.find("abTest") == -1:
            r = "<script>var props=\{\"detailArticle\|post\"\:(.*?),\"hotPostsOf30|hotPost\""
        else:
            r = "<script>var props=\{\"detailArticle\|post\"\:(.*?),\"abTest"

        result = util.re_get_result(r, content)
        (b,) = result
        #logger.info(b)
        #exit()
        base = json.loads(b, strict=False)
        tags = []
        #logger.info(base["content"])
        if base["published_at"] == "0000-00-00 00:00:00":
            base["published_at"] = base["created_at"]
        news_time = datetime.datetime.strptime(base["published_at"],"%Y-%m-%d %H:%M:%S")
        article_img = base["cover"]
        contents = base["content"]
        title = base["title"]
        brief = base["summary"]
        key = str(id)
        relatedCompanyId = base["related_company_id"]
        companyId = find_companyId(relatedCompanyId)
        column = base["column"]["name"]
        categoryNames = []

        if column =="深度" or column == "研究" or column == "深度报道" or column == "行业研究":
            type = 60003
            category = None
        else:
            if column == "明星公司":
                category = 60105
            elif column == "B轮后":
                category = 60101
            elif column == "早期项目":
                categoryNames.append("早期项目")
                if title.find("融资") >= 0:
                    categoryNames.append("融资")
                    category = 60101
                else:
                    category = 60102
            else:
                category = None
            type = TYPE
        tags.append(column)

        try:
            keywords = pq(content.decode("utf-8"))("meta[name='keywords']").attr("content").split(",")
            for keyword in keywords:
                if keyword is not None and keyword.strip() not in ["创业资讯","科技新闻","", column.strip()] and keyword not in tags:
                    tags.append(keyword.strip())
        except:
            pass
        logger.info("%s, %s, %s, %s, %s, %s -> %s", key, relatedCompanyId, companyId, title, news_time, ":".join(tags), category)


        if collection_news.find_one({"source": 13020,"key_int": int(key),"type":{"$ne":60002}}) is not None:
            return
            # collection_news.delete_one({"source": 13020, "key_int": int(key), "type":{"$ne":60002}})

        if collection_news.find_one({"title": title, "source": {"$ne": 13020}}) is not None:
            return
            # collection_news.delete_many({"title": title, "source": {"$ne": 13020}})
        flag, domain = url_helper.get_domain(url)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": url,
            "createTime": datetime.datetime.now(),
            "source": 13020,
            "key": key,
            "key_int": int(key),
            "type": type,
            "original_tags":tags,
            "processStatus":0,
            # "companyId":companyId,
            "companyIds":[companyId] if companyId is not None else [],
            "category": category,
            "domain": domain,
            "categoryNames": categoryNames
        }

        if title.find("【行研】")>=0:
            logger.info("it is research for 60006")
            download_crawler=download.DownloadCrawler(use_proxy=False)
            dnews["type"]=60006
            dnews["category"]=60107
            dnews["author"] = "36氪研究院"
            dnews["cleanTitle"] = title.replace("【行研】","")
            dnews["processStatus"] = 1
        else:
            download_crawler = download.DownloadCrawler(use_proxy=False)

        dcontents = []
        if article_img is not None:
            postraw = article_img
            # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
            (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, 13020, key, "news")
            if posturl is not None:
                post = str(posturl)
        else:
            post = None
        #     if download_crawler is None:
        #         dc = {
        #             "rank": 1,
        #             "content": "",
        #             "image": "",
        #             "image_src": article_img,
        #         }
        #
        #     else:
        #         # imgurl = parser_mysql_util.get_logo_id(article_img, download_crawler, 13020, key, "news")
        #         # dc = {
        #         #     "rank": 1,
        #         #     "content": "",
        #         #     "image": str(imgurl),
        #         #     "image_src": "",
        #         # }
        #         (imgurl, width, height) = parser_mysql_util.get_logo_id_new(article_img, download_crawler, 13020,
        #                                                                     key, "news")
        #         if imgurl is not None:
        #             dc = {
        #                 "rank": 1,
        #                 "content": "",
        #                 "image": str(imgurl),
        #                 "image_src": "",
        #                 "height": int(height),
        #                 "width": int(width)
        #             }
        #     dcontents.append(dc)
        #     # logger.info(article_img)

        # process news
        rank = len(dcontents) + 1
        # logger.info(pq(contents))
        # logger.info(contents)
        ps =  pq(contents)('p, img')
        pic = None
        for p in ps:
            dd = None
            d = pq(p)
            #logger.info(d)
            if d.has_class('detect-string'):
                #logger.info("wrong content")
                continue
            if d.text() is not None and d.text().strip() != "":
                #logger.info(d.text())
                dd = {
                    "rank": rank,
                    "content": d.text(),
                    "image": "",
                    "image_src": "",
                }
            elif d('img').attr("src") is not None and d('img').attr("src") !="":
                picn = d('img').attr("src").replace("!heading", "")
                if pic is not None:
                    if pic == picn:
                        pic = picn
                        continue
                    else:
                        pic = picn
                else:
                    pic = picn
                #logger.info(d('img').attr("src"))
                # dd = {
                #     "rank": rank,
                #     "content": "",
                #     "image": "",
                #     "image_src": d('img').attr("src").replace("!heading", ""),
                # }
                if download_crawler is None:
                    dd = {
                        "rank": rank,
                        "content": "",
                        "image": "",
                        "image_src": d('img').attr("src").replace("!heading", ""),
                    }
                else:
                    # imgurl = parser_mysql_util.get_logo_id(d('img').attr("src").replace("!heading", ""), download_crawler, 13020, key, "news")
                    # if imgurl is not None:
                    #     dd = {
                    #         "rank": rank,
                    #         "content": "",
                    #         "image": str(imgurl),
                    #         "image_src": "",
                    #     }
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(d('img').attr("src").replace("!heading", ""), download_crawler,
                                                                                 13020, key, "news")
                    if imgurl is not None:
                         dd = {
                            "rank": rank,
                            "content": "",
                            "image": str(imgurl),
                            "image_src": "",
                            "height": int(height),
                            "width": int(width)
                        }
                    else:
                        continue
            if dd is not None:
                dcontents.append(dd)
                rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        # post = util.get_poster_from_news(dcontents)
        if post is None or post.strip() == "":
            if download_crawler is None:
                post = util.get_poster_from_news(dcontents)
                dnews["post"] = post
            else:
                post = util.get_posterId_from_news(dcontents)
                dnews["postId"] = post
        else:
            dnews["postId"] = post
        # dnews["post"] = post
        dnews["brief"] = brief
        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)

        nid = parser_mongo_util.save_mongo_news(dnews)
        logger.info("Done: %s", nid)
        # collection_news.insert(dnews)
        #exit()
        #g.latestIncr()

def run_news(crawler, outlink = None):

    while True:
        if outlink is None:
            if len(newsid) ==0:
                return
            id = newsid.pop(0)
            url = "http://36kr.com/p/%s.html" % id
        else:
            url = outlink
            id = url.split("/")[-1].replace(".html", "")
        retries = 0
        maxretry = 0
        while True:
            result = crawler.crawl(url, agent=True)
            if result['get'] == 'success':
                #logger.info(result["redirect_url"])
                try:
                    process_news(id, url, result['content'])
                except Exception,ex:
                    logger.exception(ex)
                break
            else:
                if result["content"] is None or result["content"].strip() == "":
                    continue
                d = pq(html.fromstring(result["content"]))
                title = d('head> title').text().strip()
                if title.find("36氪_为创业者提供最好的产品和服务") != -1:
                    if retries >= 3:
                        break
                    retries += 1
            if maxretry > 20: break
            maxretry += 1

        if outlink is not None:
            break






def process_page(content, flag):
    bid = None
    j = json.loads(content)
    infos = j["data"]["items"]
    if infos is not None:
        for info in infos:
            key = info["id"]
            title = info["title"]
            date = info["published_at"]
            logger.info("%s, %s, %s", key, date, title)

            if collection_news.find_one({"source": 13020, "key_int": int(key), "type":{"$ne":60002}}) is None or flag == "all":
                craw = True
                newses = list(collection_news.find({"title": title, "source": {"$ne": 13020}}))
                for news in newses:
                    if news.has_key("type") and news["type"] > 0:
                        craw = False
                        break
                if craw:
                    newsid.append(key)

            bid = key

    return newsid, bid

def start_run(flag):
    global b_id
    while True:
        logger.info("36kr news %s start...", flag)

        crawler = kr36Crawler()
        for column in [71,0]:
            while True:
                if column == 0:
                    page_url = "http://36kr.com/api/info-flow/main_site/posts?per_page=100&b_id=%s" % b_id
                else:
                    page_url = "http://36kr.com/api/post?column_id=71&b_id=%s&per_page=30" % b_id
                result = crawler.crawl(page_url, agent=True)
                if result['get'] == 'success':
                    if has_content(result["content"]):
                        newsid, b_id = process_page(result["content"], flag)
                        if len(newsid) > 0 or flag == "all":
                            logger.info("crawler news details")
                            #logger.info(news)
                            threads = [gevent.spawn(run_news, kr36NewsCrawler()) for i in xrange(1)]
                            gevent.joinall(threads)
                            #exit()
                            continue
                        else:
                            b_id = ""
                    else:
                        b_id = ""
                        logger.info("no content")
                        logger.info(result["content"])
                    break


        logger.info("36kr news %s end.", flag)

        if flag == "incr":
            gevent.sleep(60*5)        #10 minutes
        else:
            gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    if len(sys.argv) > 1:
        param = sys.argv[1]
        if param == "all":
            start_run("all")
        else:
            start_run("incr")
    else:
        start_run("incr")