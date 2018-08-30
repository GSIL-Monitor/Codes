# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson import ObjectId
from pypinyin import pinyin, Style

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("migrate_industry", stream=True)
logger = loghelper.get_logger("migrate_industry")

conn = db.connect_torndb()

def process_news():
    items = conn.query("select * from user_news_mark where (active is null or active='Y')")
    for item in items:
        # if item["userId"] != 214:
        #     continue

        logger.info("userId: %s", item["userId"])
        b = conn.get("select * from bookmark_item where userId=%s and relateType=77001 and relateId=%s",
                     item["userId"], item["newsId"])
        if b is None:
            conn.insert("insert bookmark_item(userId, relateType, relateId, createTime, modifyTime) values(%s,77001,%s,%s,%s)",
                        item["userId"], item["newsId"], item["createTime"], item["createTime"])


def process_user_default_company_rel():
    items = conn.query("select * from user_default_company_rel")
    for item in items:
        # if item["userId"] != 214:
        #     continue

        logger.info("userId: %s", item["userId"])

        b = conn.get("select * from bookmark_item where userId=%s and relateType=77002 and relateId=%s",
                     item["userId"], item["companyId"])
        if b is None:
            conn.insert(
                "insert bookmark_item(userId, relateType, relateId, createTime, modifyTime) values(%s,77002,%s,%s,%s)",
                item["userId"], item["companyId"], item["createTime"], item["createTime"])


def process_user_mylist_rel():
    items = conn.query("select l.*, r.userId from mylist l join user_mylist_rel r on l.id=r.mylistId "
                       "where (l.active is null or l.active='Y') "
                       "order by l.createTime")
    for item in items:
        # if item["userId"] != 214:
        #     continue

        logger.info("userId: %s", item["userId"])
        b = conn.get("select * from bookmark where userId=%s and name=%s", item["userId"], item["name"])
        if b is None:
            bookmark_id = conn.insert(
                "insert bookmark(userId,name,createTime,modifyTime) values(%s,%s,%s,%s)",
                item["userId"], item["name"], item["createTime"], item["modifyTime"]
            )
        else:
            bookmark_id = b["id"]

        rels = conn.query("select * from mylist_company_rel where mylistId=%s order by id", item["id"])
        for rel in rels:
            b = conn.get("select * from bookmark_item where userId=%s and relateType=77002 and relateId=%s",
                         item["userId"], rel["companyId"])
            if b is None:
                bookmark_item_id = conn.insert(
                    "insert bookmark_item(userId, relateType, relateId, createTime, modifyTime) values(%s,77002,%s,%s,%s)",
                    item["userId"], rel["companyId"], rel["createTime"], rel["createTime"])
            else:
                bookmark_item_id = b["id"]

            r = conn.get("select * from bookmark_item_rel where bookmarkId=%s and bookmarkItemId=%s", bookmark_id, bookmark_item_id)
            if r is None:
                conn.insert("insert bookmark_item_rel(bookmarkId,bookmarkItemId,createTime,modifyTime) values(%s,%s,%s,%s)",
                            bookmark_id, bookmark_item_id, rel["createTime"], rel["createTime"])


if __name__ == '__main__':
    process_news()
    process_user_default_company_rel()
    process_user_mylist_rel()