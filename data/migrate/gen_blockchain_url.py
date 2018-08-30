# -*- coding: utf-8 -*-
import os, sys
import datetime, time
import json
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import util
import config
import db
import loghelper

#logger
loghelper.init_logger("find_funding", stream=True)
logger = loghelper.get_logger("find_funding")


def company():
    fo = open("logs/urls.txt", "w")
    conn = db.connect_torndb()
    items = conn.query("select c.code from company c join company_tag_rel r on c.id=r.companyId "
                       "where (c.active is null or c.active='Y') and"
                       "(r.active is null or r.active='Y') and "
                       "r.tagId=175747")
    for item in items:
        url = "http://www.juliandata.com/company/%s/overview" % item["code"]
        fo.write(url + "\n")

    conn.close()
    fo.close()


def investor():
    fo = open("logs/urls_investor.txt", "w")
    conn = db.connect_torndb()
    items = conn.query("select * from investor_tag_rel r join investor i on i.id=r.investorId "
                       "where (r.active is null or r.active='Y') and "
                       "(i.active is null or i.active='Y') and "
                       "r.tagId=175747 and i.online='Y'")
    for item in items:
        url = "http://www.juliandata.com/investor/%s/overview" % item["id"]
        fo.write(url + "\n")

    conn.close()
    fo.close()


def news():
    fo = open("logs/urls_news.txt", "w")
    mongo = db.connect_mongo()
    items = mongo.article.news.find({"source": {"$in":[13860,13867,13868,13869, 13870, 13871, 13872]}, "type":60001},{"_id":1}).sort("date",-1).limit(2000)
    for item in items:
        url = "http://www.juliandata.com/news/%s" % item["_id"]
        fo.write(url + "\n")

    mongo.close()
    fo.close()


if __name__ == "__main__":
    news()