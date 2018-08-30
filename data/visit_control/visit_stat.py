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
kafkaProducer = None
kafkaConsumer = None


def init_kafka():
    global kafkaConsumer, kafkaProducer
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("user_log", group_id="visit_stat",
                bootstrap_servers=[url],
                auto_offset_reset='smallest',
                enable_auto_commit=True)
    kafka = KafkaClient(url)
    kafkaProducer = SimpleProducer(kafka)


def stat_download(visit_control_id, userId, btoken, msg):
    # 由于不能知道下载是否成功，在这里统计是不合适的。应该有下载程序直接统计
    return

    # TODO test
    json_request = msg["jsonRequest"]
    start = json_request["start"]
    end = json_request["end"]
    cnt = start - end

    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    mongo = db.connect_mongo()
    if userId is not None:
        item = mongo.xiniudata.visit_stat.find_one(
            {"userId": userId, "visitControlId": visit_control_id, "date": today})
        if item is None:
            mongo.xiniudata.visit_stat.insert_one({
                "userId": userId,
                "visitControlId": int(visit_control_id),
                "date": today,
                "cnt": cnt
            })
        else:
            mongo.xiniudata.visit_stat.update_one({"_id": item["_id"]}, {"$inc": {"cnt": cnt}})
    else:
        item = mongo.xiniudata.visit_stat.find_one(
            {"userCookie": btoken, "visitControlId": visit_control_id, "date": today})
        if item is None:
            mongo.xiniudata.visit_stat.insert_one({
                "userCookie": btoken,
                "visitControlId": int(visit_control_id),
                "date": today,
                "cnt": cnt
            })
        else:
            mongo.xiniudata.visit_stat.update_one({"_id": item["_id"]}, {"$inc": {"cnt": cnt}})
    mongo.close()


# db.user_log.ensureIndex({userId:1, requestURL:1, jsonRequestMd5:1, time:1},{background:true})
# db.user_log.ensureIndex({userCookie:1, requestURL:1, jsonRequestMd5:1, time:1},{background:true})
def stat(visit_control_id, userId, btoken, _id, url, json_request_md5):
    now = datetime.datetime.now()
    today = datetime.datetime(year=now.year, month=now.month, day=now.day)
    utc_today = today - datetime.timedelta(hours=8)

    today = now.strftime("%Y-%m-%d")
    mongo = db.connect_mongo()
    if userId is not None:
        item = mongo.log.user_log.find_one({
            "userId": userId,
            "requestURL": url,
            "jsonRequestMd5": json_request_md5,
            "time": {"$gte": utc_today},
            "_id": {"$ne": ObjectId(_id)}
        })
        if item is not None:
            return

        item = mongo.xiniudata.visit_stat.find_one({"userId": userId, "visitControlId": visit_control_id, "date": today})
        if item is None:
            mongo.xiniudata.visit_stat.insert_one({
                "userId": userId,
                "visitControlId": int(visit_control_id),
                "date": today,
                "cnt": 1
            })
        else:
            mongo.xiniudata.visit_stat.update_one({"_id": item["_id"]},{"$inc":{"cnt":1}})
    elif btoken is not None:
        item = mongo.log.user_log.find_one({
            "userCookie": btoken,
            "requestURL": url,
            "jsonRequestMd5": json_request_md5,
            "time": {"$gte": utc_today},
            "_id": {"$ne": ObjectId(_id)}
        })
        if item is not None:
            return

        item = mongo.xiniudata.visit_stat.find_one({"userCookie": btoken, "visitControlId": visit_control_id, "date": today})
        if item is None:
            mongo.xiniudata.visit_stat.insert_one({
                "userCookie": btoken,
                "visitControlId": int(visit_control_id),
                "date": today,
                "cnt": 1
            })
        else:
            mongo.xiniudata.visit_stat.update_one({"_id": item["_id"]},{"$inc":{"cnt":1}})
    mongo.close()


def process(msg):
    t = msg.get("time")
    if t is None:
        return
    d = datetime.datetime.fromtimestamp(t/1000)
    now = datetime.datetime.now()
    if d.year != now.year or d.month != now.month or d.day != now.day:
        return

    userId = msg.get("userId")
    btoken = msg.get("userCookie")
    url = msg.get("requestURL")
    front_path = msg.get("front_path")
    json_request_md5 = msg.get("jsonRequestMd5")
    _id = msg.get("_id")
    code = msg.get("code")

    # /company/lianheyongdao/overview
    m = re.match(r'^/company/(.*?)/overview', url)
    if m:
        company_code = m.group(1)
        msg = {
            "source": "visit_web",
            "id": company_code,
            "posting_time": now.strftime('%Y-%m-%d %H:%M:%S'),
            "from": "visit_stat by arthur"
        }
        if userId is not None:
            msg["detail"] = str(userId)
        else:
            msg["detail"] = "-1"

        logger.info("task_company message, %s", json.dumps(msg))

        flag = False
        while flag is False:
            try:
                kafkaProducer.send_messages("task_company", json.dumps(msg))
                flag = True
            except Exception, e:
                logger.exception(e)
                time.sleep(60)

    if front_path is not None:
        return

    if code != 0:
        return



    # TODO 性能优化
    conn = db.connect_torndb()
    visit_control = conn.get("select c.* from visit_control_url u join visit_control c on u.visitControlId=c.id "
                             "where type=1 and %s REGEXP u.url order by c.sort desc limit 1",
                             url)
    conn.close()
    if visit_control is not None:
        logger.info("userId: %s, btoken: %s, url: %s", userId, btoken, url)
        visit_control_id = visit_control["id"]
        if visit_control_id == 7:
            stat_download(visit_control_id, userId, btoken, msg)
        else:
            stat(visit_control_id, userId, btoken, _id, url, json_request_md5)


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
