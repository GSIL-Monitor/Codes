# -*- coding: utf-8 -*-
import os, sys
import datetime
import traceback
from bson.objectid import ObjectId
import umeng
import process_util
import process_message

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("process_topic_message", stream=True)
logger = loghelper.get_logger("process_topic_message")


def process_all():
    # 处理60秒前创建的还未处理的消息
    conn = db.connect_torndb_proxy()
    items1 = conn.query(
        "select * from topic_message"
        " where tabStatus=0 and"
        " publishTime < date_sub(now(), interval 60 SECOND)")
    items2 = conn.query(
        "select * from topic_message"
        " where active='Y' and pushStatus=0 and"
        " publishTime < date_sub(now(), interval 3600 SECOND)")
    conn.close()
    for item in items1:
        process_tab(item["id"])
    for item in items2:
        process_one_message(item["id"])


def delete_invalid_message():
    logger.info("Start delete invalid topic message...")
    mid = -1
    while True:
        conn = db.connect_torndb_proxy()
        ms = conn.query("select * from topic_message where id>%s order by id limit 1000", mid)
        if len(ms) == 0:
            conn.close()
            break
        mongo = db.connect_mongo()
        for m in ms:
            mid = m["id"]
            if m["active"] == 'N':
                delete_invalid(m, conn, mongo)
                continue
            flag = message_valid_check(m, mongo, conn)
            if flag is False:
                logger.info("delete message: %s, relateType: %s, relateId: %s", mid,
                            m["relateType"],
                            m["relateId"])
                # 删除消息
                delete_invalid(m, conn, mongo)
            elif flag == 'A':
                conn.update("update topic_message set active='P',modifyTime=now(), modifyUser=1078"
                            " where id=%s", m["id"])
                mongo.message.user_message.delete_many({"topicMessageId": m["id"]})
        mongo.close()
        conn.close()

    logger.info("Delete invalid topic message over.")


def message_valid_check(message, mongo, conn):
    topicMessageId = message["id"]
    companies = conn.query("select c.* from topic_company tc join topic_message_company_rel r on tc.id=r.topicCompanyId"
                       " join company c on c.id=tc.companyId where r.topicMessageId=%s", topicMessageId)

    if len(companies) > 0:
        for company in companies:
            if company["active"] == 'A' or company["active"] == 'P':
                return "A"      #消息相关的公司还未发布，应将消息状态改为未发布状态，等待人工审核

        flag = False
        for company in companies:
            if company["active"] is None or company["active"] == 'Y':
                flag = True
                break
        if flag is False:
            return False

    relateType = message["relateType"]
    if relateType == 10:  # newsId
        news = mongo.article.news.find_one({"_id": ObjectId(message["relateId"])})
        if news is None:
            return False
        if news.get("type") != 61000 and news.get("processStatus") != 1:
            # 61000 xiniudata edit news
            return False
        # if len(companies) > 0:
        #     flag = False
        #     for company in companies:
        #         if company["id"] in news["companyIds"]:
        #             flag = True
        #             break
        #     if flag is False:
        #         return False
    elif relateType == 20 or relateType == 30:  # artifactId
        artifact = conn.get("select * from artifact where id=%s", int(message["relateId"]))
        if artifact is None or artifact["active"] == 'N':
            return False
        if artifact["companyId"] is None:
            return False
        c = process_util.get_company(artifact["companyId"], _conn=conn)
        if c is None:
            return False
        if c["active"] is not None and c["active"] != 'Y':
            return False
    elif relateType == 40:  # jobIds
        # 无相应主题
        pass
    elif relateType == 50:  # gongshangId
        # 无相应主题
        pass
    elif relateType == 60:  # companyIds
        # 无相应主题
        pass
    elif relateType == 70:  # fundingId
        funding = conn.get("select * from funding where id=%s", int(message["relateId"]))
        if funding is None or funding["active"] == 'N':
            return False
        corporate_id = funding["corporateId"]
        if corporate_id is None:
            return False
        c = conn.get("select * from company where corporateId=%s and (active is null or active='Y') limit 1", corporate_id)
        if c is None:
            return False
    return True


def process(topic_message_id):
    try:
        process_tab(topic_message_id)
        process_one_message(topic_message_id)
    except Exception, e:
        logger.exception(e)
        traceback.print_exc()
        

def process_tab(topic_message_id):
    logger.info("process_tab topic_message_id: %s", topic_message_id)
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    message = conn.get("select * from topic_message where id=%s", topic_message_id)
    if message is not None:
        items = conn.query("select * from topic_tab_message_rel where topicMessageId=%s", topic_message_id)
        if len(items) == 0:
            # 补充 topic_tab_message_rel
            # conn.execute("delete from topic_tab_message_rel where topicMessageId=%s", topic_message_id)
            topic_tabs = conn.query("select * from topic_tab where topicId=%s", message["topicId"])
            for tab in topic_tabs:
                if tab["subType"] == 1100: #所有新闻
                    conn.insert("insert topic_tab_message_rel(topicTabId,topicMessageId,createTime) "
                                "values(%s,%s,now())",
                                tab["id"], topic_message_id)
                elif tab["subType"] == 1101: #投资人观点
                    relate_type = message["relateType"]
                    if relate_type == 10: # newsId
                        news_id = message["relateId"]
                        news = mongo.article.news.find_one({"_id": ObjectId(news_id)})
                        if news is not None:
                            if news["features"] is not None and 578351 in news["features"]:
                                conn.insert("insert topic_tab_message_rel(topicTabId,topicMessageId,createTime) "
                                            "values(%s,%s,now())",
                                            tab["id"], topic_message_id)
                else:
                    pass
        conn.update("update topic_message set tabStatus=1 where id=%s", topic_message_id)
    mongo.close()
    conn.close()


def process_one_message(topic_message_id):
    logger.info("process_message topic_message_id: %s", topic_message_id)
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    message = conn.get("select * from topic_message where id=%s", topic_message_id)

    flag = message_valid_check(message, mongo, conn)
    if flag is False:
        logger.info("delete message: %s, relateType: %s, relateId: %s", topic_message_id,
                    message["relateType"],
                    message["relateId"])
        # 删除消息
        delete_invalid(message, conn, mongo)
    elif flag == 'A':
        conn.update("update topic_message set active='P',modifyTime=now(), modifyUser=1078"
                    " where id=%s", topic_message_id)
        mongo.message.user_message.delete_many({"topicMessageId": topic_message_id})
    else:
        if message is not None and message["active"] == 'Y':
            # topic_message_sector_rel
            patch_sector(message)

            # 推送给用户

            topic = conn.get("select * from topic where id=%s", message["topicId"])
            subscriptions = conn.query("select * from user_topic_subscription where (active is null or active='Y') and "
                                       "topicId=%s", topic["id"])
            # test_users = process_util.get_test_users()
            # for userId in test_users:
            #     subscriptions.append({"userId": userId})

            for subscription in subscriptions:
                user_id = int(subscription["userId"])
                send = True
                if topic["sectorRelevant"] == "Y":
                    send = has_sector(topic_message_id, user_id)

                if send is True:
                    valid = True
                    if topic["onlyForInvestor"] == "Y":
                        user = conn.get("select * from user where id=%s", user_id)
                        if user is None or user["verifiedInvestor"] != 'Y':
                            valid = False

                    if valid is True:
                        flag = process_util.insert_user_message(user_id, message["publishTime"] + datetime.timedelta(hours=-8),
                                                                topic_message_id=topic_message_id, _mongo=mongo)
                        if flag:
                            # 只推送10分钟之内的消息
                            n = datetime.datetime.now() + datetime.timedelta(minutes=-10)
                            if n < message["publishTime"]:
                                # process_util.send_iOS_message(user_id, message, "topic", _conn=conn)
                                # process_message.send_message(user_id, "topic")
                                process_util.send_iOS_content_available(user_id, "topic", _conn=conn)

            conn.update("update topic_message set pushStatus=1 where id=%s", topic_message_id)
        elif message is not None and message["active"] == 'P':
            delete_user_message(topic_message_id)
    mongo.close()
    conn.close()


def patch_sector(message):
    sectors = []
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    conn.execute("delete from topic_message_sector_rel where topicMessageId=%s", message["id"])
    relateType = message["relateType"]
    if relateType == 10: # newsId
        news = mongo.article.news.find_one({"_id": ObjectId(message["relateId"])})
        if news is not None and news.has_key("sectors"):
            sectors = news["sectors"]
    elif relateType == 20 or relateType == 30: # artifactId
        artifact = conn.get("select * from artifact where id=%s", message["relateId"])
        if artifact is not None:
            sectors = get_company_sectors(artifact["companyId"])
    elif relateType == 40:  # jobIds
        pass
    elif relateType == 50: # gongshangId
        pass
    elif relateType == 60: # companyIds
        ss = message["relateId"].split(",")
        for s in ss:
            try:
                company_id = int(s)
                _sectors = get_company_sectors(company_id)
                sectors.extend(_sectors)
            except:
                continue
    elif relateType == 70: # fundingId
        funding = conn.get("select * from funding where id=%s", message["relateId"])
        if funding is not None:
            if funding["newsId"] is not None and funding["newsId"] != "":
                news_id = funding["newsId"]
                news = mongo.article.news.find_one({"_id": ObjectId(news_id)})
                if news is not None and news.has_key("sectors"):
                    sectors = news["sectors"]
            if sectors is None or len(sectors) == 0:
                companies = conn.query("select * from company where corporateId=%s", funding["corporateId"])
                for c in companies:
                    _sectors = get_company_sectors(c["id"])
                    sectors.extend(_sectors)

    for s_id in sectors:
        r = conn.get("select * from topic_message_sector_rel where topicMessageId=%s and sectorId=%s",
                     message["id"], s_id)
        if r is None:
            conn.insert("insert topic_message_sector_rel(topicMessageId,sectorId) values(%s,%s)",
                    message["id"], s_id)
    conn.update("update topic_message set sectorStatus=1 where id=%s", message["id"])
    mongo.close()
    conn.close()


def get_company_sectors(company_id):
    conn = db.connect_torndb_proxy()
    _sectors = conn.query(" select s.* from company_tag_rel r join sector s on r.tagId=s.tagId"
                         " where (r.active is null or r.active='Y') and "
                         " (s.active is null or s.active='Y') and r.companyId=%s",
                         company_id)
    conn.close()
    sectors = []
    for s in _sectors:
        sectors.append(s["id"])
    return sectors


def has_sector(topic_message_id, user_id):
    conn = db.connect_torndb_proxy()
    user_sectors = conn.query("select sectorId from user_sector where "
                              "(active is null or active='Y') and userId=%s", user_id)
    message_sectors = conn.query("select sectorId from topic_message_sector_rel where "
                                 "topicMessageId=%s", topic_message_id)
    conn.close()
    for u in user_sectors:
        for m in message_sectors:
            if u["sectorId"] == m["sectorId"]:
                return True

    return False


def delete(topic_message_id):
    conn = db.connect_torndb_proxy()
    conn.execute("delete from topic_tab_message_rel where topicMessageId=%s", topic_message_id)
    conn.close()
    # Java端处理topic_company
    delete_user_message(topic_message_id)


def delete_invalid(message, conn, mongo):
    rel = conn.get("select * from topic_tab_message_rel where topicMessageId=%s and (active is null or active='Y') limit 1",
                   message["id"])
    if rel is not None:
        conn.update("update topic_tab_message_rel set active='N',modifyTime=now(), modifyUser=1078"
                    " where topicMessageId=%s", message["id"])

    m = conn.get("select * from topic_message where id=%s and (active is null or active='Y')",
                 message["id"])
    if m is not None:
        conn.update("update topic_message set active='N',modifyTime=now(), modifyUser=1078"
                    " where id=%s", message["id"])

    rel = conn.get("select * from topic_message_company_rel where topicMessageId=%s and (active is null or active='Y') limit 1",
                   message["id"])
    if rel is not None:
        conn.update("update topic_message_company_rel set active='N',modifyTime=now(), modifyUser=1078"
                    " where topicMessageId=%s", message["id"])

    # 删除 topic_company
    rels = conn.query("select * from topic_message_company_rel where topicMessageId=%s", message["id"])
    for rel in rels:
        topic_company_id = rel["topicCompanyId"]
        topic_company = conn.get("select * from topic_company where id=%s", topic_company_id)
        if topic_company is None or topic_company["active"] != 'Y':
            continue
        _rel = conn.get("select * from topic_message_company_rel where topicCompanyId=%s and (active is null or active='Y') limit 1",
                        topic_company_id)
        if _rel is None:
            logger.info("delete invalid topic_company, topicCompanyId=%s", topic_company_id)
            conn.update("update topic_company set active='P',modifyTime=now(), modifyUser=1078 where id=%s", topic_company_id)
            # exit(0)
    mongo.message.user_message.delete_many({"topicMessageId": message["id"]})


def delete_user_message(topic_message_id):
    mongo = db.connect_mongo()
    mongo.message.user_message.delete_many({"topicMessageId":topic_message_id})
    mongo.close()


def subscribe(user_id, topic_id):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    ms = conn.query("select * from topic_message where topicId=%s and active='Y' order by publishTime desc limit 200", topic_id)
    for m in ms:
        process_util.insert_user_message(user_id, m["publishTime"]+datetime.timedelta(hours=-8), topic_message_id=m["id"], _mongo=mongo)
    mongo.close()
    conn.close()


def unsubscribe(user_id, topic_id):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    ms = conn.query("select * from topic_message where topicId=%s and active='Y'", topic_id)
    for m in ms:
        mongo.message.user_message.delete_many({"topicMessageId": m["id"], "userId": user_id})
    mongo.close()
    conn.close()


def patch():
    conn = db.connect_torndb_proxy()
    items = conn.query("select * from topic_message where topicId=52")
    for item in items:
        process_tab(item["id"])
    conn.close()


if __name__ == '__main__':
    # process_util.insert_user_message(1078, datetime.datetime.now()+datetime.timedelta(hours=-8),topic_message_id=39893)
    # patch()
    pass