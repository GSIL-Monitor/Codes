# -*- coding: utf-8 -*-
###
### 公司信息更新，将触发
### 1. topic_tab_company_rel 死亡名单更新
###
import os, sys
import time
import json
import traceback
from kafka import KafkaConsumer

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db, config

#logger
loghelper.init_logger("process_topic_message", stream=True)
logger = loghelper.get_logger("process_topic_message")


# kafka
kafkaConsumer = None

def init_kafka():
    global kafkaConsumer
    (url) = config.get_kafka_config()
    # HashedPartitioner is default
    kafkaConsumer = KafkaConsumer("aggregator_v2", group_id="process_company_update",
                bootstrap_servers=[url],
                auto_offset_reset='smallest')


def process_delete_company(company_id):
    pass


def process_update_company(company_id):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    topic_companies = conn.query("select * from topic_company where companyId=%s", company_id)
    for topic_company in topic_companies:
        topic_tabs = conn.query("select * from topic_tab where topicId=%s", topic_company["topicId"])
        for topic_tab in topic_tabs:
            if topic_tab["subType"] == 1201: #死亡公司
                topic_tab_company_rel = conn.get("select * from topic_tab_company_rel "
                                                 "where topicTabId=%s and topicCompanyId=%s",
                                                 topic_tab["id"], topic_company["id"])
                if company["companyStatus"] in [2020, 2025]:
                    if topic_tab_company_rel is None:
                        conn.insert("insert topic_tab_company_rel(topicTabId,topicCompanyId,createTime) "
                                    "values(%s,%s,now())",
                                    topic_tab["id"], topic_company["id"])
                else:
                    if topic_tab_company_rel is not None:
                        conn.execute("delete from topic_tab_company_rel where id=%s",
                                     topic_tab_company_rel["id"])
    conn.close()


def main():
    init_kafka()
    while True:
        try:
            logger.info("start")
            for message in kafkaConsumer:
                try:
                    logger.info("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                               message.offset, message.key,
                                                               message.value))
                    msg = json.loads(message.value)
                    type = msg["type"]
                    if type == "company":
                        company_id = msg["id"]
                        action = msg["action"]
                        if action == "create":
                            process_update_company(company_id)
                        elif action == "delete":
                            process_delete_company(company_id)
                    kafkaConsumer.commit()
                except Exception, e:
                    traceback.print_exc()
        except KeyboardInterrupt:
            exit(0)
        except Exception, e:
            logger.exception(e)
            traceback.print_exc()
            time.sleep(60)
            init_kafka()


if __name__ == '__main__':
    main()