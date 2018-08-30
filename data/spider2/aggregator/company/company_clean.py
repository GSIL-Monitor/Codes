# -*- coding: utf-8 -*-
import os, sys, datetime
import time
import json
from kafka import (KafkaClient, SimpleProducer)
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db,config
import name_helper, hz, desc_helper

#logger
loghelper.init_logger("Company_data_clean", stream=True)
logger = loghelper.get_logger("Company_data_clean")

# kafka
kafkaProducer = None

def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)


def send_message(company_id, action):
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


if __name__ == "__main__":
    init_kafka()
    conn = db.connect_torndb()
    mongo = db.connect_mongo()
    # collection_raw = mongo.raw.projectdata
    collection = mongo.task.company_refresh
    # #step1 clean description
    # desc = []
    # source_companies = list(conn.query("select id, description, companyId from source_company where (active is null or active='Y') order by id desc"))
    # for company in source_companies:
    #     if company["description"] is None or company["description"].strip() == "":
    #         continue
    #     flag = desc_helper.check_desc(company["description"])
    #     if flag is False:
    #         logger.info("Wrong desc for source_company: %s", company["id"])
    #         if company["companyId"] is None:
    #             pass
    #         else:
    #             id1 = conn.get( "select id,description from source_company where companyId=%s and id!=%s and (active is null or active='Y') limit 1",
    #                 company["companyId"], company["id"])
    #             if id1 is not None:
    #                 logger.info("%s has other company %s->%s", company["id"], id1["id"], id1["description"])
    #                 conn.update("update source_company set processStatus=1 where id=%s", id1["id"])
    #
    #         conn.update("update source_company set active='N' where id=%s", company["id"])
    #         desc.append(str(company["id"]))
    #
    # logger.info("********************%d source_companies has been cleaned",len(desc))
    #
    # #step2 clean company by checking source_company status
    # num = 0
    # companies = list(conn.query("select id from company where (active is null or active='Y') order by id desc"))
    # for company in companies:
    #     company_id = company["id"]
    #     sc = list(conn.query("select * from source_company where (active is null or active='Y') and companyId=%s", company_id))
    #     if len(sc) == 0:
    #         deal = conn.get("select * from deal where status>19000 and companyId=%s limit 1", company_id)
    #         if deal is None:
    #             num += 1
    #             conn.update("update company set active='N',modifyTime=now(),modifyUser=139 where id=%s", company_id)
    #             send_message(company_id, "delete")
    #             logger.info("company: %s was deactive ", company_id)
    #         else:
    #             logger.info("******************************DEAL for %s", company_id)
    # logger.info("********************%d companies has been cleaned", num)


    #step 3 check description from lagou
    # num = 0; num1 =0;  num2 =0; num3 =0; num4 =0; num5 =0
    # tgs = conn.query("select * from tag where type=11100 and (active is null or active='Y')")
    # tags = [int(tg["id"]) for tg in tgs]
    # companies = list(conn.query("select * from company where (active is null or active='Y') order by id desc"))
    # cids = []
    # for company in companies:
    #     num2+=1
    #     company_id = company["id"]
    #     # if len(conn.query("select * from funding where (active is null or active='Y') and companyId=%s", company_id)) ==0:continue
    #     # num1+=1
    #     if company["description"] is not None and company["description"].strip() !="":
    #         continue
    #     if company["productDesc"] is not None or company["operationDesc"] is not None or company["teamDesc"] is not None or company["modelDesc"] is not None:
    #         continue
    #     num1+=1
    #     # scs = list(conn.query("select * from source_company where (active is null or active='Y') and companyId=%s and source=13050", company_id))
    #     # if len(scs) > 0:
    #     #     num3+=1
    #     #     for sc in scs:
    #     #         if sc["description"] is not None and company["description"] is not None and sc["description"] == company["description"]:
    #     #             num5+=1
    #     #             if company["round"] is not None and company["round"] >0:
    #     #                 logger.info("Round! Same description for company:%s|%s with source: %s", company["id"],
    #     #                             company["code"], sc["id"])
    #     #                 cids.append(str(company_id))
    #     #                 num+=1
    #     #             else:
    #     #                 company_tags = conn.query("select * from company_tag_rel where (active is null or active='Y') and companyId=%s", company_id)
    #     #                 for ct in company_tags:
    #     #                     if ct["tagId"] is not None and ct["tagId"] in tags:
    #     #                         logger.info("Tags! Same description for company:%s|%s with source: %s", company["id"],
    #     #                                     company["code"], sc["id"])
    #     #                         num4+=1;cids.append(str(company_id));break
    #     #             break
    #     company_tags = conn.query("select * from company_tag_rel where (active is null or active='Y') and companyId=%s",company_id)
    #     for ct in company_tags:
    #         if ct["tagId"] is not None and ct["tagId"] in tags:
    #             logger.info("Tags! Missing description for company:%s|%s", company["id"],company["code"])
    #             num4+=1;cids.append(str(company_id));break
    #
    # logger.info("num:%s/%s/%s/%s/%s/%s",num,num4, num5,num3, num1, num2)
    #
    # logger.info(cids)
    cids = []
    ccids = []
    a=0;b=0;c=0;d=0;e=0
    # nonames = conn.query("select * from company where (active is null or active='Y')")
    # for noname in nonames:
    items = list(collection.find({"extendType": 22}))
    for item in items:
        noname = conn.get("select * from company where id=%s", item["companyId"])

        corporate = conn.get("select * from corporate where id =%s", noname["corporateId"])
        c += 1
        if noname["description"] is None or noname["description"].strip() == "":
            fundings = conn.query("select * from funding where corporateId=%s and (active is null or active='Y')",
                                       noname["corporateId"])
            # logger.info("here")
            if noname["createUser"] is None and noname["modifyUser"] is None and corporate["modifyUser"] is None and len(fundings) == 0:
                a += 1

                artifacts = conn.query("select * from artifact where companyId=%s and (active is null or active='Y')",
                                       noname["id"])

                ss = conn.query("select id, source, sourceId from source_company where companyId=%s and "
                                "(active is null or active='Y')", noname["id"])

                if len(artifacts) == 0:
                    d += 1
                    # conn.update("update company set active='P',modifyUser=-576 where id=%s", noname["id"])
                else:
                    e += 1
                    cids.append(noname["id"])
                    if len(cids) % 50 == 0:
                        ccids.append(noname["id"])

        if len(ccids) >= 100:
            break
                # if len(ss) ==0:
                #     b+=1
                #     ss1 = conn.query(
                #         "select id, source, sourceId from source_company where companyId=%s and active ='N'",
                #         noname["id"])
                #
                #     if len(ss1)>0:
                #         c+=1
                #
                # if len(artifacts) == 0 and len(ss) == 0:
                #     e += 1
        logger.info("%s, %s, %s, %s, %s, %s", noname["id"], a, b, c, d, e)

    # n = 0
    # for cid in cids:
    #     if len(ccids) > 100:
    #         break
    #     if n % 50 == 0:
    #         ccids.append(cid)

    logger.info(ccids)
    logger.info(len(ccids))

    # for ccid in ccids:
    #     item = collection.find_one({"extendType":22, "companyId": int(ccid)})
    #     if item is None:
    #         citem = {
    #             "companyId": int(ccid),
    #             "createTime": datetime.datetime.now(),
    #             "createUser": 220,
    #             "extendType": 22, "status": 0,
    #         }
    #
    #         collection.insert_one(citem)
    #     else:
    #         logger.info("here wrong for company: %s", ccid)
    #         exit()
            # else:
        #     if len(ss)==1 and ss[0]["source"] in (13021,13031,13111):
        #         b+=1
        #
        #     else:
        #         c+=1
        #         for s in ss:
        #             logger.info("Source: %s, %s", s["source"],s["sourceId"])
        #     pass
        # else:
        #     b += 1
        #     conn.update("update company set name=%s,modifyTime=now() where id=%s", noname["fullName"], noname["id"])
        #     send_message(noname["id"], "create")
        # c+=1
    logger.info("%s, %s, %s, %s, %s", a, b, c, d, e)

    conn.close()


