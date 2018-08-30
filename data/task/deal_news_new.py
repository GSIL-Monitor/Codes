# -*- coding: utf-8 -*-
import os, sys
import time,datetime

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util
import extract, extractArticlePublishedDate

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../spider2/crawler'))
import BaseCrawler

#logger
loghelper.init_logger("deal_news_new", stream=True)
logger = loghelper.get_logger("deal_news_new")


class NewsCrawler(BaseCrawler.BaseCrawler):
    def __init__(self):
        BaseCrawler.BaseCrawler.__init__(self)

    def is_crawl_success(self,url,content):
        if content.find("</html>") == -1:
            return False

        return True

news_crawler = NewsCrawler()


def crawler(company_id, link):
    retry_time = 0
    while True:
        result = news_crawler.crawl(link, agent=False)
        if result['get'] == 'success':
            #logger.info(result["content"])
            html = util.html_encode(result["content"])
            #logger.info(html)
            contents = extract.extractContents(link, html)

            title = extract.extractTitle(html)
            date = extractArticlePublishedDate.extractArticlePublishedDate(link, html)

            dnews = {
                "companyId":company_id,
                "date": date,
                "title": title,
                "link": link,
                "createTime": datetime.datetime.now(),
                "source":13001
            }

            dcontents = []
            rank = 1
            for c in contents:
                if c["type"] == "text":
                    dc = {
                            "rank":rank,
                            "content":c["data"],
                            "image":"",
                            "image_src":"",
                        }
                else:
                    dc = {
                            "rank":rank,
                            "content":"",
                            "image":"",
                            "image_src":c["data"],
                        }
                dcontents.append(dc)
                rank += 1
            dnews["contents"] = dcontents

            logger.info(dnews)

            mongo = db.connect_mongo()
            _id = mongo.article.news.insert_one(dnews).inserted_id
            mongo.close()

            return _id

        retry_time += 1
        if retry_time > 10:
            break

    return None


def process(item):
    logger.info("process: %s, %s", item["_id"], item["link"])
    deal_id = item["dealId"]
    if deal_id is None:
        set_proceed(item["_id"], "F")
        return

    conn = db.connect_torndb()
    deal = conn.get("select * from deal where id=%s", deal_id)
    conn.close()
    if deal is None:
        set_proceed(item["_id"], "F")
        return

    company_id = deal["companyId"]

    mongo = db.connect_mongo()
    news = mongo.article.news.find_one({"link": item["link"]})
    mongo.close()

    if news:
        #已存在
        mongo = db.connect_mongo()
        if news["companyId"] is None:
            mongo.article.news.update({"_id":news["_id"]}, {"$set":{"companyId":company_id}})

        companyIds = news.get("companyIds",[])
        if company_id not in companyIds:
            companyIds.append(company_id)
            mongo.article.news.update({"_id":news["_id"]}, {"$set":{"companyIds":companyIds}})

        rel = mongo.article.deal_news_rel.find({"dealId":deal_id, "newsId":news["_id"]})
        if rel is None:
            rel = {"dealId":deal_id,
                   "newsId":news["_id"],
                   "createTime":datetime.datetime.now(),
                   "userId":item["userId"]}
            mongo.article.deal_news_rel.insert(rel)
        mongo.close()
    else:
        _id = crawler(company_id, item["link"])
        if _id:
            mongo = db.connect_mongo()
            rel = {"dealId":deal_id,
                   "newsId":_id,
                   "createTime":datetime.datetime.now(),
                   "userId":item["userId"]}
            mongo.article.deal_news_rel.insert(rel)
            mongo.close()
            set_proceed(item["_id"], "S")
        else:
            set_proceed(item["_id"], "F")


def set_proceed(_id,proceed):
    mongo = db.connect_mongo()
    mongo.article.deal_news.update({"_id":_id},{"$set":{"proceed":proceed}})
    mongo.close()


if __name__ == '__main__':
    while True:
        logger.info("Start...")
        mongo = db.connect_mongo()
        items = list(mongo.article.deal_news.find({"proceed":'Y'}))
        mongo.close()

        #create source_company, wait to expand and aggregate
        for item in items:
            process(item)

        logger.info("End.")

        if len(items) == 0:
            time.sleep(60)