# -*- coding: utf-8 -*-
import os, sys, datetime, re, json, time
from lxml import html
from pyquery import PyQuery as pq
import math, hashlib

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
import BaseCrawler

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util

#logger
loghelper.init_logger("crawler_mtoutiao_news", stream=True)
logger = loghelper.get_logger("crawler_mtoutiao_news")

NEWSSOURCE = "toutiao"
RETRY = 3
TYPE = 60001
SOURCE =13837
URLS = []
CURRENT_PAGE = 1
linkPattern = "toutiao"
Nocontents = [
]
columns = [
    {"column": "new", "max": 1, "code": "6350075797"},
    {"column": "new", "max": 1, "code": "3851925837"},
    {"column": "new", "max": 1, "code": "5764987977"},
    {"column": "new", "max": 1, "code": "6493820122"},
]

class ListCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        if content is not None:
            try:
                j = json.loads(content)
                logger.info(j)
            except:
                logger.info(content)
                return False

            if j.has_key("message") and j.has_key("html"):
                return True

        return False


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self, timeout=20):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    #实现<div class="tabCont
    def is_crawl_success(self,url,content):
        if content.find("articleInfo") >= 0 or content.find("404")>=0:

            return True

        return False


def has_news_content(content):
    # d = pq(html.fromstring(content.decode("utf-8","ignore")))
    # title = d('head> title').text().strip()
    # temp = title.split("|")
    # if len(temp) < 2:
    #     return False
    # if temp[0].strip() == "" or temp[0].strip() == "未找到页面":
    #     return False
    return True


def process_news(column, newsurl, content, newspost, download_crawler):
    if has_news_content(content):
        d = pq(html.fromstring(content.decode("utf-8","ignore")))

        key = newsurl.split("/")[-1].replace("i","")

        type = TYPE

        category = None
        title = d('head> title').text().strip()

        r = "content: '(.*?)',.*groupId"

        result = util.re_get_result(r.strip()[:-1], content)
        (b,) = result
        logger.info(b)

        # exit()
        tags = []
        articletags = d("meta[name='keywords']").attr("content")
        if articletags is not None:
            for tag in articletags.replace("，", ",").split(","):
                if tag is not None and tag.strip() != "" and tag not in tags and tag != title:
                    tags.append(tag)



        post = None

        brief = None
        news_time = None
        try:
            r1 = "time: '(.*?)'.*},.*tagInfo"

            result = util.re_get_result(r1, content)
            (post_time,) = result
            logger.info(post_time)
            news_time = extract.extracttime(post_time)
            logger.info("news-time: %s", news_time)
        except:
            pass
        if news_time is None:
            news_time = datetime.datetime.now()
        # exit()
        # article = d('div.post> div.post-content').html()
        # contents = extract.extractContents(newsurl, article)

        logger.info("%s, %s, %s, %s -> %s, %s. %s", key, title, news_time, ":".join(tags), category, brief, post)
        # exit()
        mongo = db.connect_mongo()
        collection_news = mongo.article.news
        if collection_news.find_one({"title": title}) is not None:
            mongo.close()
            return

        flag, domain = url_helper.get_domain(newsurl)
        dnews = {
            "date": news_time - datetime.timedelta(hours=8),
            "title": title,
            "link": newsurl,
            "createTime": datetime.datetime.now(),
            "source": SOURCE,
            "key": key,
            "key_int": int(key),
            "type": type,
            "original_tags": tags,
            "processStatus": 0,
            # "companyId": None,
            "companyIds": [],
            "category": 60101,
            "domain": domain,
            "categoryNames": [],
            # "sectors": [20]
        }
        dcontents = []
        rank = 1
        bb = b.replace('&lt;', "<").replace("&gt;",">").replace("&quot;","\"").replace("&#x3D;","=")
        logger.info(bb)

        contents = extract.extractContents(newsurl, bb, document=False)
        for c in contents:
            logger.info(c["data"])
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
                    (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler, SOURCE, key, "news")
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
        # for c in b.replace("&lt;div&gt;&lt;p&gt;",'').replace("&lt;/p&gt;&lt;/div&gt;","").split('&lt;/p&gt;&lt;p&gt;'):
        #     logger.info(c)
        #     if c.find("转载务必署名来源")>=0 or c.find("&lt;/p&gt;&lt;/div&gt;")>=0 or c.find("&lt;div&gt;&lt;p&gt; ")>=0:
        #         continue
        #     if c.find("img") >= 0:
        #         c = re.sub(r'&lt;(.*)?img.*&quot;0&quot;&gt;',"",c)
        #         dc = {
        #             "rank": rank,
        #             "content": c,
        #             "image": "",
        #             "image_src": "",
        #         }
        #     else:
        #         dc = {
        #             "rank": rank,
        #             "content": c,
        #             "image": "",
        #             "image_src": "",
        #         }
        #     # else:
        #     #     if download_crawler is None:
        #     #         dc = {
        #     #             "rank": rank,
        #     #             "content": "",
        #     #             "image": "",
        #     #             "image_src": c,
        #     #         }
        #     #     else:
        #     #         (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c, download_crawler, SOURCE, key, "news")
        #     #         if imgurl is not None:
        #     #             dc = {
        #     #                 "rank": rank,
        #     #                 "content": "",
        #     #                 "image": str(imgurl),
        #     #                 "image_src": "",
        #     #                 "height": int(height),
        #     #                 "width": int(width)
        #     #             }
        #     #         else:
        #     #             continue
        #
        #     logger.info(c)
        #     dcontents.append(dc)
        #     rank += 1
        dnews["contents"] = dcontents
        if brief is None or brief.strip() == "":
            brief = util.get_brief_from_news(dcontents)
        if post is None or post.strip() == "":
            post = util.get_posterId_from_news(dcontents)

        if download_crawler is None:
            dnews["post"] = post
        else:
            dnews["postId"] = post
        dnews["brief"] = brief

        if news_time > datetime.datetime.now():
            logger.info("Time: %s is not correct with current time", news_time)
            dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
        mid = None
        if title is not None and len(dcontents) > 0:
            # mid = collection_news.insert(dnews)
            nid = parser_mongo_util.save_mongo_news(dnews)
            logger.info("Done: %s", nid)
            pass
        mongo.close()
        # logger.info("*************DONE*************%s",mid)
    return


def run_news(column, crawler, download_crawler):
    while True:
        if len(URLS) == 0:
            return
        URL = URLS.pop(0)

        crawler_news(column, crawler, URL["link"], URL["post"], download_crawler)

def crawler_news(column, crawler, newsurl, newspost, download_crawler):
    retry = 0
    if newsurl.endswith("/"):
        key = newsurl.split("/")[-2]
    else:
        key = newsurl.split("/")[-1]
    newsurl = "https://www.toutiao.com/i%s" % key
    while True:
        result = crawler.crawl(newsurl, agent=True)
        if result['get'] == 'success':
            #logger.info(result["redirect_url"])
            try:
                process_news(column, newsurl, result['content'], newspost, download_crawler)
            except Exception,ex:
                logger.exception(ex)
            break
        retry += 1
        if retry > 20: break



def process(content, flag):
    j = json.loads(content)
    htmlo = j["html"]
    try:
        d = pq(html.fromstring(htmlo.decode("utf-8","ignore")))
        for li in d('section'):
            # logger.info(pq(li))
            try:
                href = pq(li)('a').attr("href").strip()
                link = href
                # logger.info(link)
                if re.search(linkPattern, link):
                    logger.info("Link: %s is right news link", link)
                    title = pq(li)('h3').text().strip()
                    logger.info("title: %s", title)

                    # check mongo data if link is existed
                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news
                    item = collection_news.find_one({"link": link})
                    item2 = collection_news.find_one({"title": title})
                    mongo.close()

                    if ((item is None and item2 is None) or flag == "all") and link not in URLS:
                        linkmap = {
                            "link": link,
                            "post": None
                        }
                        URLS.append(linkmap)

                else:
                    # logger.info(link)
                    pass
            except Exception, e:
                logger.info(e)
                logger.info("cannot get link")
    except Exception, e:
        logger.info(e)
        logger.info("here")
    return len(URLS)


def run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler):
    global CURRENT_PAGE
    cnt = 1
    while True:
        key = CURRENT_PAGE

        if flag == "all":
            if key > column["max"]:
                return
        else:
            if cnt == 0 or key > column["max"]:
                return

        CURRENT_PAGE += 1

        def getASCP():
            t = int(math.floor(time.time()))
            e = hex(t).upper()[2:]
            m = hashlib.md5()
            m.update(str(t).encode(encoding='utf-8'))
            i = m.hexdigest().upper()

            if len(e) != 8:
                AS = '479BB4B7254C150'
                CP = '7E0AC8874BB0985'
                return AS, CP
            n = i[0:5]
            a = i[-5:]
            s = ''
            r = ''
            for o in range(5):
                s += n[o] + e[o]
                r += e[o + 3] + a[o]

            AS = 'A1' + s + e[-3:]
            CP = e[0:3] + r + 'E1'
            return AS, CP

        aas, ccp = getASCP()
        millis = int(round(time.time() * 1000))

        url = "https://m.toutiao.com/pgc/ma_mobile/?page_type=1&max_behot_time=0&aid=&media_id=%s&count=10&version=2&as=%s&cp=%s&timestamp=%s" % (column["code"], aas, ccp, millis)
        headers = {
                    # "Accept-Encoding": 'gzip, deflate, br',
                   "Accept-Language": 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
                   'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36',
                   'Accept': '*/*',
                   # 'Referer': 'https://m.toutiao.com/m6350075797/',
                   'Connection': 'keep-alive',
                   # 'X-CSRFToken': '',
                   "X-Requested-With": "XMLHttpRequest",
                    }
        # pdata = "action=fa_load_postlist&paged=%s" % (key)
        while True:
            # result = listcrawler.crawl(url,agent=True, postdata=pdata)
            result = listcrawler.crawl(url, headers=headers)
            if result['get'] == 'success':
                pass
                try:
                    cnt = process(result['content'], flag)
                    if cnt > 0:
                        logger.info("%s has %s fresh news", url, cnt)
                        logger.info(URLS)
                        # threads = [gevent.spawn(run_news, column, newscrawler, download_crawler) for i in xrange(concurrent_num)]
                        # gevent.joinall(threads)
                        run_news(column, newscrawler, download_crawler)
                        # exit()
                except Exception,ex:
                    logger.exception(ex)
                    cnt = 0
                break



def start_run(concurrent_num, flag):
    global CURRENT_PAGE
    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        listcrawler = ListCrawler()
        newscrawler = NewsCrawler()
        download_crawler = download.DownloadCrawler(use_proxy=False)
        # download_crawler = None
        for column in columns:
            CURRENT_PAGE = 1
            run(flag, column, listcrawler, newscrawler, concurrent_num, download_crawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            time.sleep(60*120)        #30 minutes
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
            download_crawler = download.DownloadCrawler(use_proxy=False)
            # download_crawler = None
            crawler_news({"column": "new", "max": 1}, NewsCrawler(), link, None, download_crawler)
    else:
        start_run(1, "incr")