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
import image_helper
import oss2_helper
#logger
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

oss2put = oss2_helper.Oss2Helper()

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

def process(corporate_id):
    logger.info("corporate id: %s", corporate_id)
    conn = db.connect_torndb()
    funding = conn.get("select * from funding where corporateId=%s and (active is null or active !='N') order by fundingDate desc limit 1",
                       corporate_id)
    if funding is not None:
        # corporate = conn.get("select * from corporate where id=%s", corporate_id)
        # if corporate is not None:
            conn.update("update corporate set round=%s where id=%s",
                        funding["round"],corporate_id)
    else:
        pass
    conn.close()

def find_corporates(full_name):
    corporate_ids = []

    if full_name is None or full_name == "":
        return corporate_ids

    full_name = name_helper.company_name_normalize(full_name.strip())

    conn = db.connect_torndb()
    corporate_aliases = conn.query("select a.* from corporate_alias a join corporate c on c.id=a.corporateId where "
                                   "(c.active is null or c.active !='N') and (a.active is null or a.active !='N') "
                                   "and a.name=%s",
                                   full_name)
    for ca in corporate_aliases:
        company = conn.get("select * from company where corporateId=%s and (active is null or active!='N') limit 1",
                           ca["corporateId"])
        if company is not None:
            logger.info("find_corporate_by_full_name %s: %s", full_name, ca["corporateId"])
            if ca["corporateId"] not in corporate_ids:
                corporate_ids.append(int(ca["corporateId"]))
    conn.close()

    return corporate_ids

def insert_stock_exchange(stockSource):
    conn = db.connect_torndb()
    if source_map.has_key(int(stockSource)) is False:
        return None
    sxname = source_map[int(stockSource)].split("|")[0]
    website = source_map[int(stockSource)].split("|")[1]
    stock_exchange = conn.get("select * from stock_exchange where name=%s limit 1", sxname)
    if stock_exchange is None:
        sql = "insert stock_exchange(name,website,createTime,modifyTime) values(%s,%s,now(),now())"
        stock_exchange_id = conn.insert(sql, sxname, website)
    else:
        stock_exchange_id = stock_exchange["id"]
    conn.close()
    return stock_exchange_id


def insert_cop_st_rel(corporateId,sourceId,stockExchangeId,status,listingDate,applyDate,delistDate,stockWeb,industry):
    conn = db.connect_torndb()
    cop_st_rel = conn.get("select * from corporate_stock_exchange_rel where corporateId=%s and "
                          "stockExchangeId=%s limit 1", corporateId, stockExchangeId)
    logger.info("stock: %s, %s, %s", stockExchangeId,sourceId,listingDate)
    if cop_st_rel is None:
        sql = "insert corporate_stock_exchange_rel(corporateId,stockExchangeId,status,createTime,modifyTime," \
              "applyDate,listDate,delistDate,stockSymbol,stockExchangeUrl,csrc_great_code_desc) " \
              "values(%s,%s,%s,now(),now(),%s,%s,%s,%s,%s,%s)"
        cop_st_rel_id = conn.insert(sql, corporateId, stockExchangeId,status,applyDate,
                                    listingDate,delistDate,str(sourceId),stockWeb,industry)
    else:
        cop_st_rel_id = cop_st_rel["id"]
        sql = "update corporate_stock_exchange_rel set status=%s,modifyTime=now(),applyDate=%s," \
              "listDate=%s,delistDate=%s,stockExchangeUrl=%s,csrc_great_code_desc=%s where id=%s"
        # conn.update(sql, status,applyDate,listingDate,delistDate,stockWeb,industry,cop_st_rel_id)
    conn.close()
    return cop_st_rel_id

def update_ipoStatus(corporateId,seid):
    # conn = db.connect_torndb()
    # istatus = 70030
    # ilocationid = 340
    # conn.update("update corporate set ipoStatus=%s, stockExchangeId=%s where id=%s", istatus, seid, corporateId)
    # conn.close()
    pass


def insert_funding(corporateId,sourceId,stockExchangeId,listingDate,source):
    conn = db.connect_torndb()
    round = round_map[source]
    #todo
    fundingSource = None
    logger.info("%s update funding :%s", corporateId, listingDate)
    companies = conn.query("select * from company where (active is null or active!='N') and corporateId=%s",corporateId)
    if len(companies) > 0:
        companyId = companies[0]["id"]
        # for company in companies:
        funding = conn.get("select * from funding where corporateId=%s and round=%s and "
                           "(active is null or active!='N') limit 1", corporateId,round)
        if funding is None:
            sql = "insert funding(round,fundingDate,createTime,modifyTime,corporateId,companyId,source," \
                  "publishDate,stockExchangeId,stockSymbol) values(%s,%s,now(),now(),%s,%s,%s,%s,%s,%s)"
            funding_id = conn.insert(sql, round,listingDate,corporateId,companyId,fundingSource,
                                     listingDate,stockExchangeId,str(sourceId))
        else:
            funding_id = funding["id"]
            if listingDate is not None:
                # sql = "update funding set fundingDate=%s,publishDate=%s,stockExchangeId=%s," \
                #       "stockSymbol=%s where id=%s"
                # conn.update(sql, listingDate,listingDate,stockExchangeId,str(sourceId),funding_id)
                sql = "update funding set stockExchangeId=%s," \
                      "stockSymbol=%s where id=%s"
                conn.update(sql, stockExchangeId, str(sourceId), funding_id)
            else:
                sql = "update funding set stockExchangeId=%s," \
                      "stockSymbol=%s where id=%s"
                conn.update(sql, stockExchangeId, str(sourceId), funding_id)
    conn.close()

def get_logo_stock(stockname, code, source):
    name = None
    height = None
    width = None
    if stockname is not None and code is not None:
        logger.info("prepare logo: %s|%s", stockname, code)
        # (image_value, width, height) = download_crawler.get_image_size(logo_url)
        im,image = image_helper.gen_stock_image(stockname, code)
        name = str(source)+"-"+code
        logger.info("%s|%s", name,image)

        headers = {"Content-Type": "image/jpeg"}
        oss2put.put(name, image.getvalue(), headers=headers)
    return (name, width, height)


def patch_logo(corporateId,source,sourceId,stockname):

    conn = db.connect_torndb()
    companies = conn.query("select * from company where corporateId=%s",corporateId)
    for company in companies:
        companyId = company["id"]
        if company["logo"] is None:
            sc = conn.get("select * from source_company where source=%s and sourceId=%s and companyId=%s",
                          source, sourceId, companyId)
            if sc is None or sc["name"] is None:
                continue
            logger.info("patch logo for %s|%s", stockname, companyId)
            logoName,h,w = get_logo_stock(sc["name"],str(sourceId),source)
            if logoName is not None:
                conn.update("update company set logo=%s where id=%s",logoName,companyId)
            # exit()
    conn.close()


def aggregate(stockSource,sourceId,name,status,stockWeb,industry,listingDate=None,applyDate=None,delistDate=None):
    logger.info("try to map: %s|%s|%s", name,sourceId,stockSource)

    corporateIds = find_corporates(name)
    flag = False
    if len(corporateIds) == 0:
        #missing stock
        logger.info("*******missing stock\n\n\n")
        # exit()
    else:
        logger.info("find: %s",corporateIds)
        # return
        # insert to stock_exchane
        stockExchangeId = insert_stock_exchange(stockSource)
        if stockExchangeId is None:
            logger.info("missing stock exchange id")
            exit()

        for corporateId in corporateIds:
            patch_logo(corporateId,stockSource,sourceId,name)
            # update_ipoStatus(corporateId,stockExchangeId)
            #insert corporate_stock_exchange_rel
            corporateStockExchangeRelId = insert_cop_st_rel(corporateId,sourceId,stockExchangeId,
                                                            status,listingDate,applyDate,delistDate,
                                                            stockWeb,industry)

            #insert_funding
            fundingId = insert_funding(corporateId,sourceId,stockExchangeId,listingDate,stockSource)
            process(corporateId)
            flag = True
    return flag


if __name__ == '__main__':
    logger.info("Begin...")
    noo = 0
    while True:
        no = 0
        mongo = db.connect_mongo()
        collection = mongo.stock.neeq
        collection_sse = mongo.stock.sse
        collection_szse = mongo.stock.szse
        while True:
            # items = list(collection.find({"sourceId":870397}).limit(100))
            items = list(collection.find({"processStatus": 2},
                                         {"name":1,"sourceId":1,"stockwebsite":1,"baseinfo":1,"listingDate":1}))
            for item in items:
                f = aggregate(13400,item["sourceId"],item["name"],70030,item["stockwebsite"],
                          item["baseinfo"].get("industry",None),listingDate=item["listingDate"])
                # pass
                if f is True:
                    collection.update({"_id": item["_id"]}, {"$set": {"processStatus": 3}})
                else:
                    no += 1
            break
            # if len(items) == 0:
            #     break

        while True:
            # items = list(collection_sse.find({"sourceId":603997}).limit(100))
            items = list(collection_sse.find({"processStatus": 2},
                                             {"name": 1, "sourceId": 1, "stockwebsite": 1,
                                              "baseinfo": 1, "listingDate": 1}))
            for item in items:
                listingDate = item["listingDate"]
                if isinstance(listingDate, list) or str(listingDate) == "":
                    listingDate = None
                f = aggregate(13401, item["sourceId"], item["name"], 70030, item["stockwebsite"],
                              item["baseinfo"].get("CSRC_GREAT_CODE_DESC", None), listingDate=listingDate)
                # pass
                if f is True:
                    collection_sse.update({"_id": item["_id"]}, {"$set": {"processStatus": 3}})
                else:
                    no += 1
            break
            # if len(items) == 0:
            #     break

        while True:
            # items = list(collection_sse.find({"sourceId":603997}).limit(100))
            items = list(collection_szse.find({"processStatus": 2},
                                             {"name": 1, "sourceId_str": 1, "stockwebsite": 1,
                                              "baseinfo": 1, "listingDate": 1}))
            for item in items:
                listingDate = item["listingDate"]
                if isinstance(listingDate, list) or str(listingDate) == "":
                    listingDate = None
                f = aggregate(13402, item["sourceId_str"], item["name"], 70030, item["stockwebsite"],
                              None, listingDate=listingDate)
                # pass
                if f is True:
                    collection_szse.update({"_id": item["_id"]}, {"$set": {"processStatus": 3}})
                else:
                    no += 1
            break
            # if len(items) == 0:
            #     break
        # break
        if noo == no:
            logger.info("same before")
        else:
            noo = no
        mongo.close()
        time.sleep(10*60)

