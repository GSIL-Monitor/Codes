# -*- coding: utf-8 -*-
import os, sys
import time, datetime

from kafka import (KafkaClient, SimpleProducer)

import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import name_helper
import db


sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../score'))
import score_util

#logger
loghelper.init_logger("lagou_score", stream=True)
logger = loghelper.get_logger("lagou_score")

# kafka
kafkaProducer = None

DATE = None

def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

def send_message(company_id, action):
    if kafkaProducer is None:
        init_kafka()

    #action: create, delete
    msg = {"type":"company", "id":company_id , "action":action, "from": "bamy"}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


def send_message_task(company_id, action, source, noupdate):
    if kafkaProducer is None:
        init_kafka()

    #action: create, delete
    msg = {"source":action, "id":company_id , "detail":source, "no_update": noupdate}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("task_company", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)




if __name__ == "__main__":
    conn = db.connect_torndb()
    while True:
        dt = datetime.date.today()
        datestr = datetime.date.strftime(dt, '%Y%m%d')
        logger.info("last date %s", DATE)
        logger.info("now date %s", datestr)

        if dt.weekday() == 6:
            logger.info("today is sunday, recal")
            score_util.get_score_all()
            DATE = datestr

        cnt = 0
        ID = 0
        # lagou part: score and send_message for 20 in 3 hours
        while True:
            # ID = 0
            companies = conn.query("select companyId, score, modifyTime from company_scores where "
                                   "type=37040 order by score desc limit %s,100",ID)
            for company in companies:
                if cnt > 20:
                    break
                company_id = company["companyId"]
                co = conn.get("select * from company where id=%s", company_id)
                # logger.info("company: %s status: %s", co["name"], co["active"])
                if co is not None and (co["active"] == "A" or co["active"] == "P") and company["score"] >= 4:

                    if co["active"] == 'P' and company["modifyTime"] <= co["modifyTime"]:
                        continue
                    logger.info("company from lagou: %s %s %s has score: %s go to pub",
                                co["name"], company_id, co["active"],
                                company["score"])

                    # send_message_task(company_id, "company_newcover", 13050)

                    if co["active"] == "P":
                        conn.update("update company set active='A' where id=%s", company_id)
                        corporate = conn.get("select * from corporate where id=%s", co["corporateId"])
                        if corporate["active"] in ["P"]:
                            conn.update("update corporate set active='A' where id=%s", co["corporateId"])
                    send_message_task(company_id, "company_newcover", 13050, True)
                    cnt += 1
                    # break
            if cnt > 20:
                logger.info("over 20")
                break
            ID += 100
        logger.info("end")
        time.sleep(1000)
