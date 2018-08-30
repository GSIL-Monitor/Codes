# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
import pymongo
import datetime
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../support'))
import loghelper, download, config, util,url_helper
import extract
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import parser_db_util

#logger
loghelper.init_logger("itjuzi_news_parser", stream=True)
logger = loghelper.get_logger("itjuzi_news_parser")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news


SOURCE = 13030  #ITJUZI
TYPE = 36006    #新闻


def process():
    logger.info("itjuzi_news_parser begin...")
    items = parser_db_util.find_process(SOURCE, TYPE)
    for item in items:
        logger.info(item["key_int"])
        logger.info(item["url"])
        flag = parser(item)
        if flag:
            parser_db_util.update_processed(item["_id"])
        #break
    logger.info("itjuzi_news_parser end.")


def get_category(tags):
    if tags is None:
        return None

    for tag in tags:
        if tag == "产品":
            return 60102
        if tag == "资本":
            return 60101
        if tag == "采访报道":
            return None
        if tag == "人事变动":
            return 60103
        if tag == "传言预测":
            return 60105
        if tag == "关停倒闭":
            return 60199
        if tag == "内部消息":
            return 60105
        if tag == "数据信息":
            return 60105
    return None


def parser(news):
    if news is None:
        return True

    try:
        company_key_int = news["company_key_int"]
        url = news["url"]
        news_date = news["news_date"]
        html = news["content"]

        if html.find("404未找到页面") != -1:
            logger.info("404未找到页面")
            return True

        conn = db.connect_torndb()
        source_company = conn.get("select * from source_company where source=%s and sourceId=%s", SOURCE,company_key_int)
        conn.close()
        if source_company is None:
            logger.info("source_company=%s not found!", company_key_int)
            return False

        if source_company["companyId"] is None:
            logger.info("source_company=%s not aggregated yet!", company_key_int)
            return False

        company_id = source_company["companyId"]

        contents = extract.extractContents(url, html)

        if news["url"].strip().lower().startswith("http://36kr.com"):
            #不保存36kr的新闻,36kr新闻由其他程序抓取, 36kr新闻内容不能由extract得到
            return True

        if news["url"].strip().lower().startswith("http://www.ctsbw.com"):
            #www.ctsbw.com的新闻不能正确extract
            return True

        #item = collection_news.find_one({"companyId":company_id, "title":news["title"]})
        item = collection_news.find_one({"link":news["url"]})
        if item is None:
            item = collection_news.find_one({"title":news["title"]})

        category = get_category(news.get("original_tags"))

        if item is None:
            flag, domain = url_helper.get_domain(news["url"])
            dnews = {
                "key": news["key"],
                "key_int": news["key_int"],
                "companyId":company_id,
                "date":news_date - datetime.timedelta(hours=8),
                "title":news["title"],
                "link":news["url"],
                "domain":domain,
                "createTime":news["date"],
                "source":SOURCE,
                #"companyIds":[company_id],
                "type":60001,
                "original_tags":news.get("original_tags"),
                "category":category,
                "processStatus": 0
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
                    if c["data"].startswith("http://upload.iheima.com"):
                        continue

                    dc = {
                            "rank":rank,
                            "content":"",
                            "image":"",
                            "image_src":c["data"],
                        }
                dcontents.append(dc)
                rank += 1
            dnews["contents"] = dcontents
            post = util.get_poster_from_news(dcontents)
            brief = util.get_brief_from_news(dcontents)
            dnews["post"] = post
            dnews["brief"] = brief
            if news_date > datetime.datetime.now():
                logger.info("Time: %s is not correct with current time", news_date)
                dnews["date"] = datetime.datetime.now() - datetime.timedelta(hours=8)
            collection_news.insert(dnews)

        return True
    except Exception,ex:
        logger.exception(ex)

    return False

if __name__ == "__main__":
    process()