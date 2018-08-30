# -*- coding: utf-8 -*-
import os, sys
import datetime
from bson.objectid import ObjectId

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("patch", stream=True)
logger = loghelper.get_logger("patch")


#user_message增加type
def patch_user_message_type():
    mongo = db.connect_mongo()
    while True:
        items = list(mongo.message.user_message.find({"type":{"$exists":False}}).limit(1000))
        if len(items) == 0:
            break
        for item in items:
            logger.info(item["_id"])
            if item.get("topicMessageId") is not None:
                mongo.message.user_message.update_one({"_id":item["_id"]},{"$set":{"type":5020}})
            elif item.get("companyMessageId") is not None:
                mongo.message.user_message.update_one({"_id": item["_id"]}, {"$set": {"type": 5010}})
            else:
                logger.info("Error!")
                exit()
    mongo.close()


#topic_tab_message_rel缺失
def patch_topic_tab_message_rel():
    cnt = 0
    conn = db.connect_torndb()
    ms = conn.query("select m.* from topic_message m left join topic_tab_message_rel r on m.id=r.topicMessageId where m.active!='N' and r.id is null")
    for m in ms:
        logger.info(m["id"])
        conn.update("update topic_message set tabStatus=0 where id=%s", m["id"])
        cnt += 1
    conn.close()
    logger.info("total: %s", cnt)


def patch_publishtime_4_topic_mesasge():
    conn = db.connect_torndb()
    sql = "select topicId,publishTime,count(*) cnt from topic_message group by topicId,publishTime having cnt>1"
    results = conn.query(sql)
    for item in results:
        topic_id = item["topicId"]
        publish_time = item["publishTime"]
        cnt = item["cnt"]
        logger.info("topicId: %s, publishTime: %s, cnt: %s", topic_id, publish_time, cnt)
        ms = conn.query("select * from topic_message where topicId=%s and publishTime=%s order by id", topic_id, publish_time)
        for m in ms[1:]:
            publish_time += datetime.timedelta(milliseconds=1)
            while True:
                _m = conn.get("select * from topic_message where topicId=%s and publishTime=%s limit 1", topic_id, publish_time)
                if _m is not None:
                    publish_time += datetime.timedelta(milliseconds=1)
                else:
                    break
            logger.info("id: %s, adjust time: %s", m["id"], publish_time)
            conn.update("update topic_message set publishTime=%s where id=%s", publish_time, m["id"])
            # exit()
    conn.close()


def patch_publishtime_4_topic_company():
    conn = db.connect_torndb()
    sql = "select topicId,publishTime,count(*) cnt from topic_company group by topicId,publishTime having cnt>1"
    results = conn.query(sql)
    for item in results:
        topic_id = item["topicId"]
        publish_time = item["publishTime"]
        cnt = item["cnt"]
        logger.info("topicId: %s, publishTime: %s, cnt: %s", topic_id, publish_time, cnt)
        ms = conn.query("select * from topic_company where topicId=%s and publishTime=%s order by id", topic_id, publish_time)
        for m in ms[1:]:
            publish_time += datetime.timedelta(milliseconds=1)
            while True:
                _m = conn.get("select * from topic_company where topicId=%s and publishTime=%s limit 1", topic_id, publish_time)
                if _m is not None:
                    publish_time += datetime.timedelta(milliseconds=1)
                else:
                    break
            logger.info("id: %s, adjust time: %s", m["id"], publish_time)
            conn.update("update topic_company set publishTime=%s where id=%s", publish_time, m["id"])
            # exit()
    conn.close()


def patch_publishtime_4_company_mesasge():
    conn = db.connect_torndb()
    sql = "select publishTime,count(*) cnt from company_message group by publishTime having cnt>1"
    results = conn.query(sql)
    for item in results:
        publish_time = item["publishTime"]
        cnt = item["cnt"]
        logger.info("publishTime: %s, cnt: %s", publish_time, cnt)
        ms = conn.query("select * from company_message where publishTime=%s order by id", publish_time)
        for m in ms[1:]:
            publish_time += datetime.timedelta(milliseconds=1)
            while True:
                _m = conn.get("select * from company_message where publishTime=%s limit 1", publish_time)
                if _m is not None:
                    publish_time += datetime.timedelta(milliseconds=1)
                else:
                    break
            logger.info("id: %s, adjust time: %s", m["id"], publish_time)
            conn.update("update company_message set publishTime=%s where id=%s", publish_time, m["id"])
            # exit()
    conn.close()

def patch_user_message_createtime():
    mongo = db.connect_mongo()
    items = list(mongo.message.user_message.find({"createTime": {"$gt":datetime.datetime.utcnow()}}))
    for item in items:
        logger.info(item["createTime"])
        mongo.message.user_message.update_one({"_id":item["_id"]},
                                              {"$set":{"createTime":item["createTime"]+datetime.timedelta(hours=-8)}})
    mongo.close()

if __name__ == '__main__':
    # patch_user_message_type()
    # patch_topic_tab_message_rel()
    # patch_publishtime_4_topic_mesasge()
    # patch_publishtime_4_topic_company()
    patch_publishtime_4_company_mesasge()
    # patch_user_message_createtime()