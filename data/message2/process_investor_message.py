# -*- coding: utf-8 -*-
import os, sys
import datetime
import traceback
from bson.objectid import ObjectId
import process_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../track'))
import track_investor_message

#logger
loghelper.init_logger("process_investor_message", stream=True)
logger = loghelper.get_logger("process_investor_message")


def process_all():
    # 处理3600秒前创建的还未处理的消息
    mid = sys.maxint
    while True:
        conn = db.connect_torndb_proxy()
        ms = conn.query("select * from investor_message where pushStatus=0"
                       " and publishTime < date_sub(now(), interval 3600 SECOND)"
                       " and publishTime > date_sub(now(), interval 7 DAY)"
                       " and id<%s order by id desc limit 1000",
                         mid)
        if len(ms) == 0:
            conn.close()
            break
        mongo = db.connect_mongo()
        for m in ms:
            _mid = m["id"]
            if _mid < mid:
                mid = _mid
            process(_mid, _mongo=mongo, _conn=conn)
        mongo.close()
        conn.close()


def delete_invalid_message():
    logger.info("Start delete invalid investor message...")
    mid = -1
    while True:
        conn = db.connect_torndb_proxy()
        ms = conn.query("select * from investor_message where id>%s order by id limit 1000", mid)
        if len(ms) == 0:
            conn.close()
            break
        mongo = db.connect_mongo()
        for m in ms:
            mid = m["id"]
            if m["active"] == 'N':
                delete(mid, _mongo=mongo)
                continue
            flag = message_valid_check(m, mongo, conn)
            if flag is False:
                logger.info("delete investor_message: %s, relateType: %s, relateId: %s", mid,
                            m["relateType"],
                            m["relateId"])
                # 删除消息
                delete(mid, _mongo=mongo)
                conn.update("update investor_message set active='N', pushStatus=1, modifyUser=1078, modifyTime=now() where id=%s", mid)
            else:
                if m["pushStatus"] == 0:
                    process(mid, _mongo=mongo, _conn=conn)
        mongo.close()
        conn.close()

    logger.info("Delete invalid company message over.")


def publish_check(message, mongo, conn):
    relateType = message["relateType"]

    investor = process_util.get_investor(message["investorId"], _conn=conn)
    if investor["verify"] != 'Y':
        return False
    if investor["online"] != 'Y':
        return False

    if relateType == 10:  # newsId
        # 新闻已审核，不用在检查该消息
        return True
    elif relateType == 70:  # fundingId
        funding = conn.get("select * from funding where id=%s", int(message["relateId"]))
        if funding is not None and funding["verify"] == 'Y':
            return True
    elif relateType == 80:  # companyFAId, detailId为companyId
        companyFaId = message["relateId"]
        if companyFaId is not None:
            company_fa = conn.get("select * from company_fa where id=%s", int(companyFaId))
            if company_fa is not None and company_fa["active"] != 'N':
                # logger.info("message for relateType 80 could auto publish, messageId: %s", message["id"])
                return True
        else:
            # logger.info("message for relateType 80 could auto publish, messageId: %s", message["id"])
            return True
    return False


def message_valid_check(message, mongo, conn):
    relateType = message["relateType"]
    if relateType == 10:  # newsId
        news = mongo.article.news.find_one({"_id": ObjectId(message["relateId"])})
        if news is None:
            return False
        if message["investorId"] not in news["investorIds"]:
            return False
        if news.get("type") != 61000 and news.get("processStatus") != 1:
            # 61000 xiniudata edit news
            return False
    elif relateType == 70:  # fundingId
        funding = conn.get("select * from funding where id=%s", int(message["relateId"]))
        if funding is None or funding["active"] == 'N':
            return False
        if message["trackDimension"] == 7002:  # 投资事件
            rel = conn.get("select * from funding_investor_rel "
                           "where fundingId=%s and investorId=%s and "
                           "(active is null or active !='N')",
                           int(message["relateId"]), message["investorId"])
            if rel is None or rel["active"] == 'N':
                return False

    return True


def process(investor_message_id, _mongo=None, _conn=None):
    try:
        _process(investor_message_id, _mongo=None, _conn=None)
    except Exception, e:
        logger.exception(e)
        traceback.print_exc()


def _process(investor_message_id, _mongo=None, _conn=None):
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn

    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo

    logger.info("investor_message_id: %s", investor_message_id)
    message = conn.get("select * from investor_message where id=%s", investor_message_id)
    flag = message_valid_check(message, mongo, conn)
    if flag is False:
        logger.info("should delete message: %s, relateType: %s, relateId: %s", investor_message_id, message["relateType"],
                    message["relateId"])
        # 删除消息
        # delete(company_message_id, _mongo=mongo)
        # conn.update("update company_message set active='N', pushStatus=1 where id=%s", company_message_id)
    else:
        if message["active"] == 'P':
            flag = publish_check(message, mongo, conn)
            if flag:
                message["active"] = 'Y'
                conn.update("update investor_message set active='Y',modifyTime=now() where id=%s",
                            investor_message_id)

        if message["active"] == 'Y':
            logger.info("publish investor_message_id: %s", investor_message_id)
            # 推送给用户
            subscriptions = conn.query("select * from user_investor_subscription where (active is null or active='Y') and "
                                       "investorId=%s", message["investorId"])
            test_users = process_util.get_test_users()
            for userId in test_users:
                subscriptions.append({"userId": userId})

            for subscription in subscriptions:
                user_id = int(subscription["userId"])
                flag = process_util.insert_user_message(user_id,
                                                        message["publishTime"] + datetime.timedelta(hours=-8),
                                                        investor_message_id=investor_message_id, _mongo=mongo)
                if flag:
                    n = datetime.datetime.now() + datetime.timedelta(minutes=-10)
                    if n < message["publishTime"]:
                        process_util.send_iOS_content_available(user_id, "investor", _conn=conn)

            # 推送给user_message2
            track_investor_message.process(conn, mongo, investor_message_id)

            conn.update("update investor_message set pushStatus=1 where id=%s", investor_message_id)
        else:
            # logger.info("delete company_message_id: %s", company_message_id)
            # TODO 重复删除
            # delete(company_message_id, _mongo=mongo)
            pass

    if _mongo is None:
        mongo.close()
    if _conn is None:
        conn.close()


def delete(investor_message_id, _mongo=None):
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo

    mongo.message.user_message.delete_many({"investorMessageId": investor_message_id})

    # 从user_message2中删除
    track_investor_message.delete(mongo, investor_message_id)

    if _mongo is None:
        mongo.close()


def subscribe(user_id, investor_id):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    ms = conn.query("select * from investor_message where investorId=%s and active='Y' order by publishTime desc limit 100", investor_id)
    for m in ms:
        process_util.insert_user_message(user_id, m["publishTime"] + datetime.timedelta(hours=-8),
                                         investor_message_id=m["id"], _mongo=mongo)
    mongo.close()
    conn.close()


def unsubscribe(user_id, investor_id):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    ms = conn.query("select * from investor_message where investorId=%s and active='Y'", investor_id)
    for m in ms:
        mongo.message.user_message.delete_many({"investorMessageId": m["id"], "userId": user_id})
    mongo.close()
    conn.close()


if __name__ == '__main__':
    process_all() # Test
    # process(22351)