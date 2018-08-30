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
import track_company_message

#logger
loghelper.init_logger("process_company_message", stream=True)
logger = loghelper.get_logger("process_company_message")


def process_all():
    # 处理60秒前创建的还未处理的消息
    mid = sys.maxint
    while True:
        conn = db.connect_torndb_proxy()
        ms = conn.query("select * from company_message use index (rds_idx_0) "
                        "where pushStatus=0"
                       " and publishTime < date_sub(now(), interval 3600 SECOND)"
                       " and publishTime > date_sub(now(), interval 1 DAY)"
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
    logger.info("Start delete invalid company message...")
    mid = -1
    while True:
        conn = db.connect_torndb_proxy()
        ms = conn.query("select * from company_message where id>%s order by id limit 1000", mid)
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
                logger.info("delete message: %s, relateType: %s, relateId: %s", mid,
                            m["relateType"],
                            m["relateId"])
                # 删除消息
                delete(mid, _mongo=mongo)
                conn.update("update company_message set active='N', pushStatus=1, modifyUser=1078, modifyTime=now() where id=%s", mid)
            else:
                if m["pushStatus"] == 0:
                    process(mid, _mongo=mongo, _conn=conn)
        mongo.close()
        conn.close()

    logger.info("Delete invalid company message over.")


def publish_check(message, mongo, conn):
    relateType = message["relateType"]

    company = process_util.get_company(message["companyId"], _conn=conn)
    if company["verify"] != 'Y':
        return False

    if relateType == 10:  # newsId
        # 新闻已审核，不用在检查该消息
        return True
    elif relateType == 20 or relateType == 30:  # artifactId
        artifact = conn.get("select * from artifact where id=%s", int(message["relateId"]))
        if artifact is not None and artifact["verify"] == 'Y':
            return True
    elif relateType == 40:  # jobIds
        flag = True
        ss = message["relateId"].split(",")
        for job_id in ss:
            job = mongo.job.job.find_one({"_id": ObjectId(job_id)})
            if job is not None:
                recruit_company_id = job["recruit_company_id"]
                r = conn.get("select * from company_recruitment_rel where companyId=%s and jobCompanyId=%s",
                             company["id"], recruit_company_id)
                if r is None or r["verify"] != 'Y':
                    flag = False
                    break
            else:
                flag = False
                break
        if flag is True:
            return flag
        # 使用时需说明数据来源仅限于拉钩
        # 由于目前只有拉钩，不能准确判断是否有招聘，所以需要人工确认
        # return False
    elif relateType == 50:  # gongshangId
        # gs = mongo.info.gongshang.find_one({"_id": ObjectId(message["relateId"])})
        # alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s and verify='Y'",
        #                  company["corporateId"], gs["name"])
        # if alias is not None:
        #     return True
        #工商变更需要人工修改消息
        return False
    elif relateType == 60:  # companyIds
        # ss = message["relateId"].split(",")
        # for s in ss:
        #     try:
        #         comps_company_id = int(s)
        #         comps = conn.get("select * from company where id=%s", comps_company_id)
        #         if comps["verify"] != 'Y':
        #             return False
        #         rel = conn.get("select * from companies_rel where companyId=%s and company2Id=%s and"
        #                        " (active is null or active='Y') limit 1", message["companyId"], comps_company_id)
        #         if rel is None:
        #             return False
        #     except:
        #         return False
        # return True
        # 竞品需要人工审核
        return False
    elif relateType == 70:  # fundingId
        funding = conn.get("select * from funding where id=%s", int(message["relateId"]))
        if funding is not None and funding["verify"] == 'Y':
            return True
    elif relateType == 80: # companyFaId
        companyFaId = message["relateId"]
        if companyFaId is not None:
            company_fa = conn.get("select * from company_fa where id=%s", int(companyFaId))
            if company_fa is not None and company_fa["active"] != 'N':
                #logger.info("message for relateType 80 could auto publish, messageId: %s", message["id"])
                return True   # Test
                pass
        else:
            #logger.info("message for relateType 80 could auto publish, messageId: %s", message["id"])
            return True   # Test
            pass

    return False


def message_valid_check(message, mongo, conn):
    c = conn.get("select * from company where id=%s", message["companyId"])
    if c["active"] == "Y" or c["active"] == "A" or c["active"] is None:
        pass
    else:
        return False

    relateType = message["relateType"]
    company = process_util.get_company(message["companyId"], _conn=conn)
    if relateType == 10:  # newsId
        news = mongo.article.news.find_one({"_id": ObjectId(message["relateId"])})
        if news is None:
            return False
        if message["companyId"] not in news["companyIds"]:
            return False
        if news.get("type") != 61000 and news.get("processStatus") != 1:
            # 61000 xiniudata edit news
            return False
    elif relateType == 20 or relateType == 30:  # artifactId
        artifact = conn.get("select * from artifact where id=%s", int(message["relateId"]))
        if artifact is None or artifact["active"] == 'N':
            return False
        if artifact["companyId"] != message["companyId"]:
            return False
    elif relateType == 40:  # jobIds
        ss = message["relateId"].split(",")
        for job_id in ss:
            job = mongo.job.job.find_one({"_id": ObjectId(job_id)})
            if job is not None:
                recruit_company_id = job["recruit_company_id"]
                r = conn.get("select * from company_recruitment_rel where companyId=%s and jobCompanyId=%s and "
                             "(active is null or active='Y') limit 1",
                             message["companyId"], recruit_company_id)
                if r is None or r["active"] == 'N':
                    logger.info(message)
                    # exit()
                    return False
            else:
                logger.info(message)
                # exit()
                return False
    elif relateType == 50:  # gongshangId
        if message["detailId"] is None:
            return False
        gs = mongo.info.gongshang.find_one({"_id": ObjectId(message["relateId"])})
        alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s and"
                         " (active is null or active='Y') limit 1",
                         company["corporateId"], gs["name"])
        if alias is None or alias["active"] == 'N':
            return False
    elif relateType == 60:  # companyIds
        flag = False
        left = []
        ss = message["relateId"].split(",")
        for s in ss:
            try:
                comps_company_id = int(s)
                comps = conn.get("select * from company where id=%s", comps_company_id)
                if comps["active"] != 'Y' and comps["active"] is not None:
                    flag = True
                    continue
                rel = conn.get("select * from companies_rel where companyId=%s and company2Id=%s and"
                               " (active is null or active='Y') limit 1", message["companyId"], comps_company_id)
                if rel is None:
                    flag = True
                    continue

                left.append(comps_company_id)
            except:
                flag = True
                continue

        if flag is True:
            logger.info(message)
            logger.info(left)
            if len(left) == 0:
                return False
            else:
                s = "%s发现了%s个潜在的竞争对手" % (company["name"], len(left))
                relateId = ",".join([str(t) for t in left])
                conn.update("update company_message set message=%s, relateId=%s where id=%s",
                            s, relateId, message["id"])
    elif relateType == 70:  # fundingId
        funding = conn.get("select * from funding where id=%s", int(message["relateId"]))
        if funding is None or funding["active"] == 'N':
            return False
    elif relateType == 80: # companyFaId
        companyFaId = message["relateId"]
        if companyFaId is not None:
            company_fa = conn.get("select * from company_fa where id=%s", int(companyFaId))
            if company_fa is None or company_fa["active"] == 'N':
                logger.info("invalid message for relateType 80, messageId: %s", message["id"])
                return False
    return True


def process(company_message_id, _mongo=None, _conn=None):
    try:
        _process(company_message_id, _mongo=None, _conn=None)
    except Exception, e:
        logger.exception(e)
        traceback.print_exc()

def _process(company_message_id, _mongo=None, _conn=None):
    if _conn is None:
        conn = db.connect_torndb_proxy()
    else:
        conn = _conn

    message = conn.get("select * from company_message where id=%s", company_message_id)
    if message is None or message["relateType"] == 60:
        if _conn is None:
            conn.close()
        return

    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo

    flag = message_valid_check(message, mongo, conn)
    if flag is False:
        logger.info("should delete message: %s, relateType: %s, relateId: %s", company_message_id, message["relateType"],
                    message["relateId"])
        # 删除消息
        # delete(company_message_id, _mongo=mongo)
        # conn.update("update company_message set active='N', pushStatus=1 where id=%s", company_message_id)
    else:
        process_util.audit_company_from_company_message(message["companyId"], message["trackDimension"],
                                                        message["id"], message["relateType"], message["createTime"],
                                                        _mongo=mongo, _conn=conn)
        # if message["relateType"] == 60:
        #     process_util.audit_companies(message["relateId"], message["trackDimension"], message["id"],
        #                                  message["relateType"], message["createTime"], _mongo=mongo, _conn=conn)

        if message["active"] == 'P':
            flag = publish_check(message, mongo, conn)
            if flag:
                message["active"] = 'Y'
                publish_time = message["publishTime"]
                #7天内publishTime更新为现在，7天外的不变
                # if publish_time + datetime.timedelta(days=7) > datetime.datetime.now():
                #     publish_time = datetime.datetime.now()
                #     message["publishTime"] = publish_time
                conn.update("update company_message set active='Y',modifyTime=now(), publishTime=%s where id=%s",
                            publish_time, company_message_id)

        if message["active"] == 'Y':
            logger.info("publish company_message_id: %s", company_message_id)
            # 推送给用户
            if message["relateType"] == 80:
                subscriptions = []
                test_users = process_util.get_test_users()
                for userId in test_users:
                    subscriptions.append({"userId":userId})
            else:
                subscriptions = conn.query("select * from user_company_subscription where (active is null or active='Y') and "
                                       "companyId=%s", message["companyId"])

            for subscription in subscriptions:
                user_id = int(subscription["userId"])
                flag = process_util.insert_user_message(user_id,
                                                        message["publishTime"] + datetime.timedelta(hours=-8),
                                                        company_message_id=company_message_id, _mongo=mongo)
                if flag:
                    n = datetime.datetime.now() + datetime.timedelta(minutes=-10)
                    if n < message["publishTime"]:
                        # process_util.send_iOS_message(user_id, message, "company", _conn=conn)
                        # process_message.send_message(user_id, "company")
                        process_util.send_iOS_content_available(user_id, "company", _conn=conn)

            # 推送给user_message2
            track_company_message.process(conn, mongo, company_message_id)

            conn.update("update company_message set pushStatus=1 where id=%s", company_message_id)

            # if message["relateType"] == 80:
            #     exit(0)  # Test
        else:
            # logger.info("delete company_message_id: %s", company_message_id)
            # TODO 重复删除
            # delete(company_message_id, _mongo=mongo)
            pass

    if _mongo is None:
        mongo.close()
    if _conn is None:
        conn.close()


def delete(company_message_id, _mongo=None):
    if _mongo is None:
        mongo = db.connect_mongo()
    else:
        mongo = _mongo

    mongo.message.user_message.delete_many({"companyMessageId":company_message_id})
    # 折叠消息的删除
    items = mongo.message.user_message.find({"otherMessages.companyMessageId": company_message_id})
    for item in items:
        new_otherMessages = []
        otherMessages = item["otherMessages"]
        for m in otherMessages:
            if m["companyMessageId"] != company_message_id:
                new_otherMessages.append(m)
        mongo.message.user_message.update_one({"_id": item["_id"]}, {"$set":{"otherMessages": new_otherMessages}})

    # 从user_message2中删除
    track_company_message.delete(mongo, company_message_id)

    if _mongo is None:
        mongo.close()


def subscribe(user_id, company_id):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    ms = conn.query("select * from company_message where companyId=%s and active='Y' "
                    "and publishTime>date_sub(now(),interval 30 day) "
                    "order by publishTime desc "
                    , company_id)
    for m in ms:
        process_util.insert_user_message(user_id, m["publishTime"] + datetime.timedelta(hours=-8),
                                         company_message_id=m["id"], _mongo=mongo)
    mongo.close()
    conn.close()


def unsubscribe(user_id, company_id):
    conn = db.connect_torndb_proxy()
    mongo = db.connect_mongo()
    ms = conn.query("select * from company_message where companyId=%s and active='Y'", company_id)
    for m in ms:
        mongo.message.user_message.delete_many({"companyMessageId": m["id"], "userId": user_id})
    mongo.close()
    conn.close()


if __name__ == '__main__':
    process_all()