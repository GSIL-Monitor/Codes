# -*- coding: utf-8 -*-
import os, sys, datetime, re, json,time
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
import loghelper,extract,db, util,url_helper,download, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util2'))
import parser_mysql_util
import parser_mongo_util


#logger
loghelper.init_logger("crawler_lanxiong_news", stream=True)
logger = loghelper.get_logger("crawler_lanxiong_news")

NEWSSOURCE = "lanxiong"
# RETRY = 3
# TYPE = 60001
SOURCE =13828
URLS = []
# links=[]
# CURRENT_PAGE = 1
# linkPattern = "Xfeature/view\?aid=\d+"
# Nocontents = []
# columns = [
#     {"column": None, "max": 3},
# ]
categoryDict={
            u'公司':{'category':None,'type':60001},
            u'观点':{'category':60107,'type':60003},
            u'报告':{'category':60107,'type':60003},
            u'独家专访':{'category':60103,'type':60001},

}

class Hotcrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('<div class="index_hot or">')>=0:
                return True
            return False
        return False

class Indexcrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        try:
            j=json.loads(content)
            return True
        except Exception, ex:
            return False

class Contentcrawler(BaseCrawler.BaseCrawler):
    def __init__(self,timeout=30):
        BaseCrawler.BaseCrawler.__init__(self, timeout=timeout)

    def is_crawl_success(self, url, content):
        if content is not None:
            if content.find('<div class="article or">')>=0:
                return True
            return False
        return False


def process(crawler):
    while True:
        if len(URLS)==0:return
        linkDict=URLS.pop(0)
        retries=0


        while True:
            if retries>6:break
            retries+=1

            download_crawler = download.DownloadCrawler(use_proxy=False)
            url=linkDict['href']
            result = crawler.crawl(url)
            if result['get'] == 'success':
                d=pq(result['content'])

                title=linkDict['title']
                key=url.split('=')[-1]

                if categoryDict.has_key(linkDict['category']):
                    type=categoryDict[linkDict['category']]['type']
                    category=categoryDict[linkDict['category']]['category']
                else:
                    type=60001
                    category=None

                brief=linkDict['brief']
                postraw=linkDict['post']


                tags=[]
                for tag in d('.txt span em').text().split():
                    if tag.strip() not in tags:tags.append(tag)
                for tag in d('.pag span').text().split():
                    if tag.strip() not in tags: tags.append(tag)

                news_time = linkDict['date']

                flag, domain = url_helper.get_domain(url)
                dnews = {
                    "date": news_time - datetime.timedelta(hours=8),
                    "title": title,
                    "link": url,
                    "createTime": datetime.datetime.now(),
                    "source": SOURCE,
                    "key": key,
                    "key_int": int(key),
                    "type": type,
                    "original_tags": tags,
                    "processStatus": 0,
                    # "companyId": None,
                    "companyIds": [],
                    "category": category,
                    "domain": domain,
                    "categoryNames": []
                }

                article = d('.article .top').html()
                contents = extract.extractContents(url, article)
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
                            (imgurl, width, height) = parser_mysql_util.get_logo_id_new(c["data"], download_crawler,
                                                                                        SOURCE, key, "news")

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
                dnews["contents"] = dcontents

                if brief is None or brief.strip() == "":
                    brief = util.get_brief_from_news(dcontents)

                # posturl = parser_mysql_util.get_logo_id(postraw, download_crawler, SOURCE, key, "news")
                (posturl, width, height) = parser_mysql_util.get_logo_id_new(postraw, download_crawler, SOURCE, key,
                                                                             "news")
                if posturl is not None:
                    post = str(posturl)
                else:
                    post = None
                if post is None or post.strip() == "":
                    post = util.get_posterId_from_news(dcontents)

                if download_crawler is None:
                    dnews["post"] = post
                else:
                    dnews["postId"] = post
                dnews["brief"] = brief

                mongo = db.connect_mongo()
                collection_news = mongo.article.news
                # update link content with oldId
                item = collection_news.find_one({"link": url})
                if item is None:
                    nid = parser_mongo_util.save_mongo_news(dnews)
                    logger.info("Done: %s", nid)
                else:
                    logger.info("update %s",url)
                    # oldId = collection_news.find_one({"link": url})['_id']
                    # collection_news.delete_one({"link": url})
                    # dnews['_id'] = oldId
                    # collection_news.insert(dnews)
                mongo.close()
                logger.info("%s, %s, %s, %s, %s, %s, %s", key, title, news_time, category, " ".join(tags), brief, post)
                # logger.info("*************DONE*************")
                break

def get_link(crawler,concurrent_num,contentcrawler):
    for page in xrange(5):
        url='http://lanxiongsports.com/mservice/?c=news&format=json&page=%s'%(page+1)
        while True:
            result = crawler.crawl(url)
            if result['get'] == 'success':
                j = json.loads(result['content'])

                for item in j['items']:
                    if item.has_key('ad_code'):continue
                    key = item['id']
                    title = item['title']
                    post = item['logo']
                    brief = item['summary']
                    category = item['_category']['name']
                    date = item['created_at']

                    if not isinstance(date,datetime.datetime):
                        logger.info('%s not datetime',date)
                        date=extract.extracttime(date)

                    href='http://lanxiongsports.com/?c=posts&a=view&id=%s'%key
                    linkDict = {
                        "href": href,
                        "title": title,
                        "post": post,
                        "brief": brief,
                        "category": category,
                        "date": date,
                    }

                    mongo = db.connect_mongo()
                    collection_news = mongo.article.news

                    item = collection_news.find_one({"link": href,'title':title})
                    if item is None:
                        # logger.info( 'not exists %s ,%s '%(href,title))
                        URLS.append(linkDict)
                    else:
                        logger.info('already exists %s , %s',href,title)
                    mongo.close()


                break

        if len(URLS) == 0 and page>0 :
            logger.info('page %s got no fresh news,quiting............',page+1)
            break

        threads = [gevent.spawn(process, contentcrawler) for i in
                   xrange(concurrent_num)]
        gevent.joinall(threads)




        # break

def get_hot(crawler,concurrent_num,contentcrawler):
    url='http://lanxiongsports.com/'
    while True:
        result = crawler.crawl(url)
        if result['get'] == 'success':
            d = pq(html.fromstring(result['content'].decode("utf-8")))
            for i in d('div.index_hot')('a'):
                href=d(i).attr('href')
                if href.find('http://lanxiongsports.com/')<0:
                    print href,'not a url'
                    continue
                title= d(i)('h1').text().strip()
                category=d(i)('.tit').text().strip()
                pic=d(i)('.pic').attr('style').strip()
                post=re.search('https?://.*.(jpe?g|gif|png)', pic).group(0)

                # date=post.replace('.jpg','').split('/')[-1]
                date=re.sub('.(jpe?g|gif|png)','',post).split('/')[-1]
                x = time.localtime(int(date))
                timestr = time.strftime('%Y-%m-%d %H:%M:%S', x)
                date=datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')

                linkDict = {
                    "href": href,
                    "title": title,
                    "post": post,
                    "brief": None,
                    "category": category,
                    "date": date,
                }
                # print linkDict


                mongo = db.connect_mongo()
                collection_news = mongo.article.news

                item = collection_news.find_one({"link": href, 'title': title})
                if item is None:
                    logger.info( 'not exists %s ,%s '%(href,title))
                    URLS.append(linkDict)
                else:
                    logger.info('already exists %s , %s', href, title)
                mongo.close()

            break

    threads = [gevent.spawn(process, contentcrawler) for i in
               xrange(concurrent_num)]
    gevent.joinall(threads)


# get_hot(Indexcrawler())

def start_run(concurrent_num, flag):

    while True:
        logger.info("%s news %s start...", NEWSSOURCE, flag)
        hotcrawler = Hotcrawler()
        indexcrawler = Indexcrawler()
        contentcrawler = Contentcrawler()
        # download_crawler = download.DownloadCrawler(use_proxy=False)

        get_hot(hotcrawler,concurrent_num,contentcrawler)
        get_link(indexcrawler,concurrent_num,contentcrawler)

        logger.info("%s news %s end.", NEWSSOURCE, flag)

        if flag == "incr":
            logger.info('sleeping')
            gevent.sleep(60*8)        #30 minutes
        else:
            return
            #gevent.sleep(86400*3)   #3 days


if __name__ == "__main__":
    start_run(1,'incr')


