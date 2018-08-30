# -*- coding: utf-8 -*-
import os, sys
import traceback
import datetime, time
import process_util

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("push_message2ios", stream=True)
logger = loghelper.get_logger("push_message2ios")


def main(type):
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    user_ids = conn.query("select distinct userId from user_token where deviceId is not null and deviceId !=''")
    for _user_id in user_ids:
        user_id = _user_id["userId"]
        try:
            push_user(user_id, type, conn=conn, mongo=mongo)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
    mongo.close()
    conn.close()


def push_user(user_id, type, conn=None, mongo=None, test=False):
    if conn is None:
        conn = db.connect_torndb()
    if mongo is None:
        mongo = db.connect_mongo()
    logger.info("userId: %s", user_id)
    last_user_message_createtime = None
    if test is False:
        last_user_message_createtime = get_user_last_message_createtime(user_id, conn)
    current = datetime.datetime.now()
    if last_user_message_createtime is None:
        last_user_message_createtime = current + datetime.timedelta(hours=-24)

    # for mongo usage
    last_user_message_createtime += datetime.timedelta(hours=-8)

    if type == "company":
        badge, message = gen_user_company_message(user_id, last_user_message_createtime, conn, mongo)
        logger.info("company message badge: %s", badge)
        logger.info(message)
        if badge > 0:
            process_util.send_iOS_message1(user_id, badge, message, "company", conn, test=False)

    if type == "topic":
        badge, message = gen_user_topic_message(user_id, last_user_message_createtime, conn, mongo)
        logger.info("topic message badge: %s", badge)
        logger.info(message)
        if badge > 0:
            process_util.send_iOS_message1(user_id, badge, message, "topic", conn, test=False)

    if type == "investor":
        badge, message = gen_user_investor_message(user_id, last_user_message_createtime, conn, mongo)
        logger.info("investor message badge: %s", badge)
        logger.info(message)
        if badge > 0:
            process_util.send_iOS_message1(user_id, badge, message, "investor", conn, test=False)

    if type == "updateLastUserMessageCreateTime":
        conn.update("update user_behavior set lastUserMessageCreateTime=%s where userId=%s", current, user_id)


def get_user_last_message_createtime(user_id, conn):
    item = conn.get("select * from user_behavior where userId=%s order by lastUserMessageCreateTime desc limit 1", user_id)
    if item is None:
        return None
    else:
        return item["lastUserMessageCreateTime"]


def gen_user_company_message(user_id, last_user_message_createtime, conn, mongo):
    badge = mongo.message.user_message.find(
        {"userId": user_id, "type": 5010, "createTime": {"$gt": last_user_message_createtime}}).count()
    # if badge == 0 and user_id in [3142]:
    #     badge = 10
    message = ""
    if badge > 0:
        items = mongo.message.user_message.find(
            {"userId": user_id, "type": 5010, "createTime": {"$gt": last_user_message_createtime}}).sort("createTime", -1).limit(2)
        message = u"您关注的公司产生了%s条最新动态，\n" % badge
        i = 1
        for item in items:
            cm = conn.get("select * from company_message where id=%s", item["companyMessageId"])
            if cm is None or cm["active"] != "Y":
                continue
            if cm["trackDimension"] == 5001:
                message += u"%s. 股东变更，%s\n" % (i, cm["message"])
            elif cm["trackDimension"] == 5002:
                message += u"%s. 注册资本变更，%s\n" % (i, cm["message"])
            else:
                message += "%s. %s\n" % (i, cm["message"])
            i += 1
        if badge > 2:
            message += "..."
    return badge, message


def gen_user_topic_message(user_id, last_user_message_createtime, conn, mongo):
    badge = mongo.message.user_message.find(
        {"userId": user_id, "type": 5020, "createTime": {"$gt": last_user_message_createtime}}).count()
    message = ""
    if badge > 0:
        items = mongo.message.user_message.find(
            {"userId": user_id, "type": 5020, "createTime": {"$gt": last_user_message_createtime}}).sort("createTime",
                                                                                                         -1).limit(2)
        message = u"您关注的主题产生了%s条最新动态，\n" % badge
        i = 1
        for item in items:
            cm = conn.get("select * from topic_message where id=%s", item["topicMessageId"])
            if cm is None or cm["active"] != "Y":
                continue
            message += "%s. %s\n" % (i, cm["message"])
            i += 1
        if badge > 2:
            message += "..."
    return badge, message


def gen_user_investor_message(user_id, last_user_message_createtime, conn, mongo):
    badge = mongo.message.user_message.find(
        {"userId": user_id, "type": 5030, "createTime": {"$gt": last_user_message_createtime}}).count()
    message = ""
    if badge > 0:
        items = mongo.message.user_message.find(
            {"userId": user_id, "type": 5030, "createTime": {"$gt": last_user_message_createtime}}).sort("createTime",
                                                                                                         -1).limit(2)
        message = u"您关注的投资机构产生了%s条最新动态，\n" % badge
        i = 1
        for item in items:
            cm = conn.get("select * from investor_message where id=%s", item["investorMessageId"])
            if cm is None or cm["active"] != "Y":
                continue
            message += "%s. %s\n" % (i, cm["message"])
            i += 1
        if badge > 2:
            message += "..."
    return badge, message


if __name__ == '__main__':
    if len(sys.argv) == 1:
        logger.info("push company message")
        main("company")
        logger.info("sleep...")
        time.sleep(30*60)
        logger.info("push topic message")
        main("topic")
        logger.info("sleep...")
        time.sleep(30 * 60)
        logger.info("push investor message")
        # main("investor") # TODO test
        main("updateLastUserMessageCreateTime")
        logger.info("push end.")
    elif len(sys.argv) == 2:
        user_id = int(sys.argv[1])
        push_user(user_id, "company", test=False)
        push_user(user_id, "topic", test=False)
        # push_user(user_id, "investor", test=True) # TODO test
        # main("updateLastUserMessageCreateTime")
    else:
        logger.info("wrong arg")