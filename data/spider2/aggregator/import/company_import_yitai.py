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
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../corporate'))
import loghelper, db, config, util,url_helper,name_helper
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


def insert(shortname, name,brief,website):
    name = name.replace("（开业）","")
    sourceId = util.md5str(name)
    sid = parser_db_util.save_company_yitai(shortname, name,13100,sourceId,brief)
    logger.info("sid:%s->sourceId:%s",sid, sourceId)
    parser_db_util.save_source_company_name(sid, name, 12010)
    parser_db_util.save_source_company_name(sid, shortname, 12020)
    # if website is not None and website.strip() != "":
    #     website = url_helper.url_normalize(website)
    #     if website is not None and website != "":
    #         if website.find("http://") == -1 and website.find("https://"):
    #             website = "http://" + website
    #         type, market, app_id = url_helper.get_market(website)
    #         if type == 4010:
    #             if website.find('sse.com') > 0:
    #                 pass
    #             else:
    #                 artifact = {
    #                     "sourceCompanyId": sid,
    #                     "name": shortname,
    #                     "description": None,
    #                     "link": website,
    #                     "domain": app_id,
    #                     "type": type
    #                 }
    #
    #                 parser_db_util.save_artifacts_standard(sid, [artifact])


def findc(aname):
    rvalue = 0
    conn = db.connect_torndb()
    aname = aname.replace("（开业）","")
    sourceId = util.md5str(aname)
    sc = conn.get("select * from source_company where source=13100 and sourceId=%s", sourceId)
    if sc is None:
        logger.info("wrong")
        exit()
    companyId = sc["companyId"]
    company =  conn.get("select * from company where id=%s", companyId)
    scs = conn.query("select * from source_company where companyId=%s", companyId)
    # if len(scs) == 1 and scs[0]["source"] == 13096 and company is not None:
    if company is not None and company["active"] in ["A","P","N"]:
        # conn.update("update company set brief=%s,locationId=2 where id=%s", brief, companyId)
        # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])

        # if company["active"] == "A":
            rvalue = 1
            # conn.update("update company set brief=%s,locationId=2 where id=%s", brief,companyId)
            # conn.update("update corporate set brief=%s,locationId=2 where id=%s", brief, company["corporateId"])


    conn.close()
    return rvalue,companyId



if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    fp = open("yitai3.txt")
    fp2 = open("company_sh.txt", "w")
    # conn = db.connect_torndb()
    lines = fp.readlines()
    # lines = []
    cnt = 0
    tot = 0
    pb = 0
    for line in lines:
        # logger.info(line)
        names = [name.strip() for name in line.strip().split("+++")]
        if len(names) != 2:
            logger.info(line)
            exit()
        tot += 1
        shortname = names[0]
        fullName = names[1]
        fullName = name_helper.company_name_normalize(unicode(fullName))
        # if len(brief) < 100:
        #     logger.info(brief)
        # if len(brief) == 0:
        #     brief = None
        #     logger.info("none")
        # if website is not None and website.strip() != "":
        #     logger.info(website)

        # logger.info("name:%s, fullName:%s", shortname, fullName)
        # company_ids = find_company.find_companies_by_full_name_corporate([fullName])
        #
        # if len(company_ids) != 0:
        #     logger.info("found : %s, %s", fullName, company_ids)
        #     cnt += 1
        # insert(shortname,fullName,None,None)
        rv,cid = findc(fullName)
        if rv == 1:
            cnt+=1
            c = conn.get("select * from company where id=%s", cid)
            link = 'http://www.xiniudata.com/validator/#/company/%s/overview' % c["code"]
            # send_message_task(cid, "company_newcover", 13100)
            line = "%s+++%s+++%s+++%s\n" % (c["code"], c["name"], link, c["active"])
            fp2.write(line)

        # if pb>50:
        #     break
        # # break
    conn.close()
    logger.info("%s/%s",cnt, tot)
    logger.info("End.")