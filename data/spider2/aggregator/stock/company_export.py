# -*- coding: utf-8 -*-
import os, sys,json,time
import datetime
from pymongo import MongoClient
import pymongo
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper, db, config, util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../parser/util'))
import parser_db_util


# kafka
kafkaProducer = None


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
    msg = {"type":"company", "id":company_id , "action":action}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)

def send_message_task(company_id, action, source):
    if kafkaProducer is None:
        init_kafka()

    # action: create, delete
    msg = {"source": action, "id": company_id, "detail": source}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("task_company", json.dumps(msg))
            flag = True
        except Exception, e:
            logger.exception(e)
            time.sleep(60)


#logger
loghelper.init_logger("sh_import", stream=True)
logger = loghelper.get_logger("sh_import")



if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    cnt = 0
    fp2 = open("stock1.txt", "w")
    companies = conn.query("select count(*) as cnt,companyId,id,name,fullName,source,sourceId,active,"
                           "createTime,processStatus,modifyTime from source_company where source in "
                           "(13400,13401,13402) group by companyId having cnt>1")
    for company in companies:
        if company["companyId"] is None: continue
        cnt+=1
        cid = company["companyId"]
        stocks = [sc["name"] for sc in conn.query("select name from source_company where source in (13400,13401,13402) "
                                                  "and companyId=%s", cid)]
        c = conn.get("select * from company where id=%s", cid)
        link = 'http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"]
        line = "%s+++%s+++%s+++%s\n" % (c["code"], c["name"], link, ";".join(stocks))
        fp2.write(line)

        # if pb>50:
        #     break
        # # break
    conn.close()
    logger.info("%s/%s",cnt, len(companies))
    logger.info("End.")