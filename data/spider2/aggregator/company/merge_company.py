# -*- coding: utf-8 -*-
import os, sys
import time
import json
from kafka import (KafkaClient, SimpleProducer)
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import config, db

#logger
loghelper.init_logger("merge_company", stream=True)
logger = loghelper.get_logger("merge_company")

#mongo
mongo = db.connect_mongo()
collection_news = mongo.article.news

# kafka
kafkaProducer = None

def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

init_kafka()

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


def choose(companyId1, companyId2):
    #选择哪个合并哪个
    conn = db.connect_torndb()
    company1 = conn.get("select * from company where id=%s", companyId1)
    company2 = conn.get("select * from company where id=%s", companyId2)
    sourceCompany1s = conn.query("select * from source_company where companyId=%s and (active is null or active='Y')", companyId1)
    sourceCompany2s = conn.query("select * from source_company where companyId=%s and (active is null or active='Y')", companyId2)
    deals1 = conn.query("select * from deal where companyId=%s order by status", companyId1)
    deals2 = conn.query("select * from deal where companyId=%s order by status", companyId2)
    conn.close()

    # if company1["verify"]=='Y' and company2["verify"]!='Y':
    #     return companyId1, companyId2
    # if company1["verify"]!='Y' and company2["verify"]=='Y':
    #     return companyId2, companyId1

    if len(sourceCompany1s) > 0 and len(sourceCompany2s) == 0:
        return companyId1, companyId2
    if len(sourceCompany2s) > 0 and len(sourceCompany1s) == 0:
        return companyId2, companyId1

    if len(deals1)==0 and len(deals2)==0:
        pass
    elif len(deals1)>0 and len(deals2)==0:
        return companyId1, companyId2
    elif len(deals1)==0 and len(deals2)>0:
        return companyId2, companyId1
    else:
        deal1 = deals1[0]
        deal2 = deals2[0]
        if deal1.status == deal2.status:
            pass
        elif deal1.status > deal2.status:
            return companyId1, companyId2
        else:
            return companyId2, companyId1

    if companyId1 < companyId2:
        return companyId1, companyId2
    else:
        return companyId2, companyId1


def merge_company(companyId1, companyId2):
    logger.info("begin merge_company: %s <-> %s", companyId1, companyId2)
    companyId1, companyId2 = choose(companyId1, companyId2)
    logger.info("choose merge_company: %s <-> %s", companyId1, companyId2)
    #companyId1是要留下来的
    conn = db.connect_torndb()
    company1 = conn.get("select * from company where id=%s", companyId1)
    company2 = conn.get("select * from company where id=%s", companyId2)
    conn.close()

    #-----company有关表合并-----
    #1. document
    conn = db.connect_torndb()
    docs = conn.query("select * from document where companyId=%s", companyId2)
    for doc in docs:
        doc1 = conn.get("select * from document where companyId=%s and name=%s", companyId1, company1["name"])
        if doc1 is None:
            conn.update("update document set companyId=%s where id=%s", companyId1, doc["id"])
    conn.close()

    #2. company_candidate
    conn = db.connect_torndb()
    cs = conn.query("select * from company_candidate where companyId=%s", companyId2)
    for c in cs:
        c1 = conn.get("select * from company_candidate where sourceCompanyId=%s and companyId=%s",c["sourceCompanyId"],companyId1)
        if c1 is None:
            conn.update("update company_candidate set companyId=%s where id=%s", companyId1, c["id"])
    conn.close()

    #3. coldcall_company_rel
    conn = db.connect_torndb()
    cs = conn.query("select * from coldcall_company_rel where companyId=%s", companyId2)
    for c in cs:
        conn.update("update coldcall_company_rel set companyId=%s where id=%s", companyId1, c["id"])
    conn.close()

    #4. demoday_company
    conn = db.connect_torndb()
    cs = conn.query("select * from demoday_company where companyId=%s", companyId2)
    for c in cs:
        conn.update("update demoday_company set companyId=%s where id=%s", companyId1, c["id"])
    conn.close()

    #5. collection_company_rel
    conn = db.connect_torndb()
    cs = conn.query("select * from collection_company_rel where companyId=%s", companyId2)
    for c in cs:
        c1 = conn.get("select * from collection_company_rel where companyId=%s and collectionId=%s", companyId1, c["collectionId"])
        if c1 is None:
            conn.update("update collection_company_rel set companyId=%s where id=%s", companyId1, c["id"])
    conn.close()

    #6. mylist_company_rel
    conn = db.connect_torndb()
    cs = conn.query("select * from mylist_company_rel where companyId=%s", companyId2)
    for c in cs:
        c1 = conn.get("select * from mylist_company_rel where companyId=%s and mylistId=%s", companyId1, c["mylistId"])
        if c1 is None:
            conn.update("update mylist_company_rel set companyId=%s where id=%s", companyId1, c["id"])
    conn.close()

    #7. job
    conn = db.connect_torndb()
    cs = conn.query("select * from job where companyId=%s", companyId2)
    for c in cs:
        c1 = conn.get("select * from job where companyId=%s and position=%s  and startDate=%s and locationId=%s limit 1", companyId1, c["position"], c["startDate"],c["locationId"])
        if c1 is None:
            conn.update("update job set companyId=%s where id=%s", companyId1, c["id"])
    conn.close()

    #8. news
    cs = list(collection_news.find({"companyId":companyId2}))
    for c in cs:
        item = collection_news.find_one({"companyId":companyId1, "title":c["title"]})
        if item is None:
            collection_news.update_one({"_id":c["_id"]},{"$set":{"companyId":companyId1}})

    #9. push_pool
    conn = db.connect_torndb()
    cs = conn.query("select * from push_pool where companyId=%s", companyId2)
    for c in cs:
        c1 = conn.get("select * from push_pool where companyId=%s", companyId1)
        if c1 is None:
            conn.update("update push_pool set companyId=%s where companyId=%s", companyId1, companyId2)
    conn.close()

    #10. company_fa
    conn = db.connect_torndb()
    docs = conn.query("select * from company_fa where companyId=%s", companyId2)
    for doc in docs:
        conn.update("update company_fa set companyId=%s where id=%s", companyId1, doc["id"])
    conn.update("update company_fa_candidate set companyId=%s where companyId=%s", companyId1, companyId2)
    conn.close()

    #-----deal有关表合并-----
    conn = db.connect_torndb()
    deals = conn.query("select * from deal where companyId=%s", companyId2)
    for deal in deals:
        d1 = conn.get("select * from deal where companyId=%s and organizationId=%s", companyId1, deal["organizationId"])
        if d1 is None:
            conn.update("update deal set companyId=%s where id=%s", companyId1, deal["id"])
        else:
            #两个company都有deal, 留stage靠后的
            if deal["status"] > d1["status"]:
                logger.info("keep companyId2's deal: %s - %s", companyId2, deal["id"])
                conn.update("update deal set companyId=140446 where id=%s", d1["id"])
                conn.update("update deal set companyId=%s where id=%s", companyId1, deal["id"])
                conn.update("update deal set companyId=%s where id=%s", companyId2, d1["id"])   #对调
            else:
                logger.info("keep companyId1's deal: %s - %s", companyId1, d1["id"])
    conn.close()


    #
    conn = db.connect_torndb()
    cmrs = conn.query("select * from company_member_rel where companyId=%s", companyId2)
    memberIds = []
    for cmr in cmrs:
        memberIds.append(cmr["memberId"])
    conn.execute("delete from company_member_rel where companyId=%s", companyId2)
    for memberId in memberIds:
        cmrs = conn.query("select * from company_member_rel where memberId=%s", memberId)
        if len(cmrs) == 0:
            conn.update("update source_member set memberId=null where memberId=%s", memberId)
            conn.execute("delete from member where id=%s", memberId)

    conn.update("update company set active='N',modifyTime=now(),modifyUser=139 where id=%s", companyId2)

    #add funding for check
    scompanies = conn.query("select * from source_company where (active is null or active='Y') and companyId=%s", company_id2)
    conn.update("update source_company set companyId=%s,processStatus=1 where companyId=%s", companyId1, companyId2)
    for sc in scompanies:
        conn.update("update source_funding set processStatus=0 where sourceCompanyId=%s",sc["id"])

    conn.close()

    send_message(companyId1, "create")
    send_message(companyId2, "delete")

    return companyId1

def get_copmpany_id(code):
    conn = db.connect_torndb()
    company = conn.get("select * from company where code=%s and (active is null or active='Y')",code)
    conn.close()
    if company is None:
        return None
    return company["id"]

def get_copmpany_code(company_id):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s and (active is null or active='Y')",company_id)
    conn.close()
    if company is None:
        return None
    return company["code"]

if __name__ == "__main__":
    if len(sys.argv) > 2:
        code1 = sys.argv[1]
        code2 = sys.argv[2]
        conn = db.connect_torndb()
        company1 = conn.get("select * from company where code=%s and (active is null or active='Y')",code1)
        company2 = conn.get("select * from company where code=%s and (active is null or active='Y')",code2)
        conn.close()
        if company1 is None:
            logger.info("company %s not exist!",code1)
            exit()

        if company2 is None:
            logger.info("company %s not exist!",code2)
            exit()

        merge_company(company1["id"], company2["id"])
    else:
        # logger.info("python merge_company <companyId1> <companyId1>")
        while True:
            conn = db.connect_torndb()
            ts = conn.query("select * from audit_reaggregate_company where type=1 and processStatus=1")
            for t in ts:
                logger.info("%s: %s", t["id"], t["beforeProcess"])
                beforeProcess = t["beforeProcess"]
                codes = beforeProcess.split(" ")
                if len(codes) <= 1:
                    conn.update("update audit_reaggregate_company set processStatus=2 where id=%s",
                                t["id"])
                    continue
                code1 = codes.pop(0)
                company_id1 = get_copmpany_id(code1)
                if company_id1 is None:
                    conn.update("update audit_reaggregate_company set processStatus=2 where id=%s",
                                t["id"])
                    continue
                while len(codes) >= 1:
                    code2 = codes.pop(0)
                    company_id2 = get_copmpany_id(code2)
                    if company_id2 is None or company_id1 == company_id2:
                        continue
                    company_id1 = merge_company(company_id1, company_id2)
                conn.update("update audit_reaggregate_company set processStatus=2, afterProcess=%s"
                            "where id=%s",
                             get_copmpany_code(company_id1), t["id"])
            conn.close()

            time.sleep(60)

