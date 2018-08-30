# -*- coding: utf-8 -*-
import os, sys
import time
import datetime
from kafka import (KafkaClient, SimpleProducer)
import json
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import loghelper
import db
import name_helper
import config
#logger
#二级市场检查是否有多家公司，然后公司是否检验过
loghelper.init_logger("stock_aggregate", stream=True)
logger = loghelper.get_logger("stock_aggregate")

source_map = {
    13400: "全国中小企业股份转让系统|http://www.neeq.com.cn",
    13401: "上海证券交易所|http://www.sse.com.cn",
    13402: "深圳证券交易所|http://www.szse.cn"
}
round_map = {
    13400: 1105,
    13401: 1110,
    13402: 1110
}

# kafka
kafkaProducer = None
(n0,n1,n2,n3,n4,n5) = (0,0,0,0,0,0)

fp2 = open("stock1.txt", "w")

def find_corporates(full_name):
    corporate_ids = []

    if full_name is None or full_name == "":
        return corporate_ids

    full_name = name_helper.company_name_normalize(full_name.strip())

    conn = db.connect_torndb()
    corporate_aliases = conn.query("select a.* from corporate_alias a join corporate c on c.id=a.corporateId where "
                                   "(c.active is null or c.active !='N') and (a.active is null or a.active !='N') "
                                   "and a.type=12010 and a.name=%s",
                                   full_name)
    for ca in corporate_aliases:
        company = conn.get("select * from company where corporateId=%s and (active is null or (active!='N' and"
                           " active!='P')) limit 1",
                           ca["corporateId"])
        if company is not None:
            # logger.info("find_corporate_by_full_name %s: %s", full_name, ca["corporateId"])
            if ca["corporateId"] not in corporate_ids:
                corporate_ids.append(int(ca["corporateId"]))
    conn.close()

    return corporate_ids

def count_lagou(corporate_ids):
    a = []
    b = []
    conn = db.connect_torndb()
    for coid in corporate_ids:
        ab = True
        companies = conn.query("select * from company where corporateId=%s and (active is null or (active!='N' "
                           "and active!='P'))",coid)
        if len(companies) > 1:
            ab = False
            a.append(coid)
            continue

        scs = conn.query("select * from source_company where (active is null or active!='N') and "
                         "companyId=%s", companies[0]["id"])
        for sc in scs:
            if sc["source"] not in [13050]:
                ab = False
                break

        if ab is False:
            a.append(coid)
            continue

        b.append(coid)
    conn.close()
    return a, b

def check_source(corporateId):
    source = True
    conn = db.connect_torndb()
    companies = conn.query("select * from company where (active is null or active!='N') and corporateId=%s",
                           corporateId)
    for company in companies:
        scs = conn.query("select * from source_company where (active is null or active!='N') and companyId=%s", company["id"])
        for sc in scs:
            if sc["source"] not in [13400,13401,13402]:
                source = False
                break
        if source is False:
            break
    conn.close()
    return source

def check_ok(corporateId):
    ss = datetime.datetime.strptime("2017-07-01", "%Y-%m-%d")
    status = True
    conn = db.connect_torndb()
    companies = conn.query("select * from company where (active is null or active!='N') and corporateId=%s",
                           corporateId)
    for company in companies:
        if company["modifyUser"] is not None and company["modifyTime"]>=ss and company["verify"] == 'Y':
            pass
        else:
            status = False

    conn.close()
    return status

def merge_company(coid, coids):
    # return
    conn = db.connect_torndb()
    company = conn.get("select * from company where corporateId=%s and (active is null or (active!='N' "
                           "and active!='P')) limit 1", coid)

    if company is not None:

        for coidold in coids:
            if coidold == coid:
                continue
            companyolds = conn.query("select * from company where corporateId=%s", coidold)
            for companyold in companyolds:
                conn.update("update source_company set companyId=%s where companyId=%s and id>0",
                            company["id"], companyold["id"])

                conn.update("update company_recruitment_rel set companyId=%s where companyId=%s and id>0",
                            company["id"], companyold["id"])

                conn.update("update company set active='N' where id=%s", companyold["id"])

    conn.close()

def get_links(cids):
    links = []
    conn = db.connect_torndb()
    for cid in cids:
        companies = conn.query("select * from company where corporateId=%s and (active is null or (active!='N' "
                               "and active!='P'))", cid)
        for c in companies:
            link = 'http://www.xiniudata.com/#/company/%s/overview' % c["code"]
            links.append(link)
    conn.close()
    return ";".join(links)


def aggregate(stockSource,sourceId,name,status,stockWeb,industry,listingDate=None,applyDate=None,delistDate=None):
    global n0
    global n1
    global n2
    global n3
    global n4
    # logger.info("try to map: %s|%s|%s", name,sourceId,stockSource)

    corporateIds = find_corporates(name)
    flag = 0
    if len(corporateIds) == 0:
        #missing stock
        pass
        # logger.info("*******missing stock\n\n\n")
        # exit()
    else:
        if len(corporateIds) > 1:
            # logger.info("%s|%s|%s have 1 more corporates", name,sourceId,stockSource)
            n0 += 1
            a1 = []
            b1 = []
            a1, b1 = count_lagou(corporateIds)
            if len(corporateIds) !=  len(a1) + len(b1):
                logger.info("wwwwrong")
                exit()
            # logger.info("%s - %s, %s", corporateIds, a1, b1)
            logger.info("%s|%s|%s have 1 more corporates", name, sourceId, stockSource)
            n4 += 1
            # if len(corporateIds) == len(b1) or len(corporateIds) == len(b1) + 1:
            #     logger.info("%s - %s, %s", corporateIds, a1, b1)
            #     n4 += 1
            #     if len(corporateIds) == len(b1):
            #         merge_company(corporateIds[0], corporateIds)
            #     else:
            #         merge_company(a1[0],corporateIds)
            #     # exit()
            # else:
            #     line = "%s+++%s+++%s\n" % (name, ";".join([str(id) for id in corporateIds]), get_links(corporateIds))
            #     fp2.write(line)

        else:
            if check_source(corporateIds[0]) is True:
                n1 += 1
            else:
                logger.info("%s|%s|%s|%s have other source", name, sourceId, stockSource, corporateIds[0])
                if check_ok(corporateIds[0]) is True:
                    n2 += 1
                    logger.info("%s|%s|%s|%s have verified", name, sourceId, stockSource, corporateIds[0])
                else:
                    n3 += 1
                    logger.info("%s|%s|%s|%s have not verified", name, sourceId, stockSource, corporateIds[0])

    return flag


if __name__ == '__main__':
    logger.info("Begin...")
    noo = 0
    while True:
        mongo = db.connect_mongo()
        collection = mongo.stock.neeq
        collection_sse = mongo.stock.sse
        collection_szse = mongo.stock.szse
        while True:
            # items = list(collection.find({"sourceId":870397}).limit(100))
            items = list(collection.find({"processStatus": 3},
                                         {"name":1,"sourceId":1,"stockwebsite":1,"baseinfo":1,"listingDate":1}))
            for item in items:
                f = aggregate(13400,item["sourceId"],item["name"],70030,item["stockwebsite"],
                          item["baseinfo"].get("industry",None),listingDate=item["listingDate"])
                # pass

            break
            # if len(items) == 0:
            #     break

        while True:
            # items = list(collection_sse.find({"sourceId":603997}).limit(100))
            items = list(collection_sse.find({"processStatus": 3},
                                             {"name": 1, "sourceId": 1, "stockwebsite": 1,
                                              "baseinfo": 1, "listingDate": 1}))
            for item in items:
                listingDate = item["listingDate"]
                if isinstance(listingDate, list) or str(listingDate) == "":
                    listingDate = None
                f = aggregate(13401, item["sourceId"], item["name"], 70030, item["stockwebsite"],
                              item["baseinfo"].get("CSRC_GREAT_CODE_DESC", None), listingDate=listingDate)
                # pass

            break
            # if len(items) == 0:
            #     break

        while True:
            # items = list(collection_sse.find({"sourceId":603997}).limit(100))
            items = list(collection_szse.find({"processStatus": 3},
                                             {"name": 1, "sourceId_str": 1, "stockwebsite": 1,
                                              "baseinfo": 1, "listingDate": 1}))
            for item in items:
                listingDate = item["listingDate"]
                if isinstance(listingDate, list) or str(listingDate) == "":
                    listingDate = None
                f = aggregate(13402, item["sourceId_str"], item["name"], 70030, item["stockwebsite"],
                              None, listingDate=listingDate)
                # pass

            break
            # if len(items) == 0:
            #     break
        logger.info("%s/%s/%s/%s/%s", n0, n1, n2, n3, n4)
        mongo.close()
        time.sleep(10*60)

