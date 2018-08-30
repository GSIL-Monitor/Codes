# -*- coding: utf-8 -*-
import os, sys
import time
import json
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config

#logger
loghelper.init_logger("check_trial_enterprise_will_expire", stream=True)
logger = loghelper.get_logger("check_trial_enterprise_will_expire")

# kafka
kafkaProducer = None

def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

def send_message(task_id):
    if kafkaProducer is None:
        init_kafka()

    #action: create, delete
    msg = {"type":"email", "email_task_id": task_id}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("send_verify_code", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


def check():
    conn = db.connect_torndb()
    # will expire
    # orgs = conn.query("select * from organization where "
    #                   "grade=33010 and trial='Y' and serviceEndDate is not null and "
    #                   "date_sub(serviceEndDate, interval %s day) < now() and serviceEndDate>now()",
    #                   10
    #                   )
    orgs = conn.query("select * from organization where "
                      "serviceType=80002 and serviceStatus='Y' and serviceEndDate is not null and "
                      "date_sub(serviceEndDate, interval %s day) < now() and serviceEndDate>now()",
                      10
                      )
    logger.info("will expire after 10 days")
    for org in orgs:
        #if org["id"] != 51:
        #    continue
        task = conn.get("select * from email_task where type=63070 and orgId=%s limit 1",
                          org["id"])
        if task is None:
            logger.info("org_id: %s, name: %s", org["id"], org["name"])
            task_id = conn.insert("insert email_task(createTime,type,orgId) values(now(),63070,%s)",
                        org["id"])
            send_message(task_id)

    # expired
    logger.info("expired")
    # orgs = conn.query("select * from organization where "
    #                   "grade=33010 and trial='Y' and serviceEndDate is not null and "
    #                   "serviceEndDate<now() and date_add(serviceEndDate, interval %s day)>now()",
    #                   5
    #                   )
    orgs = conn.query("select * from organization where "
                      "serviceType=80002 and serviceStatus='Y' and serviceEndDate is not null and "
                      "serviceEndDate<now() and date_add(serviceEndDate, interval %s day)>now()",
                      5
                      )
    for org in orgs:
        #if org["id"] != 51:
        #    continue
        task = conn.get("select * from email_task where type=63080 and orgId=%s limit 1",
                        org["id"])
        if task is None:
            logger.info("org_id: %s, name: %s", org["id"], org["name"])
            task_id = conn.insert("insert email_task(createTime,type,orgId) values(now(),63080,%s)",
                                  org["id"])
            send_message(task_id)

    conn.close()


if __name__ == "__main__":
    while True:
        try:
            logger.info("Begin check...")
            check()
            logger.info("End check.")
            time.sleep(3600*8)  # 8 hours
        except KeyboardInterrupt:
            exit(0)