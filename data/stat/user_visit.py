# -*- coding: utf-8 -*-
import os, sys
import re
import time, datetime
import json
from bson.objectid import ObjectId
import traceback
from kafka import (KafkaClient, SimpleProducer, KafkaConsumer)

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, config, db

#logger
loghelper.init_logger("visit_stat", stream=True)
logger = loghelper.get_logger("visit_stat")


# kafka
kafkaConsumer = None


def init_kafka():
    global kafkaConsumer, kafkaProducer
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("user_log", group_id="user_visit",
                bootstrap_servers=[url],
                auto_offset_reset='largest',
                enable_auto_commit=True)


def get_code_from_user_log(_id):
    mongo = db.connect_mongo()
    user_log = mongo.log.user_log.find_one({"_id": ObjectId(_id)})
    mongo.close()

    if user_log is not None:
        try:
            code = user_log["jsonRequest"]["payload"]["code"]
            return code
        except:
            pass
    return None


def get_code_from_url(regex, url):
    m = re.match(regex, url)
    if m:
        company_code = m.group(1)
        return company_code
    return None


def process(msg):
    t = msg.get("time")
    if t is None:
        return
    msg_time = datetime.datetime.fromtimestamp(t / 1000)

    user_id = msg.get("userId")
    url = msg.get("requestURL")
    _id = msg.get("_id")

    if url == "/api2/service/x_service/person_ctbb_company/get_by_code":
        company_code = get_code_from_user_log(_id)
        if company_code is not None:
            company_visit_tongji(user_id, company_code, msg_time)
        return

    company_code = get_code_from_url(r'^/company/(.*?)/overview', url)
    if company_code is not None:
        company_visit_tongji(user_id, company_code, msg_time)
        return

    if url == "/api2/service/x_service/person_ctxb_investor/get_by_code":
        investor_code = get_code_from_user_log(_id)
        if investor_code is not None:
            investor_visit_tongji(user_id, investor_code, msg_time)
        return

    investor_code = get_code_from_url(r'^/investor/(.*?)/overview', url)
    if investor_code is not None:
        investor_visit_tongji(user_id, investor_code, msg_time)
        return

def company_visit_tongji(user_id, company_code, msg_time):
    if company_code is not None:
        conn = db.connect_torndb()
        company = conn.get("select id from company where code=%s order by id desc limit 1", company_code)
        if company is not None:
            company_id = company["id"]
            logger.info("companyId: %s", company_id)
            # company_stat
            cs = conn.get("select * from company_stat where companyId=%s limit 1", company_id)
            if cs is None:
                conn.insert("insert company_stat(companyId,visitCnt,likeCnt,commentCnt,createTime,modifyTime) values("
                            "%s,1,0,0,now(),now())", company_id)
            else:
                conn.update("update company_stat set visitCnt=visitCnt+1 where id=%s", cs["id"])

            # user_visit
            if user_id is not None:
                uv = conn.get("select * from user_visit where userId=%s and companyId=%s limit 1", user_id, company_id)
                if uv is None:
                    conn.insert("insert user_visit(userId, companyId, createTime,modifyTime) values(%s, %s, %s, %s)",
                                user_id, company_id, msg_time, msg_time)
        conn.close()


def investor_visit_tongji(user_id, investor_code, msg_time):
    if investor_code is not None:
        conn = db.connect_torndb()
        investor = conn.get("select id from investor where code=%s order by id desc limit 1", investor_code)
        if investor is not None:
            investor_id = investor["id"]
            logger.info("investorId: %s", investor_id)
            # investor_stat
            cs = conn.get("select * from investor_stat where investorId=%s limit 1", investor_id)
            if cs is None:
                conn.insert("insert investor_stat(investorId,visitCnt,likeCnt,commentCnt,createTime,modifyTime) values("
                            "%s,1,0,0,now(),now())", investor_id)
            else:
                conn.update("update investor_stat set visitCnt=visitCnt+1 where id=%s", cs["id"])

            # user_visit
            if user_id is not None:
                uv = conn.get("select * from user_visit where userId=%s and investorId=%s limit 1", user_id, investor_id)
                if uv is None:
                    conn.insert("insert user_visit(userId, investorId, createTime,modifyTime) values(%s, %s, %s, %s)",
                                user_id, investor_id, msg_time, msg_time)
        conn.close()


def main():
    init_kafka()
    while True:
        try:
            logger.info("start")
            for message in kafkaConsumer:
                try:
                    # logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                    #                                           message.offset, message.key,
                    #                                           message.value))
                    kafkaConsumer.commit()
                    try:
                        msg = json.loads(message.value)
                        # logger.info(msg)
                        process(msg)
                    except ValueError, e:
                        traceback.print_exc()
                except Exception, e:
                    traceback.print_exc()
                # exit(0) # Test
        except KeyboardInterrupt:
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()


if __name__ == '__main__':
    main()
