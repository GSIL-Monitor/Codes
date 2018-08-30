# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from pymongo import MongoClient
import gridfs
import pymongo
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper
import hz
import name_helper
import simhash
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))

#logger
loghelper.init_logger("parser_mongodb_util", stream=True)
logger = loghelper.get_logger("parser_mongodb_util")

#mongo

source_company_columns = {
    "name":             None,
    "fullName":         None,
    "description":      None,
    "productDesc":      None,
    "modelDesc":        None,
    "operationDesc":    None,
    "teamDesc":         None,
    "marketDesc":       None,
    "compititorDesc":   None,
    "advantageDesc":    None,
    "planDesc":         None,
    "brief":            None,
    "round":            None,
    "roundDesc":        None,
    "companyStatus":    None,
    "fundingType":      None,
    "preMoney":         None,
    "investment":       None,
    "currency":         None,
    "locationId":       None,
    "address":          None,
    "phone":            None,
    "establishDate":    None,
    "logo":             None,
    "type":             41010,
    "source":           None,
    "sourceId":         None,
    "verify":           None,
    "active":           None,
    "createTime":       "now",
    "modifyTime":       "now",
    "field":            None,
    "subField":         None,
    "tags":             None,
    "headCountMin":     None,
    "headCountMax":     None,
    "auditor":          None,
    "auditTime":        None,
    "auditMemo":        None,
    "recommendCompanyIds":  None
}

source_artifact_columns = {
    "name":             None,
    "description":      None,
    "link":             None,
    "domain":           None,
    "type":             None,
    "verify":           None,
    "active":           None,
    "createTime":       "now",
    "modifyTime":       "now",
    "rank":             None,
    "rankDate":         None,
    "extended":         None,
    "expanded":         None,
    "artifactStatus":   None
}

source_company_name_columns = {
    "type":             None,
    "name":             None,
    "verify":           None,
    "chinese":          None,
    "createTime":       "now",
    "modifyTime":       "now",
    "extended":         None,
    "expanded":         None
}

source_funding_columns = {
    "preMoney":         None,
    "postMoney":        None,
    "investment":       None,
    "round":            None,
    "roundDesc":        None,
    "currency":         None,
    "precise":          None,
    "fundingDate":      None,
    "verify":           None,
    "createTime":       "now",
    "modifyTime":       "now",
    "processStatus":    0,
    "_investorIds":     []
}

source_company_member_columns = {
    "_memberId":        None,
    "position":         None,
    "joinDate":         None,
    "leaveDate":        None,
    "type":             None,
    "verify":           None,
    "createTime":       "now",
    "modifyTime":       "now"
}

company_columns = {
    "source_company":           {},
    "source_artifact":          [],
    "source_company_name":      [],
    "source_mainbeianhao":      [],
    "source_funding":           [],
    "source_company_member":    [],
    "source":                   None,
    "sourceId":                 None,
    "processStatus":            None,
    "createTime":               "now",
    "modifyTime":               "now",
    "diff":                     []
}

investor_columns = {
    "name":         None,
    "website":      None,
    "description":  None,
    "logo":         None,
    "stage":        None,
    "field":        None,
    "type":         None,
    "source":       None,
    "sourceId":     None,
    "verify":       None,
    "createTime":   "now",
    "modifyTime":   "now",
    "processStatus":0
}

member_columns = {
    "name":         None,
    "photo":        None,
    "weibo":        None,
    "location":     None,
    "role":         None,
    "description":  None,
    "education":    None,
    "work":         None,
    "source":       None,
    "sourceId":     None,
    "verify":       None,
    "createTime":   "now",
    "modifyTime":   "now",
    "processStatus":0
}

funding_columns = {
    "preMoney":         None,
    "postMoney":        None,
    "investment":       None,
    "round":            None,
    "roundDesc":        None,
    "currency":         None,
    "precise":          None,
    "fundingDate":      None,
    "verify":           None,
    "createTime":       "now",
    "modifyTime":       "now",
    "processStatus":    0,
    "_investorIds":     [],
    "companySourceId":  None
}

recruit_company_columns = {
    "name": None,
    "fullName": None,
    "description": None,
    "brief": None,
    "round": None,
    "roundDesc": None,
    "companyStatus": None,
    'fundingType': None,
    "locationId": None,
    "address": None,
    "phone": None,
    "establishDate": None,
    "logo": None,
    "source": None,
    "sourceId": None,
    "sourceId2": None,
    "sourceUrl": None,
    "field": None,
    "headCountMin": None,
    "headCountMax": None,
    "artifacts": [],
    "members": [],
    "createTime": "now",
    "modifyTime": "now",
}

def populate_column(item, columns):
    item_new = {}
    for column in columns:
        if item.has_key(column) is True:
            item_new[column] = item[column]
        else:
            item_new[column] = columns[column]

        if item_new[column] == "now":
            item_new[column] = datetime.datetime.now()
    return item_new

def save_mongo_company(source, sourceId, cdata):
    mongo = db.connect_mongo()
    collection_company = mongo.source.company

    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        collection_company.delete_one({"source": source, "sourceId": sourceId})

    scitem = populate_column(cdata, source_company_columns)

    cdata = {}
    cdata["source_company"] = scitem
    cdata["source"] = source
    cdata["sourceId"] = sourceId
    item = populate_column(cdata, company_columns)

    collection_company.insert(item)
    #TODO add back funding data for itjuzi
    mongo.close()

def update_processStatus(source, sourceId, value):
    mongo = db.connect_mongo()
    collection_company = mongo.source.company
    collection_company.update_one({"source": source, "sourceId": sourceId},{"$set":{"processStatus": value}})
    mongo.close()

def save_mongo_source_artifact(source, sourceId, sadata):
    mongo = db.connect_mongo()
    collection_company = mongo.source.company

    item = populate_column(sadata, source_artifact_columns)

    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        source_artifact = collection_company.find_one({"source": source, "sourceId": sourceId,
                                               "source_artifact": {"$elemMatch": {"type": item["type"], "link": item["link"], "domain": item["domain"]}}})
        if source_artifact is None:
            collection_company.update_one({"_id": record["_id"]}, {'$addToSet': {"source_artifact": item}})

    mongo.close()

def save_mongo_source_company_name(source, sourceId, scndata):
    mongo = db.connect_mongo()
    collection_company = mongo.source.company

    item = populate_column(scndata, source_company_name_columns)
    chinese = hz.is_chinese_string(item["name"])
    if chinese:
        item["chinese"] = 'Y'
    else:
        item["chinese"] = 'N'
    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        #logger.info(record)
        source_company_name = collection_company.find_one({"source": source, "sourceId": sourceId, "source_company_name.name": item["name"]})
        if source_company_name is None:
            collection_company.update_one({"_id": record["_id"]}, {'$addToSet': {"source_company_name": item}})

    mongo.close()

def save_mongo_source_funding(source, sourceId, sfdata):
    mongo = db.connect_mongo()
    collection_company = mongo.source.company

    item = populate_column(sfdata, source_funding_columns)

    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        source_company_funding = collection_company.find_one({"source": source, "sourceId": sourceId,
                                                   "source_funding": {"$elemMatch": {"investment": item["investment"], "currency": item["currency"],
                                                                                     "round": item["round"], "fundingDate": item["fundingDate"]}}})
        if source_company_funding is None:
            collection_company.update_one({"_id": record["_id"]}, {'$addToSet': {"source_funding": item}})

    mongo.close()

def save_mongo_source_company_member(source, sourceId, scmdata):
    mongo = db.connect_mongo()
    collection_company = mongo.source.company

    item  = populate_column(scmdata, source_company_member_columns)

    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        # logger.info(record)
        source_company_member = collection_company.find_one({"source": source, "sourceId": sourceId,
                                                   "source_company_member": {"$elemMatch": {"position": item["position"], "type": item["type"],
                                                                                            "_memberId": item["_memberId"]}}})
        if source_company_member is None:
            collection_company.update_one({"_id": record["_id"]}, {'$addToSet': {"source_company_member": item}})

    mongo.close()

def save_mongo_investor(source, sourceId, idata):
    mongo = db.connect_mongo()
    collection_investor = mongo.source.investor

    item = populate_column(idata, investor_columns)
    record = collection_investor.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        id = record["_id"]
        #Check diff
        for column in ["name","website","description","type"]:
            if item[column] != record[column]:
                item["createTime"] = record["createTime"]
                collection_investor.update_one({"_id": id}, {'$set': item})
                #update diff
                # companys = list(collection_company.find({"source_funding._investorIds": {"$all": [id]}}))
                # for company in companys:
                #     collection_company.update_one({"_id": company["_id"]}, {'$addToSet': {"diff": {"source_funding": "update"}}})
                break
    else:
        id = collection_investor.insert(item)

    mongo.close()
    return id

def save_mongo_member(source, sourceId, mdata):
    mongo = db.connect_mongo()
    collection_member = mongo.source.member

    item = populate_column(mdata, member_columns)
    record = collection_member.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        id = record["_id"]
        #Check diff
        for column in ["name","weibo","education","work","description"]:
            if item[column] != record[column]:
                logger.info("Member info diff for %s, %s<->%s", column, item[column], record[column])
                item["createTime"] = record["createTime"]
                collection_member.update_one({"_id": id}, {'$set': item})
                # update diff
                # companys = list(collection_company.find({"source_company_member._memberId": {"$all": [id]}}))
                # for company in companys:
                #     collection_company.update_one({"_id": company["_id"]}, {'$addToSet': {"diff": {"source_company_member": "update"}}})
                break
        logger.info("Member info no diff")
    else:
        id = collection_member.insert(item)

    mongo.close()
    return id

def save_mongo_funding(source, sourceId, fdata):
    mongo = db.connect_mongo()
    collection_funding = mongo.source.funding
    item = populate_column(fdata, funding_columns)
    record = collection_funding.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        id = record["_id"]
        item["createTime"] = record["createTime"]
        collection_funding.update_one({"_id": id}, {'$set': item})
    else:
        id = collection_funding.insert(item)

    mongo.close()
    return id

def save_mongo_recruit_company(source, sourceId, cdata):
    mongo = db.connect_mongo()
    collection_company = mongo.job.company

    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        # collection_company.delete_one({"source": source, "sourceId": sourceId})
        pass
    else:
        scitem = populate_column(cdata, recruit_company_columns)

        collection_company.insert(scitem)
    mongo.close()

def save_mongo_amac_manager(source, sourceId, cdata):
    mongo = db.connect_mongo()
    collection_company = mongo.amac.manager
    cdata["createTime"] = datetime.datetime.now()
    cdata["modifyTime"] = datetime.datetime.now()
    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        cdata["createTime"] = record["createTime"]
        collection_company.update_one({"_id": record["_id"]},{"$set":cdata})
        # pass
    else:
        collection_company.insert(cdata)
    mongo.close()

def save_mongo_proxy(cdata):
    mongo = db.connect_mongo()
    collection_proxy = mongo.xiniudata.proxy
    cdata["createTime"] = datetime.datetime.now()
    cdata["modifyTime"] = datetime.datetime.now()
    record = collection_proxy.find_one({"ip": cdata["ip"], "port": cdata["port"]})
    logger.info("saving : %s/%s",cdata["ip"],cdata["port"])
    if record is not None:
        logger.info("got before")
        collection_proxy.update_one({"_id": record["_id"]},{"$set":{"modifyTime": cdata["modifyTime"]}})
        if cdata["source"] == "daxiangip.com" and record["source"] == "daxiangip.com":
            if (cdata["type"] == "HTTPS" and record["type"] == "HTTP") or \
                    (cdata["anonymous"] == "high" and record["anonymous"] == "normal"):
                logger.info("here is different record for %s with %s", cdata, record)
                cdata["createTime"] = record["createTime"]
                if record["anonymous"] == "high": cdata["anonymous"] = record["anonymous"]
                if record["type"] == "HTTPS": cdata["type"] = record["type"]
                collection_proxy.update_one({"_id": record["_id"]}, {"$set": cdata})
        # pass
    else:
        collection_proxy.insert(cdata)
    mongo.close()


def save_mongo_amac_fund(source, sourceId, cdata):
    mongo = db.connect_mongo()
    collection_company = mongo.amac.fund
    cdata["createTime"] = datetime.datetime.now()
    cdata["modifyTime"] = datetime.datetime.now()
    record = collection_company.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        cdata["createTime"] = record["createTime"]
        collection_company.update_one({"_id": record["_id"]},{"$set":cdata})
        # pass
    else:
        collection_company.insert(cdata)
    mongo.close()

def save_mongo_blockchain(source, coinName, cdata):
    mongo = db.connect_mongo()
    collection_company = mongo.raw.blockchain
    cdata["createTime"] = datetime.datetime.now()
    cdata["modifyTime"] = datetime.datetime.now()
    record = collection_company.find_one({"source": source, "coinName": coinName})
    if record is not None:
        cdata["createTime"] = record["createTime"]
        collection_company.update_one({"_id": record["_id"]},{"$set":cdata})
        # pass
    else:
        collection_company.insert(cdata)
    mongo.close()

def get_simhash_value(contents):
    main =""
    for content in contents:
        if content["content"].strip() != "":
            main = main + content["content"]
    a = simhash.Simhash(simhash.get_features(main))
    logger.info("*****%s", a.value)
    return str(a.value)


def save_mongo_news(newsdata):
    mongo = db.connect_mongo()
    collection_news = mongo.article.news
    newsdata["imgChecked"] = True
    value = get_simhash_value(newsdata.get("contents",[]))
    newsdata["simhashValue"] = value
    nid = collection_news.insert(newsdata)
    mongo.close()
    return nid



def find_mongo_memberId(source, sourceId):
    mongo = db.connect_mongo()
    collection_member = mongo.source.member

    record = collection_member.find_one({"source": source, "sourceId": sourceId})
    if record is not None:
        id = record["id"]
    else:
        id = None

    mongo.close()
    return id

def find_android_market(app_market, app_id):
    mongo = db.connect_mongo()
    collection_android_market = mongo.market.android_market
    item = collection_android_market.find_one({"appmarket": app_market, "key_int": app_id})
    mongo.close()
    return item

def find_process_limit(SOURCE, TYPE, start, limit):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    items = list(collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}).skip(start).limit(limit))
    mongo.close()
    return items
    #return list(collection.find({"source": SOURCE, "type": TYPE, "key_int": 84172}))

def find_all_limit(SOURCE, TYPE, start, limit):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    items = list(collection.find({"source":SOURCE, "type":TYPE}).skip(start).limit(limit))
    mongo.close()
    return items

def find_process_one(SOURCE, TYPE, key_int):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    item = collection.find_one({"source": SOURCE, "type": TYPE, "key_int": key_int})
    mongo.close()
    return item

def find_process(SOURCE, TYPE):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    items = list(collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}))
    mongo.close()
    return items
    #return list(collection.find({"source":SOURCE, "type":TYPE, "key_int":1701}).sort("key_int", pymongo.ASCENDING))

def find_process_limit_lagou(SOURCE, TYPE, start, limit):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    items = list(collection.find({"source": SOURCE, "type": TYPE, "processed_lagou": {"$ne": True}}).skip(start).limit(limit))
    mongo.close()
    return items

def update_processed(_id):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    collection.update_one({"_id":_id},{"$set":{"processed":True}})
    mongo.close()

def update_processed_lagou(_id):
    mongo = db.connect_mongo()
    collection = mongo.raw.projectdata
    collection.update_one({"_id":_id},{"$set":{"processed_lagou":True}})
    mongo.close()

def get_location(location):
    conn = db.connect_torndb()
    result = conn.get("select * from location where locationName=%s", location)
    conn.close()
    return result
