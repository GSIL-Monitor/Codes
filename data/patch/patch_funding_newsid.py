# -*- coding: utf-8 -*-
import os, sys
import requests

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, util

#logger
loghelper.init_logger("patch_funding_newsid", stream=True)
logger = loghelper.get_logger("patch_funding_newsid")

conn = None
mongo = None

def patch_funding_newsid():
    sources = {}

    fundings = conn.query("select * from funding where newsId is null and newsLink is not null")
    for funding in fundings:
        logger.info("id :%s", funding["id"])
        news_link = funding["newsLink"].strip()
        if news_link.startswith("https://www.baidu.com/link"):
            # logger.info("%s", news_link)
            news_link = baidu_get_actual_link(news_link)
            # logger.info("%s", news_link)
            if news_link is not None:
                conn.update("update funding set newsLink=%s where id=%s", news_link, funding["id"])
                # exit()
        logger.info("news: %s", news_link)
        news = mongo.article.news.find_one({"link": news_link})
        if news is not None:
            news_id = str(news["_id"])
            logger.info("newsId: %s", news_id)
            conn.update("update funding set newsId=%s where id=%s", news_id, funding["id"])
            # exit()
        website = get_website_from_url(news_link)
        if website is not None:
            if sources.has_key(website):
                sources[website] += 1
            else:
                sources[website] = 1

    items = sorted(sources.items(), key=lambda d: d[1], reverse=True)
    for link, cnt in items:
        logger.info("%s, %s", cnt, link)


def baidu_get_actual_link(url):
    r = requests.get(url)
    html = r.content
    r = util.re_get_result("URL='(.*?)'", html)
    if r is None:
        return None
    url, = r
    return url


def get_website_from_url(news_link):
    r = util.re_get_result("//(.*?)/", news_link)
    if r is None:
        return None
    website, = r
    return website


def migrate_mongo_funding_news():
    items = list(mongo.company.funding_news.find())
    for item in items:
        funding_id = item["funding_id"]
        logger.info("fundingId: %s", funding_id)
        link = item.get("link")
        if link is None or link.strip() == "":
            mongo.company.funding_news.remove({"_id": item["_id"]})
            continue
        if len(link)>500:
            continue
        funding = conn.get("select * from funding where id=%s", funding_id)
        if funding is None:
            continue
        if funding["newsLink"] is None or funding["newsLink"].strip() == "":
            logger.info("%s", link)
            conn.update("update funding set newsLink=%s where id=%s", link.strip(), funding["id"])
            # exit()


if __name__ == "__main__":
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    migrate_mongo_funding_news()
    patch_funding_newsid()
    mongo.close()
    conn.close()