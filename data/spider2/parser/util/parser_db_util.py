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

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util2'))
import parser_mysql_util

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))

#logger
loghelper.init_logger("parser_db_util", stream=True)
logger = loghelper.get_logger("parser_db_util")

#mongo
mongo = db.connect_mongo()
collection = mongo.raw.projectdata

imgfs = gridfs.GridFS(mongo.gridfs)
collection_android_market = mongo.market.android_market

def find_alibaba():  # for test crunchbase_company_parser
    return list(collection.find({"source":13130,'name':'Alibaba'}))

def find_android_market(app_market, app_id):
    return collection_android_market.find_one({"appmarket": app_market, "key_int": app_id})

def find_process_limit(SOURCE, TYPE, start, limit):
    return list(collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}).skip(start).limit(limit))
    #return list(collection.find({"source": SOURCE, "type": TYPE, "key_int": 84172}))

def find_all_limit(SOURCE, TYPE, start, limit):
    return list(collection.find({"source":SOURCE, "type":TYPE}).sort("key_int", pymongo.ASCENDING).skip(start).limit(limit))


def find_process_one(SOURCE, TYPE, key_int):
    return collection.find_one({"source": SOURCE, "type": TYPE, "key_int": key_int})

def find_process_one_key(SOURCE, TYPE, key):
    return collection.find_one({"source": SOURCE, "type": TYPE, "key": key})


def find_process(SOURCE, TYPE):
    return list(collection.find({"source":SOURCE, "type":TYPE, "processed":{"$ne":True}}))
    #return list(collection.find({"source":SOURCE, "type":TYPE, "key_int":1701}).sort("key_int", pymongo.ASCENDING))

def find_36kr(SOURCE,TYPE, key):
    return collection.find_one({"source": SOURCE, "type": TYPE, "key": key})

def update_processed(_id):
    collection.update({"_id":_id},{"$set":{"processed":True}})

def get_location(location):
    conn = db.connect_torndb()
    result = conn.get("select * from location where locationName=%s", location)
    conn.close()
    return result

def get_company(SOURCE,company_key):
    conn = db.connect_torndb()
    result = conn.get("select * from source_company where source=%s and sourceId=%s", SOURCE, str(company_key))
    conn.close()
    return result

def save_company(r, SOURCE, download_crawler):
    company_key = r["sourceId"]
    conn = db.connect_torndb()

    logo_id = None
    source_company = conn.get("select * from source_company where source=%s and sourceId=%s", SOURCE, str(company_key))
    if source_company is None or source_company["logo"] is None or source_company["logo"] == "":
        log_url = r["logo"]
        if log_url is not None and len(log_url.strip()) > 0:
            logger.info(log_url)
            # image_value = download_crawler.get_image(log_url)
            # if image_value is not None:
            #     logo_id = imgfs.put(image_value, content_type='jpeg', filename='company_%s_%s.jpg' % (SOURCE, company_key))
            (logo_id,w,h) = parser_mysql_util.get_logo_id_new(log_url, download_crawler, SOURCE, company_key, "company")
    else:
        logo_id = source_company["logo"]
    logger.info("gridfs logo_id=%s" % logo_id)

    if source_company == None:
        source_company_id = conn.insert("insert source_company(name,fullName,description,brief,\
                    round,roundDesc,companyStatus,fundingType,locationId,establishDate,logo,\
                    source,sourceId,createTime,modifyTime,\
                    field,subField,tags,type,processStatus) \
                    values(%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,%s,%s,\
                    %s,%s,now(),now(),\
                    %s,%s,%s,%s,0)",
                    r["productName"], r["fullName"], r["description"], r["brief"],
                    r["round"],r["roundDesc"],r["companyStatus"],r["fundingType"],r["locationId"],r["establishDate"],logo_id,
                    SOURCE,company_key,
                    r["field"],r["subField"],r["tags"],r["type"]
                    )
    else:
        source_company_id = source_company["id"]
        conn.update("update source_company set \
                    name=%s,fullName=%s,description=%s, brief=%s, \
                    round=%s,roundDesc=%s,companyStatus=%s,fundingType=%s,locationId=%s,establishDate=%s,logo=%s, \
                    field=%s,subField=%s,tags=%s,type=%s, \
                    modifyTime=now(),processStatus=0,active=null \
                    where id=%s",
                    r["productName"], r["fullName"], r["description"], r["brief"],
                    r["round"],r["roundDesc"],r["companyStatus"],r["fundingType"],r["locationId"],r["establishDate"],logo_id,
                    r["field"],r["subField"],r["tags"],r["type"],
                    source_company_id
                    )
    conn.close()

    return source_company_id

def save_artifacts(source_company_id, artifacts):
    conn = db.connect_torndb()
    conn.execute("delete from source_artifact where sourceCompanyId=%s", source_company_id)

    for a in artifacts:
        if a["link"] is not None and a["link"].strip() != "":
            b = conn.get("select * from source_artifact where sourceCompanyId=%s and link=%s and type=%s", source_company_id, a["link"], a["type"])
        elif a["domain"] is not None and a["domain"].strip() != "":
            b = conn.get("select * from source_artifact where sourceCompanyId=%s and domain=%s and type=%s", source_company_id, a["domain"], a["type"])
        else:
            continue
        if b is None:
            sql = "insert source_artifact(sourceCompanyId,`name`,`description`,`link`,`type`, domain,createTime,modifyTime) \
                  values(%s,%s,%s,%s,%s,%s,now(),now())"
            conn.insert(sql, source_company_id,a["name"],a["desc"],a["link"],a["type"],a["domain"])
    conn.close()

def save_footprints(source_company_id, footprints):
    conn = db.connect_torndb()
    for f in footprints:
        fp = conn.get("select * from source_footprint where sourceCompanyId=%s and footDate=%s and description=%s",
                    source_company_id, f["footDate"], f["footDesc"])
        if fp is None:
            conn.insert("insert source_footprint(sourceCompanyId,footDate,description,createTime,modifyTime) \
                        values(%s,%s,%s,now(),now())",
                        source_company_id, f["footDate"], f["footDesc"])
    conn.close()

def save_member_rels(source_company_id, members, SOURCE):
    conn = db.connect_torndb()
    for m in members:
        member_key = m["key"]
        source_member = conn.get("select * from source_member where source=%s and sourceId=%s order by id limit 1",
                                                   SOURCE, member_key)
        if source_member is None:
            continue

        source_member_id = source_member["id"]
        source_company_member_rel = conn.get("select * from source_company_member_rel where \
                sourceCompanyId=%s and sourceMemberId=%s",
                source_company_id, source_member_id)

        type = name_helper.position_check(m["position"])
        logger.info("position %s, type %s", m["position"], type)
        if source_company_member_rel is None:
            conn.insert("insert source_company_member_rel(sourceCompanyId, sourceMemberId, \
                        position,type,createTime,modifyTime) \
                        values(%s,%s,%s,%s, now(),now())",
                        source_company_id, source_member_id,m["position"],type)
    conn.close()

def save_company_score(source_company_id, score):
    conn = db.connect_torndb()
    source_company_score = conn.get("select * from source_company_score where sourceCompanyId=%s", source_company_id)
    if source_company_score is None:
        conn.insert("insert source_company_score(sourceCompanyId, score, createTime) values(%s,%s,now())",
                    source_company_id, score)
    else:
        conn.update("update source_company_score set score=%s, modifyTime=now() where sourceCompanyId=%s",
                    score,source_company_id)
    conn.close()

def save_funding(f,SOURCE):
    flag = True #是否完全处理

    conn = db.connect_torndb()

    #TODO make sure they have same roundStr
    #source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and roundDesc=%s", f["sourceCompanyId"], f["roundStr"])
    source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and round=%s order by fundingDate limit 1", f["sourceCompanyId"], f["fundingRound"])

    if source_funding is None:
        source_funding_id = conn.insert("insert source_funding(sourceCompanyId,investment,round,roundDesc, currency, precise, fundingDate,createTime,modifyTime) \
                                        values(%s,%s,%s,%s,%s,%s,%s,now(),now())",
                                        f["sourceCompanyId"], f["investment"], f["fundingRound"], f["roundStr"],
                                        f["currency"], f["precise"],f["fundingDate"])
    else:
        source_funding_id = source_funding["id"]
        conn.update("update source_funding set investment=%s,currency=%s, precise=%s, fundingDate=%s, modifyTime=now() \
                    where id=%s",
                    f["investment"], f["currency"], f["precise"], f["fundingDate"], source_funding_id
                        )

    for investor in f["investors"]:
        source_investor_id = None
        if investor["key"] is None:
            source_investor = conn.get("select * from source_investor where source=%s and name=%s limit 1",
                                    SOURCE, investor["name"])
            if source_investor is None:
                sql = "insert source_investor(name,website,description,logo,stage,field,type, \
                    source,sourceId,createTime,modifyTime) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
                source_investor_id = conn.insert(sql,
                    investor["name"],None,None,None,None,None,10020,SOURCE,None)
            else:
                source_investor_id = source_investor["id"]
        else:
            source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                                       SOURCE, investor["key"])
            if source_investor is not None:
                source_investor_id = source_investor["id"]

        if source_investor_id is None:
            flag = False
        else:
            source_funding_investor_rel = conn.get("select * from source_funding_investor_rel where \
                    sourceFundingId=%s and sourceInvestorId=%s order by id limit 1",
                    source_funding_id, source_investor_id)
            if source_funding_investor_rel is None:
                conn.insert("insert source_funding_investor_rel(sourceFundingId, investorType, sourceInvestorId, \
                            createTime,modifyTime) \
                            values(%s,%s,%s, now(),now())", source_funding_id, investor["type"], source_investor_id)
    conn.close()

    return flag, source_funding_id

def save_investfirm(r, SOURCE, download_crawler):
    investor_key, investor_name, logo, website, stageStr, fieldsStr, desc = r
    conn = db.connect_torndb()
    source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                                               SOURCE, str(investor_key))
    #logger.info(source_investor["logo"])
    logo_id = None
    if source_investor == None or source_investor["logo"] == None or source_investor["logo"] == "":
        if logo is not None and logo != "":
            # image_value = download_crawler.get_image(logo)
            # if image_value is not None:
            #     logo_id = imgfs.put(image_value, content_type='jpeg', filename='investor_%s_%s.jpg' % (SOURCE, investor_key))
            #     logger.info("gridfs logo_id=%s" % logo_id)
            (logo_id, w, h) = parser_mysql_util.get_logo_id_new(logo, download_crawler, SOURCE, investor_key, "investor")
    else:
        logo_id = source_investor["logo"]

    if source_investor is None:
        sql = "insert source_investor(name,website,description,logo,stage,field,type, \
        source,sourceId,createTime,modifyTime,processStatus) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),0)"
        source_investor_id = conn.insert(sql,
            investor_name,website,desc,logo_id,stageStr,fieldsStr,10020,SOURCE,investor_key)
    else:
        source_investor_id = source_investor["id"]
        sql = "update source_investor set name=%s,website=%s,description=%s,logo=%s,stage=%s,\
        field=%s,type=%s,modifyTime=now(),processStatus=0 where id=%s"
        conn.update(sql,
            investor_name,website,desc,logo_id,stageStr,fieldsStr,10020, source_investor_id)

    conn.close()

def save_member(r, SOURCE, download_crawler):
    member_key, name, weibo, introduction, education, work, location, role, pictureUrl, company_key, position = r
    conn = db.connect_torndb()
    source_member = conn.get("select * from source_member where source=%s and sourceId=%s order by id limit 1",
                                                   SOURCE, member_key)
    logo_id = None
    if source_member == None or source_member["photo"] == None or source_member["photo"] == "":
        if pictureUrl is not None and pictureUrl != "":
            # image_value = download_crawler.get_image(pictureUrl)
            # if image_value is not None:
            #     logo_id = imgfs.put(image_value, content_type='jpeg', filename='member_%s_%s.jpg' % (SOURCE, member_key))
            # logger.info("gridfs logo_id=%s" % logo_id)
            (logo_id, w, h) = parser_mysql_util.get_logo_id_new(pictureUrl, download_crawler, SOURCE, member_key, "member")
    else:
        logo_id = source_member["photo"]

    if source_member is None:
        sql = "insert source_member(name,photo,weibo,location,role,description,\
        education,work,source,sourceId,createTime,modifyTime,processStatus) \
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),0)"
        source_member_id = conn.insert(sql,
            name,logo_id,weibo,location,role,introduction,
            education,work,SOURCE,member_key)
    else:
        source_member_id = source_member["id"]
        sql = "update source_member set name=%s,photo=%s,weibo=%s,location=%s,role=%s,description=%s,\
        education=%s,work=%s,modifyTime=now(),processStatus=0 where id=%s"
        conn.update(sql,
            name,logo_id,weibo,location,role,introduction,
            education,work,source_member_id)

    if company_key is not None:
        source_company = conn.get("select * from source_company where source=%s and sourceId=%s",
                                  SOURCE, company_key)
        if source_company is not None:
            source_company_id = source_company["id"]
            source_company_member_rel = conn.get("select * from source_company_member_rel where \
                    sourceCompanyId=%s and sourceMemberId=%s",
                    source_company_id, source_member_id)
            if source_company_member_rel is None:
                type = name_helper.position_check(position)
                logger.info("position %s, type %s",position,type)
                conn.insert("insert source_company_member_rel(sourceCompanyId, sourceMemberId, \
                            position,type,createTime,modifyTime) \
                            values(%s,%s,%s,%s, now(),now())",
                            source_company_id, source_member_id,position,type)
    conn.close()

##############################################
#                                            #
#       Standard Mysql save process          #
#                                            #
##############################################

def delete_funding(source_company_id):
    conn = db.connect_torndb()
    conn.execute("delete from source_funding_investor_rel where sourceFundingId in (select id from source_funding where sourceCompanyId=%s)", source_company_id)
    conn.execute("delete from source_funding where sourceCompanyId=%s", source_company_id)
    conn.close()

def save_funding_standard(source_funding, download_crawler, investors=None):
    f = source_funding
    conn = db.connect_torndb()
    source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and round=%s order by id limit 1",
                              f["sourceCompanyId"], f["round"])

    investment = f['investment']

    if investment is None or investment == 'None':
        investment = 0

    if source_funding == None:
        source_funding_id = conn.insert("insert source_funding(\
                                sourceCompanyId, investment, round, roundDesc, currency,\
                                precise, fundingDate, newsUrl,createTime, modifyTime) \
                                values(%s,%s,%s,%s,%s,%s,%s,%s,now(),now())",
                                        f["sourceCompanyId"], investment, f["round"], f["roundDesc"], f["currency"],
                                        f["precise"], f["fundingDate"], f.get("newsUrl",None))
    else:
        source_funding_id = source_funding["id"]
        conn.update("update source_funding set investment=%s,currency=%s, precise=%s, fundingDate=%s, modifyTime=now() \
                    where id=%s",
                    investment, f["currency"], f["precise"], f["fundingDate"], source_funding_id
                    )

    if investors is not None:
        if len(investors) != 0:
            for investor in investors:
                if investor.has_key("source_investor_id"):
                    source_investor_id = investor["source_investor_id"]
                else:
                    source_investor_id = save_investor_standard(investor, download_crawler)
                source_funding_investor_rel = conn.get("select * from source_funding_investor_rel where \
                                                 sourceFundingId=%s and sourceInvestorId=%s",
                                                   source_funding_id, source_investor_id)
                if source_funding_investor_rel is None:
                    conn.insert("insert source_funding_investor_rel(sourceFundingId, sourceInvestorId, \
                            createTime,modifyTime) \
                            values(%s,%s, now(),now())",
                            source_funding_id, source_investor_id)

    conn.close()

def save_funding_standard_crunchbase(source_funding, download_crawler, investors=None):
    f = source_funding
    conn = db.connect_torndb()
    if source_funding["fundingDate"] is not None:
        source_funding = conn.get(
            "select * from source_funding where sourceCompanyId=%s and round=%s and fundingDate=%s order by id limit 1",
            f["sourceCompanyId"], f["round"], f["fundingDate"])
    else:
        source_funding = conn.get("select * from source_funding where sourceCompanyId=%s and round=%s order by id limit 1",
                                  f["sourceCompanyId"], f["round"])

    investment = f['investment']

    if investment is None or investment == 'None':
        investment = 0

    if source_funding == None:
        source_funding_id = conn.insert("insert source_funding(\
                                sourceCompanyId, investment, round, roundDesc, currency,\
                                precise, fundingDate, newsUrl,createTime, modifyTime) \
                                values(%s,%s,%s,%s,%s,%s,%s,%s,now(),now())",
                                        f["sourceCompanyId"], investment, f["round"], f["roundDesc"], f["currency"],
                                        f["precise"], f["fundingDate"], f.get("newsUrl",None))
    else:
        source_funding_id = source_funding["id"]
        conn.update("update source_funding set investment=%s,currency=%s, precise=%s, fundingDate=%s, modifyTime=now() \
                    where id=%s",
                    investment, f["currency"], f["precise"], f["fundingDate"], source_funding_id
                    )

    if investors is not None:
        if len(investors) != 0:
            for investor in investors:
                if investor.has_key("source_investor_id"):
                    source_investor_id = investor["source_investor_id"]
                else:
                    source_investor_id = save_investor_standard(investor, download_crawler)
                source_funding_investor_rel = conn.get("select * from source_funding_investor_rel where \
                                                 sourceFundingId=%s and sourceInvestorId=%s",
                                                   source_funding_id, source_investor_id)
                if source_funding_investor_rel is None:
                    conn.insert("insert source_funding_investor_rel(sourceFundingId, sourceInvestorId, \
                            createTime,modifyTime) \
                            values(%s,%s, now(),now())",
                            source_funding_id, source_investor_id)

    conn.close()

def save_investor_standard(source_investor, download_crawler):
    s = source_investor
    source = s["source"]
    sourceId = s["sourceId"]
    logo_url = s["logo_url"]
    conn = db.connect_torndb()
    source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                               source, str(sourceId))

    logo_id = None
    if source_investor == None or source_investor["logo"] == None or source_investor["logo"] == "":
        if logo_url is not None and len(logo_url.strip()) > 0:
            # image_value = download_crawler.get_image(logo_url)
            # if image_value is not None:
            #     logo_id = imgfs.put(image_value, content_type='jpeg', filename='investor_%s_%s.jpg' % (source, sourceId))
            #     logger.info("gridfs logo_id=%s" % logo_id)
            (logo_id, w, h) = parser_mysql_util.get_logo_id_new(logo_url, download_crawler, source, sourceId, "investor")
    else:
        logo_id = source_investor["logo"]
        #logger.info("logo_id=%s" % logo_id)

    if source_investor is None:
        sql = "insert source_investor(" \
              "name,website,description,logo,stage," \
              "field,type, source,sourceId,createTime," \
              "modifyTime,processStatus)" \
              " values" \
              "(%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,now()," \
              "now(),0)"
        source_investor_id = conn.insert(sql,
                                         s["name"], s["website"], s["description"], logo_id, s["stage"],
                                         s["field"], s["type"], source, sourceId)
    else:
        source_investor_id = source_investor["id"]
        sql = "update source_investor set name=%s,website=%s,description=%s,logo=%s,stage=%s,\
        field=%s,type=%s,modifyTime=now(),processStatus=0 where id=%s"
        conn.update(sql,
                    s["name"], s["website"], s["description"], logo_id, s["stage"],
                    s["field"], s["type"], source_investor_id)

    conn.close()
    return source_investor_id

def save_member_standard(source_member, download_crawler, source_company_member_rel=None):
    s = source_member
    conn = db.connect_torndb()
    source_member = conn.get("select * from source_member where source=%s and sourceId=%s",
                             s['source'], str(s['sourceId']))

    source = s["source"]
    sourceId = s["sourceId"]
    photo_url = s["photo_url"]

    photo_id = None
    #if photo_url is not None and photo_url.strip() != "":
    #    photo_id = get_logo_id(source, sourceId, "member", photo_url)

    if source_member == None or source_member["photo"] == None or source_member["photo"] == "":
        if photo_url is not None and photo_url != "":
            # image_value = download_crawler.get_image(photo_url)
            # if image_value is not None:
            #     photo_id = imgfs.put(image_value, content_type='jpeg',
            #                         filename='member_%s_%s.jpg' % (source, sourceId))
            # logger.info("gridfs logo_id=%s" % photo_id)
            (photo_id, w, h) = parser_mysql_util.get_logo_id_new(photo_url, download_crawler, source, sourceId, "member")
    else:
        photo_id = source_member["photo"]

    if source_member is None:
        sql = "insert source_member(name,photo,weibo,location,role,description,\
                education,work,source,sourceId,createTime,modifyTime,processStatus) \
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),0)"
        source_member_id = conn.insert(sql,
                                       s["name"], photo_id, s['weibo'], s['location'], s['role'], s['description'],
                                       s['education'], s['work'], s['source'], s['sourceId'])
    else:
        source_member_id = source_member["id"]
        sql = "update source_member set name=%s,photo=%s,weibo=%s,location=%s,role=%s,description=%s,\
        education=%s,work=%s,modifyTime=now(),processStatus=0 where id=%s"
        conn.update(sql,
                    s["name"], photo_id, s['weibo'], s['location'], s['role'], s['description'],
                    s['education'], s['work'], source_member_id)

    if source_company_member_rel is not None:
        r = source_company_member_rel
        source_company_member_rel = conn.get("select * from source_company_member_rel where \
                    sourceCompanyId=%s and sourceMemberId=%s",
                                         r["sourceCompanyId"], source_member_id)
        if source_company_member_rel is None:
            conn.insert("insert source_company_member_rel(sourceCompanyId, sourceMemberId, \
                    position, joinDate, leaveDate, type,createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s,%s, now(),now())",
                    r["sourceCompanyId"], source_member_id, r['position'], r['joinDate'], r['leaveDate'], r['type'])
        else:
            sql = "update source_company_member_rel set \
                position=%s, joinDate=%s, leaveDate=%s,type=%s,modifyTime=now() \
                where id=%s"
            conn.update(sql, r["position"], r["joinDate"], r["leaveDate"], r["type"], source_company_member_rel["id"])

    conn.close()

def save_company_standard(source_company,download_crawler):
    conn = db.connect_torndb()
    s = source_company
    result = conn.get("select * from source_company where source=%s and sourceId=%s order by id limit 1", s["source"],
                      str(s["sourceId"]))

    logo_id = None
    if result is None or result["logo"] is None or result["logo"] == "":
        log_url = s["logo"]
        if log_url is not None and len(log_url.strip()) > 0:
            # logger.info(log_url)
            # image_value = download_crawler.get_image(log_url)
            # if image_value is not None:
            #     logo_id = imgfs.put(image_value, content_type='jpeg', filename='company_%s_%s.jpg' % (s["source"], s["sourceId"]))
            (logo_id, w, h) = parser_mysql_util.get_logo_id_new(log_url, download_crawler, s["source"], s["sourceId"], "company")
    else:
        logo_id = result["logo"]
    logger.info("gridfs logo_id=%s" % logo_id)

    s["logo"] = logo_id

    if result is not None:
        source_company_id = result["id"]
        s["id"] = source_company_id
        update_source_company(s)
    else:
        sql = "insert source_company(name,fullName,description,brief,round, \
              productDesc, modelDesc, operationDesc, teamDesc, marketDesc, compititorDesc, advantageDesc, planDesc, \
              roundDesc,companyStatus,fundingType,locationId, address, \
              phone, establishDate, logo,source,sourceId, \
              createTime,modifyTime, \
              field,subField,tags, headCountMin, headCountMax,processStatus) \
              values \
              (%s,%s,%s,%s,%s, \
              %s,%s,%s,%s,%s,%s,%s,%s, \
              %s,%s,%s,%s,%s, \
              %s,%s,%s, %s, %s, \
              now(),now(), \
              %s,%s,%s, %s, %s,0)"

        source_company_id = conn.insert(sql,
                                        s["name"], s["fullName"], s["description"], s["brief"], s["round"],
                                        s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"),
                                        s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"),
                                        s.get("advantageDesc"), s.get("planDesc"),
                                        s["roundDesc"], s["companyStatus"], s["fundingType"], s["locationId"],
                                        s["address"],
                                        s["phone"], s["establishDate"], s["logo"], s["source"], s["sourceId"],
                                        s["field"], s["subField"], s["tags"], s["headCountMin"], s["headCountMax"]
                                        )
    conn.close()
    return source_company_id


def update_source_company(source_company):
    s = source_company
    conn = db.connect_torndb()
    conn.update("update source_company set \
                        name=%s, fullName=%s, description=%s, companyStatus=%s, fundingType=%s,\
                        locationId=%s,establishDate=%s,logo=%s, \
                        productDesc=%s, modelDesc=%s, operationDesc=%s, teamDesc=%s, marketDesc=%s, compititorDesc=%s, advantageDesc=%s, planDesc=%s, \
                        modifyTime=now(),processStatus=0, active=null \
                        where id=%s",
                s["name"], s["fullName"], s["description"], s["companyStatus"], s["fundingType"],
                s["locationId"], s["establishDate"], s["logo"],
                s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"),
                s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
                s["id"]
                )
    conn.close()

def save_artifacts_standard(source_company_id, source_artifacts):
    conn = db.connect_torndb()
    conn.execute("delete from source_artifact where sourceCompanyId=%s", source_company_id)
    for s in source_artifacts:
        sql = "insert source_artifact(sourceCompanyId, name, description, link, domain, type,createTime,modifyTime) \
                      values(%s,%s,%s,%s,%s,%s,now(),now())"
        conn.insert(sql, source_company_id, s["name"], s["description"], s["link"], s["domain"], s["type"])
    conn.close()


def save_jobs_standard(source_jobs):
    conn = db.connect_torndb()
    for source_job in source_jobs:
        s = source_job
        sourceCompanyId = s["sourceCompanyId"]
        sourceId = s["sourceId"]
        source_job = conn.get("select * from source_job where sourceCompanyId=%s and sourceId=%s",
                              sourceCompanyId, sourceId)

        if source_job is None:
            sql = "insert source_job(sourceCompanyId, position, salary, description, domain," \
                  "locationId, educationType, workYearType, startDate, updateDate," \
                  "sourceId, createTime, modifyTime)" \
                  "values" \
                  "(%s,%s,%s,%s,%s," \
                  "%s,%s,%s,%s,%s," \
                  "%s, now(),now())"
            #version 2 there is no borntime in lagou
            # conn.insert(sql,
            #             sourceCompanyId, s["position"], s["salary"], s["description"], s["domain"],
            #             s["locationId"], s["educationType"], s["workYearType"], s["startDate"], s["updateDate"],
            #             sourceId)
            conn.insert(sql,
                        sourceCompanyId, s["position"], s["salary"], s["description"], s["domain"],
                        s["locationId"], s["educationType"], s["workYearType"], s["updateDate"], s["updateDate"],
                        sourceId)
        else:
            sql = "update source_job set position=%s, salary=%s, description=%s, domain=%s, locationId=%s,\
                    educationType=%s, workYearType=%s, updateDate=%s, modifyTime=now() where id=%s"
            conn.update(sql, s["position"], s["salary"], s["description"], s["domain"], s["locationId"],
                        s["educationType"], s["workYearType"], s["updateDate"], source_job["id"]
                        )
    conn.close()

def update_active(SOURCE, sourceId, active):
    conn = db.connect_torndb()
    conn.update("update source_company set active=%s where source=%s and sourceId=%s", active, SOURCE, str(sourceId))
    conn.close()

def save_source_company_name(source_company_id,name,type):
    if name is None or name.strip() == "":
        return

    conn = db.connect_torndb()
    n = conn.get("select * from source_company_name where sourceCompanyId=%s and name=%s",
                 source_company_id, name)
    if n is None:
        chinese = hz.is_chinese_string(name)
        if chinese:
            chinese = 'Y'
        else:
            chinese = 'N'
        conn.insert("insert source_company_name(sourceCompanyId,name,type,chinese,createTime,modifyTime) values( \
                    %s,%s,%s,%s,now(),now())",
                    source_company_id,name,type,chinese)
    conn.close()


def save_company_fullName(name, source, sourceId, brief=None):

    conn = db.connect_torndb()
    result = conn.get("select * from source_company where source=%s and sourceId=%s order by id limit 1", source,sourceId)
    if result is not None:
        source_company_id = result["id"]
    else:
        if brief is None:
            sql = "insert source_company(name,fullName,source,sourceId,createTime,modifyTime) \
                       values(%s,%s,%s,%s,now(),now())"

            source_company_id = conn.insert(sql, name,name,source,sourceId)
        else:
            sql = "insert source_company(name,fullName,source,sourceId,createTime,modifyTime,brief) \
                                   values(%s,%s,%s,%s,now(),now(),%s)"

            source_company_id = conn.insert(sql, name, name, source, sourceId, brief)
    conn.close()
    return source_company_id

def save_company_yitai(shortname, name, source, sourceId, brief=None):

    conn = db.connect_torndb()
    result = conn.get("select * from source_company where source=%s and sourceId=%s order by id limit 1", source,sourceId)
    if result is not None:
        source_company_id = result["id"]
    else:
        if brief is None:
            sql = "insert source_company(name,fullName,source,sourceId,createTime,modifyTime) \
                       values(%s,%s,%s,%s,now(),now())"

            source_company_id = conn.insert(sql, shortname,name,source,sourceId)
        else:
            if len(brief) < 100:
                sql = "insert source_company(name,fullName,source,sourceId,createTime,modifyTime,brief) \
                                             values(%s,%s,%s,%s,now(),now(),%s)"
            else:
                sql = "insert source_company(name,fullName,source,sourceId,createTime,modifyTime,description) \
                                             values(%s,%s,%s,%s,now(),now(),%s)"
            source_company_id = conn.insert(sql, shortname, name, source, sourceId, brief)
    conn.close()
    return source_company_id


def delete_source_company_name(source_company_id):
    conn = db.connect_torndb()
    conn.execute("delete from source_company_name where sourceCompanyId=%s", source_company_id)
    conn.close()

def delete_source_mainbeianhao(source_company_id):
    conn = db.connect_torndb()
    conn.execute("delete from source_mainbeianhao where sourceCompanyId=%s", source_company_id)
    conn.close()

def find_source_investor_id(SOURCE, sourceId):
    conn = db.connect_torndb()
    source_investor_id = conn.get("select id from source_investor where source=%s and sourceId=%s limit 1", SOURCE, sourceId)
    conn.close()
    return source_investor_id

def get_source_company_by_source_and_sourceid(source, sourceId):
    conn = db.connect_torndb()
    result = conn.get("select * from source_company where source=%s and sourceId=%s order by id limit 1", source, str(sourceId))
    conn.close()
    return result


#special for kr36 investor working for 2018/03/06
def save_investor_standard_new(source_investor, download_crawler):
    s = source_investor
    source = s["source"]
    sourceId = s["sourceId"]
    logo_url = s["logo"]
    conn = db.connect_torndb()
    source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s",
                               source, sourceId)

    logo_id = None
    if source_investor is None or source_investor["logo"] is None or source_investor["logo"] == "":
        if logo_url is not None and len(logo_url.strip()) > 0:
            (logo_id, w, h) = parser_mysql_util.get_logo_id_new(logo_url, download_crawler, source, sourceId, "investor")
    else:
        logo_id = source_investor["logo"]

    if source_investor is None:
        sql = "insert source_investor(" \
              "name,website,description,logo,stage," \
              "field,type, source,sourceId,createTime," \
              "modifyTime,processStatus,wechatId,weibo,enName,fullName,enFullName,establishDate)" \
              " values" \
              "(%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,now()," \
              "now(),0,%s,%s,%s,%s,%s,%s)"
        source_investor_id = conn.insert(sql,
                                         s["name"], s["website"], s["description"], logo_id, s.get("stage"),
                                         s.get("field"), s.get("type"), source, sourceId,
                                         s.get("wechatId"), s.get("weibo"),s.get("enName"), s.get("fullName"),
                                         s.get("enFullName"), s.get("establishDate"))
    else:
        source_investor_id = source_investor["id"]
        sql = "update source_investor set name=%s,website=%s,description=%s,logo=%s,stage=%s," \
              "field=%s,type=%s,wechatId=%s,weibo=%s,enName=%s,fullName=%s," \
              "enFullName=%s,establishDate=%s, modifyTime=now(),processStatus=0 where id=%s"
        conn.update(sql,
                    s["name"], s["website"], s["description"], logo_id, s.get("stage"),
                    s.get("field"), s.get("type"),
                    s.get("wechatId"), s.get("weibo"), s.get("enName"), s.get("fullName"),
                    s.get("enFullName"), s.get("establishDate"),
                    source_investor_id)

    conn.close()
    return source_investor_id

def save_investor_contact_standard(source_investor_id, contacts):
    conn = db.connect_torndb()
    conn.execute("delete from source_investor_contact where sourceInvestorId=%s", source_investor_id)
    for s in contacts:
        sql = "insert source_investor_contact(sourceInvestorId, locationId, address, phone, email, createTime,modifyTime) \
                      values(%s,%s,%s,%s,%s,now(),now())"
        conn.insert(sql, source_investor_id, s["locationId"], s["address"], s["phone"], s["email"])
    conn.close()

def save_investor_member_standard(source_investor_id, members,download_crawler):
    conn = db.connect_torndb()
    conn.execute("delete from source_investor_member where sourceInvestorId=%s", source_investor_id)
    for s in members:
        (logo_id, w, h) = parser_mysql_util.get_logo_id_new(s["logo"], download_crawler, s["source"], s["sourceId"], "member")
        sql = "insert source_investor_member(sourceInvestorId, investorMemberId,source,sourceId,name,logo, position, description, createTime,modifyTime) \
                      values(%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"
        conn.insert(sql, source_investor_id, None,s["source"], s["sourceId"], s["name"], logo_id, s["position"], s["description"])
    conn.close()

def save_blockchain_standard_feixiaohao(source_feixiaohao, download_crawler):
    s = source_feixiaohao

    logo_url = s["logo"]
    conn = db.connect_torndb()

    source = None
    if s["name"] is not None and s["name"].strip() != "":
        source = conn.get("select * from digital_token where symbol=%s and name=%s",
                           s["symbol"], s["name"])

    elif s["enname"] is not None and s["enname"].strip() != "":
        source = conn.get("select * from digital_token where symbol=%s and enname=%s",
                          s["symbol"], s["enname"])

    else:
        source = conn.get("select * from digital_token where symbol=%s",
                          s["symbol"])


    logo_id = None
    if source is None or source["logo"] is None or source["logo"] == "":
        if logo_url is not None and len(logo_url.strip()) > 0:
            (logo_id, w, h) = parser_mysql_util.get_logo_id_new(logo_url, download_crawler,
                                                                13511, s["symbol"], "blockchain")
    else:
        logo_id = source["logo"]

    if source is None:
        sql = "insert digital_token(" \
              "companyId,symbol,name,enname,publishDate," \
              "websites,browsers,description,whitepaper,logo,createTime," \
              "modifyTime)" \
              " values" \
              "(%s,%s,%s,%s,%s," \
              "%s,%s,%s,%s,%s, now()," \
              "now())"
        source_d_id = conn.insert(sql,s["companyId"], s["symbol"], s["name"],
                                         s["enname"], s["publishDate"], s["websites"],
                                         s["browsers"], s["description"], s["whitepaper"],logo_id)

    else:
        source_d_id = source["id"]
        sql = "update digital_token set name=%s,enname=%s,publishDate=%s," \
              "websites=%s,browsers=%s,description=%s,whitepaper=%s,logo=%s,modifyTime=now() where id=%s"
        conn.update(sql, s["name"],
                    s["enname"], s["publishDate"], s["websites"],
                    s["browsers"], s["description"], s["whitepaper"], logo_id,
                    source_d_id)

    conn.close()
    return source_d_id

def save_blockchain_cq(source_feixiaohao):
    flag = False
    s = source_feixiaohao

    conn = db.connect_torndb()

    source = None
    if s["name"] is not None and s["name"].strip() != "":
        source = conn.get("select * from digital_token where symbol=%s and name=%s",
                           s["symbol"], s["name"])

    elif s["enname"] is not None and s["enname"].strip() != "":
        source = conn.get("select * from digital_token where symbol=%s and enname=%s",
                          s["symbol"], s["enname"])

    else:
        source = conn.get("select * from digital_token where symbol=%s",
                          s["symbol"])


    if source is not None:
        source_d_id = source["id"]
        s_m = conn.get("select * from digital_token_market where digitalTokenId=%s", source_d_id)
        if s_m is not None:
            sql = "update digital_token_market set totalCirculation=%s where digitalTokenId=%s"
            conn.update(sql, s["cq"],
                        source_d_id)
            flag = True

    conn.close()
    return flag