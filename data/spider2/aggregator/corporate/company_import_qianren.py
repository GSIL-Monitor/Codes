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
import find_company

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

tmap = {

}

def insert(name):
    name = name.replace("（开业）","")
    sourceId = util.md5str(name)
    sid = parser_db_util.save_company_fullName(name,13097,sourceId)
    logger.info("sid:%s->sourceId:%s",sid, sourceId)
    parser_db_util.save_source_company_name(sid, name, 12010)


def findc(aname):
    rvalue = 0
    conn = db.connect_torndb()
    aname = aname.replace("（开业）","")
    sourceId = util.md5str(aname)
    sc = conn.get("select * from source_company where source=13097 and sourceId=%s", sourceId)
    if sc is None:
        logger.info("wrong")
        exit()
    companyId = sc["companyId"]
    company =  conn.get("select * from company where id=%s", companyId)
    scs = conn.query("select * from source_company where companyId=%s", companyId)
    # if len(scs) == 1 and scs[0]["source"] == 13096 and company is not None:
    if company is not None:
        # conn.update("update company set brief=%s,locationId=2 where id=%s", brief, companyId)
        # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])

        # if company["active"] == "A":
            rvalue = 1
            # conn.update("update company set brief=%s,locationId=2 where id=%s", brief,companyId)
            # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])
    # if tmap.has_key(tag) is None:
    #     logger.info("wrong tag")
    #     exit()
    # addtag(aname,companyId,tmap[tag])
    conn.close()
    return rvalue,companyId

def addtag(bname,companyId,tagId):
    logger.info("%s-%s-%s",bname,companyId,tagId)
    conn = db.connect_torndb()
    sql = "insert company_tag_rel(companyId,tagId,verify,active,createTime) values(%s,%s,%s,%s,now())"
    tag1 = conn.get("select * from company_tag_rel where companyId=%s and tagId=%s limit 1", companyId, 592646)
    if tag1 is None:
        conn.insert(sql, companyId, 592646, 'Y','Y')
    tag2 = conn.get("select * from company_tag_rel where companyId=%s and tagId=%s limit 1", companyId, tagId)
    if tag2 is None:
        conn.insert(sql, companyId, tagId, 'Y', 'Y')
    conn.close()

if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    fp = open("qianren.txt")
    fp2 = open("company_qianren.txt", "w")
    # conn = db.connect_torndb()
    lines = fp.readlines()
    # lines = []
    cnt = 0
    tot = 0
    pb = 0
    for line in lines:
        #logger.info(line)
        names = [name.strip() for name in line.strip().split("+++")]
        if len(names) != 1:
            logger.info(line)
            exit()
        tot += 1
        fullName = names[0]
        # brief = names[1]
        # tag = names[3]
        # company_ids = find_company.find_companies_by_full_name_corporate([fullName])
        #
        # if len(company_ids) != 0:
        #     logger.info("found : %s, %s", fullName, company_ids)
        #     cnt += 1
        # insert(fullName)
        rv,cid = findc(fullName)
        if rv == 1:
            cnt+=1
            c = conn.get("select * from company where id=%s", cid)
            link = 'http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"]
            send_message_task(cid, "company_newcover", 13097)
            send_message(cid,"create")
            line = "%s+++%s+++%s+++%s\n" % (c["code"], c["name"], link, c["active"])
            fp2.write(line)

        # if pb>50:
        #     break
        # break
    conn.close()
    logger.info("%s/%s",cnt, tot)
    logger.info("End.")