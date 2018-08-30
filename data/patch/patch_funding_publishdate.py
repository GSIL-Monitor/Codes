# -*- coding: utf-8 -*-
import os, sys
import datetime, time
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch_funding_publishdate", stream=True)
logger = loghelper.get_logger("patch_funding_publishdate")

conn = db.connect_torndb()
mongo = db.connect_mongo()


# def main():
#     items = conn.query("select corporateId, newsId, count(*) cnt from funding "
#                        "where (active is null or active='Y') and newsId is not null "
#                        "group by corporateId, newsId "
#                        "having cnt>1")
#     for item in items:
#         corporate_id = item["corporateId"]
#         logger.info("corporateId: %s", corporate_id)
#         fundings = list(conn.query("select * from funding where (active is null or active='Y') and "
#                               "corporateId=%s and newsId=%s "
#                               "order by fundingDate desc",
#                               corporate_id, item["newsId"]))
#         logger.info("keep fundingId: %s", fundings[0]["id"])
#         for funding in fundings[1:]:
#             logger.info("revise fundingId: %s", funding["id"])
#             conn.update("update funding set publishDate=null, newsId=null, source=null where id=%s", funding["id"])
#         # exit()

def get_possible_publish_date(funding):
    if funding["newsId"] is not None and funding["newsId"] != "":
        try:
            news = mongo.article.news.find_one({"_id": ObjectId(funding["newsId"])})
        except:
            logger.info(funding)

        if news is not None:
            return "internalnews", news["date"]

    funding_news = mongo.company.funding_news.find_one({"funding_id": funding["id"]})
    if funding_news is not None:
        return "externalnews", funding_news.get("date")

    if funding["source"] == 69002:
        return "gongshang", funding["gsDetectdate"]

    return None, None


def main1():
    items = conn.query("select * from funding where (active is null or active='Y')")
    for item in items:
        publish_date = item["publishDate"]
        source, possible_publish_date = get_possible_publish_date(item)
        # logger.info("%s, %s, %s", publish_date, source, possible_publish_date)

        if publish_date is None and possible_publish_date is None:
            continue

        if publish_date is not None and possible_publish_date is None and item["fundingDate"] is not None:
            t = publish_date - item["fundingDate"]
            if abs(t.days) < 1:
                continue

        if publish_date is not None and possible_publish_date is not None:
            if type(possible_publish_date) != datetime.datetime:
                # logger.info(" %s date error! fundingId: %s, date: %s", source, item["id"], possible_publish_date)
                continue

            t = publish_date - possible_publish_date
            if abs(t.days) < 1:
                continue

        if publish_date is not None and possible_publish_date is None:
            company = conn.get("select * from company where id=%s", item["companyId"])
            if company["active"] == 'N':
                continue

            logger.info("fundingId: %s, company code: %s, source: %s, possible_publish_date: %s, publish_date: %s",
                        item["id"], company["code"], source, possible_publish_date, publish_date)
            if publish_date < datetime.datetime.strptime("2017-08-01", "%Y-%m-%d"):
                conn.update("update funding set publishDate=null where id=%s", item["id"])
                # exit()


# news date + 8h = funding.publishDate
def main2():
    items = conn.query("select * from funding where (active is null or active='Y') and newsId is not null")
    for item in items:
        if item["publishDate"] is None:
            continue
        news_id = item["newsId"]
        try:
            news = mongo.article.news.find_one({"_id": ObjectId(news_id)})
        except:
            logger.info("Error! fundingId: %s, newsId: %s", item["id"], news_id)
            continue
        if news is None:
            continue
        if news["date"] == item["publishDate"]:
            publish_date = item["publishDate"] + datetime.timedelta(hours=8)
            logger.info("fundingId: %s, publishDate: %s, newsDate: %s, patched publishDate: %s", item["id"], item["publishDate"], news["date"], publish_date)
            conn.update("update funding set publishDate=%s where id=%s",
                        publish_date, item["id"])
            # exit()


def patch():
    fundings = conn.query("select * from funding "
                          "where (active is null or active='Y') and "
                          "publishDate is null and fundingDate is not null and "
                          "(source is null or source != 69002)")
    for funding in fundings:
        logger.info("fundingId: %s, fundingDate: %s, publishDate: %s",
                    funding["id"], funding["fundingDate"], funding["publishDate"])
        conn.update("update funding set publishDate=fundingDate where id=%s", funding["id"])
        # exit()


if __name__ == "__main__":
    while True:
        logger.info("Begin...")
        patch()
        logger.info("End.")
        time.sleep(60)
