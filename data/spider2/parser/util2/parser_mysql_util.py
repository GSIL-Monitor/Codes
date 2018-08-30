# -*- coding: utf-8 -*-
import os, sys
import datetime
import json
from pymongo import MongoClient
import gridfs
import pymongo
from bson import ObjectId
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper
import hz
import name_helper
import util
import image_helper
import oss2_helper
import download
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))

#logger
loghelper.init_logger("parser_mysql_util", stream=True)
logger = loghelper.get_logger("parser_mysql_util")

oss2put = oss2_helper.Oss2Helper()



def get_logo_id(logo_url, download_crawler, source, sourceId, catename):
    mongo = db.connect_mongo()
    imgfs = gridfs.GridFS(mongo.gridfs)
    logo_id = None
    if logo_url is not None and len(logo_url.strip()) > 0:
        logger.info("Download logo: %s",logo_url)
        image_value = download_crawler.get_image(logo_url)
        if image_value is not None:
            logo_id = imgfs.put(image_value, content_type='jpeg', filename='%s_%s_%s.jpg' % (catename, source, sourceId))
    mongo.close()
    return logo_id

def get_logo_id_size(logo_url, download_crawler, source, sourceId, catename):
    mongo = db.connect_mongo()
    imgfs = gridfs.GridFS(mongo.gridfs)
    logo_id = None
    height = None
    width = None
    if logo_url is not None and len(logo_url.strip()) > 0:
        logger.info("Download logo: %s",logo_url)
        (image_value, width, height) = download_crawler.get_image_size(logo_url)
        if image_value is not None:
            logo_id = imgfs.put(image_value, content_type='jpeg', filename='%s_%s_%s.jpg' % (catename, source, sourceId))
    mongo.close()
    return (logo_id, width, height)

def get_logo_id_new(logo_url, download_crawler, source, sourceId, catename):
    mongo = db.connect_mongo()
    # imgfs = gridfs.GridFS(mongo.gridfs)
    name = None
    height = None
    width = None
    if logo_url is not None and len(logo_url.strip()) > 0:
        logger.info("Download logo: %s",logo_url)
        # (image_value, width, height) = download_crawler.get_image_size(logo_url)
        (image_file, width, height) = download_crawler.get_image_size_new(logo_url)
        if image_file is not None:
            # logo_id = imgfs.put(image_value, content_type='jpeg', filename='%s_%s_%s.jpg' % (catename, source, sourceId))
            # out = imgfs.get(ObjectId(logo_id))
            name = util.get_uuid()
            logger.info("%s->%s|%s", logo_url, name, image_file)
            if source in [13835,13836,13613]:
                # img, width, height = util.convert_image(out, out.name, size=1024)
                img, width, height = util.convert_image(image_file, name, size=1024)
            elif source in [13613,13803]:
                img, width, height = util.convert_image(image_file, name, size=width)
            else:
                # img, width, height = util.convert_image(out, out.name)
                img, width, height = util.convert_image(image_file, name)
            headers = {"Content-Type": "image/jpeg"}
            # oss2put.put(str(logo_id), img, headers=headers)
            oss2put.put(name, img, headers=headers)
    # mongo.close()
    return (name, width, height)


def get_logo_stock(stockname, code, source):
    name = None
    height = None
    width = None
    if stockname is not None and code is not None:
        logger.info("prepare logo: %s|%s", stockname, code)
        # (image_value, width, height) = download_crawler.get_image_size(logo_url)
        im,image = image_helper.gen_stock_image(stockname, code)
        name = source+"-"+code
        logger.info("%s|%s", name,image)

        headers = {"Content-Type": "image/jpeg"}
        oss2put.put(name, image.getvalue(), headers=headers)
    return (name, width, height)


def get_location(location):
    conn = db.connect_torndb()
    result = conn.get("select * from location where locationName=%s", location)
    conn.close()
    return result

def update_db_processStatus(source, sourceId, value):
    conn = db.connect_torndb()
    conn.update("update source_company set processStatus=%s where source=%s and sourceId=%s", value, source, sourceId)
    conn.close()

def save_company(s, download_crawler):
    # save logo
    s["logo"] = get_logo_id(s["logo"], download_crawler, s["source"], s["sourceId"], "company")
    conn = db.connect_torndb()
    sql = "insert source_company(name,fullName,description,productDesc,modelDesc,operationDesc,teamDesc,marketDesc,compititorDesc,advantageDesc, \
           planDesc,brief,round,roundDesc,companyStatus,fundingType,preMoney,investment,currency,locationId,address,phone,establishDate,logo,type, \
           source,sourceId,verify,active,createTime,modifyTime,field,subField,tags,headCountMin,headCountMax,auditor,auditTime,auditMemo,recommendCompanyIds) \
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    source_company_id = conn.insert(sql,
                                s["name"], s["fullName"], s["description"], s["productDesc"], s["modelDesc"], s["operationDesc"], s["teamDesc"],
                                s["marketDesc"], s["compititorDesc"], s["advantageDesc"], s["planDesc"], s["brief"], s["round"], s["roundDesc"],
                                s["companyStatus"], s["fundingType"], s["preMoney"], s["investment"], s["currency"], s["locationId"], s["address"],
                                s["phone"], s["establishDate"], s["logo"], s["type"], s["source"], s["sourceId"], s["verify"], s["active"], s["field"],
                                s["subField"], s["tags"], s["headCountMin"], s["headCountMax"], s["auditor"], s["auditTime"], s["auditMemo"], s["recommendCompanyIds"]
                                )
    conn.close()
    return source_company_id

def save_artifact(sourceCompanyId, sadata):
    conn = db.connect_torndb()
    sql = "insert source_artifact(sourceCompanyId,name,description,link,domain,type,verify,active,createTime,modifyTime,rank,rankDate,extended,expanded,artifactStatus) \
                      values(%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s,%s,%s,%s,%s)"
    source_artifact_id = conn.insert(sql, sourceCompanyId, sadata["name"], sadata["description"],sadata["link"], sadata["domain"], sadata["type"], sadata["verify"],
                sadata["active"], sadata["rank"], sadata["rankDate"], sadata["extended"], sadata["expanded"], sadata["artifactStatus"])
    conn.close()
    return source_artifact_id

def save_company_name(sourceCompanyId, scndata):
    conn = db.connect_torndb()
    sql = "insert source_company_name(sourceCompanyId, name, chinese, type, extended, verify, expanded, createTime,modifyTime) \
                      values(%s,%s,%s,%s,%s,%s,%s,now(),now())"
    source_company_name_id = conn.insert(sql, sourceCompanyId, scndata["name"], scndata["chinese"], scndata["type"], scndata["extended"], scndata["verify"], scndata["expanded"])
    conn.close()
    return source_company_name_id

def save_mainbeianhao(sourceCompanyId, smdata):
    conn = db.connect_torndb()
    sql = "insert source_mainbeianhao(sourceCompanyId, mainBeianhao, verify, expanded, createTime,modifyTime) \
                          values(%s,%s,%s,%s,now(),now())"
    source_mainbeianhao_id = conn.insert(sql, sourceCompanyId, smdata["mainBeianhao"], smdata["verify"], smdata["expanded"])
    conn.close()
    return source_mainbeianhao_id

def save_funding(sourceCompanyId, sfdata, download_crawler):
    conn = db.connect_torndb()
    sql = "insert source_funding(sourceCompanyId,preMoney,postMoney,investment,round,roundDesc,currency,precise,fundingDate,verify,createTime,modifyTime,processStatus) \
                              values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s)"
    source_funding_id = conn.insert(sql, sourceCompanyId, sfdata["preMoney"], sfdata["postMoney"], sfdata["investment"], sfdata["round"], sfdata["roundDesc"],
                                    sfdata["currency"], sfdata["precise"], sfdata["fundingDate"], sfdata["verify"], sfdata["processStatus"])

    if sfdata.has_key("_investorIds") and len(sfdata["_investorIds"]) > 0:
        mongo = db.connect_mongo()
        collection_investor = mongo.source.investor
        for investorId in sfdata["_investorIds"]:
            investor = collection_investor.find_one({"_id": investorId})
            if investor is None:
                continue

            if investor["sourceId"] is not None:
                source_investor = conn.get("select * from source_investor where source=%s and sourceId=%s limit 1", investor["source"], investor["sourceId"])
            else:
                source_investor = conn.get("select * from source_investor where source=%s and name=%s limit 1", investor["source"], investor["name"])

            if source_investor is not None:
                source_investor_id = source_investor["id"]
            else:
                source_investor_id = save_investor(investor, download_crawler)
            source_funding_investor_rel = conn.get("select * from source_funding_investor_rel where sourceFundingId=%s and sourceInvestorId=%s",
                                                   source_funding_id, source_investor_id)
            if source_funding_investor_rel is None:
                conn.insert("insert source_funding_investor_rel(sourceFundingId, sourceInvestorId,createTime,modifyTime) \
                            values(%s,%s, now(),now())", source_funding_id, source_investor_id)
        mongo.close()
    conn.close()
    return source_funding_id

def save_investor(idata, download_crawler):
    # save logo
    idata["logo"] = get_logo_id(idata["logo"], download_crawler, idata["source"], idata["sourceId"], "investor")
    conn = db.connect_torndb()
    sql = "insert source_investor(name,website,description,logo,stage,field,type,source,sourceId,verify,createTime,modifyTime,processStatus) \
                              values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s)"
    source_investor_id = conn.insert(sql, idata["name"], idata["website"], idata["desciption"], idata["logo"], idata["stage"], idata["field"],
                                     idata["type"], idata["source"], idata["sourceId"], idata["verify"], idata["processStatus"])
    conn.close()
    return source_investor_id

def save_company_member_rel(sourceCompanyId, scmdata, download_crawler):
    #Check member data in mongo
    if scmdata["_memberId"] is None:
        return
    mongo = db.connect_mongo()
    collection_member = mongo.source.member
    member = collection_member.find_one({"_id": scmdata["_memberId"]})
    mongo.close()
    if member is None:
        return

    conn = db.connect_torndb()

    if member["sourceId"] is not None:
        source_member = conn.get("select * from source_member where source=%s and sourceId=%s limit 1", member["source"], member["sourceId"])
    else:
        source_member = conn.get("select * from source_member where source=%s and name=%s limit 1", member["source"], member["name"])

    if source_member is not None:
        source_member_id = source_member["id"]
    else:
        source_member_id = save_member(member, download_crawler)

    source_company_member_rel_id = conn.insert("insert source_company_member_rel(sourceCompanyId,sourceMemberId,position,joinDate,leaveDate,type,verify,createTime,modifyTime) \
                                    values(%s,%s,%s,%s,%s,%s,%s,now(),now())", sourceCompanyId, source_member_id, scmdata['position'],
                                    scmdata['joinDate'], scmdata['leaveDate'], scmdata['type'], scmdata["verify"])
    conn.close()
    return source_company_member_rel_id

def save_member(mdata, download_crawler):
    # save logo
    mdata["photo"] = get_logo_id(mdata["photo"], download_crawler, mdata["source"], mdata["sourceId"], "member")
    conn = db.connect_torndb()
    sql = "insert source_member(name,photo,weibo,location,role,description,education,work,source,sourceId,verify,createTime,modifyTime,processStatus) \
                                  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now(),%s)"
    source_member_id = conn.insert(sql, mdata["name"], mdata["photo"], mdata["weibo"], mdata["location"], mdata["role"], mdata["description"],
                                   mdata["education"], mdata["work"], mdata["source"], mdata["sourceId"], mdata["verify"], mdata["processStatus"])
    conn.close()
    return source_member_id

def insert_audit_source_company(sourceCompanyId):
    conn = db.connect_torndb()
    sql = "insert audit_source_company(source_company_id,createTime) values(%s,now())"
    source_member_id = conn.insert(sql, sourceCompanyId)
    conn.close()
    return source_member_id


if __name__ == "__main__":
    # if len(sys.argv) > 1:
    #     param = sys.argv[1]
    #     if param == "incr":
    #         start_run(1, "incr")
    #     elif param == "all":
    #         start_run(1, "all")
    #     else:
    #         link = param
    #         download_crawler = download.DownloadCrawler(use_proxy=False)
    #         crawler_news({}, ListCrawler(), link, None, download_crawler)
    # else:
    #     start_run(1, "incr")

    download_crawler = download.DownloadCrawler(use_proxy=False)
    (imgurl, width, height) = get_logo_id_new('https://mmbiz.qpic.cn/mmbiz_jpg/gqEibpZa7hiaLEQ32Fk24O9ibJ9IC6ibVPdbPXQxs69wLoFic9kZFUfr8WOnFtKt6KYNGibhtW0mMzIPDUHlhC7AGOmQ/640?wx_fmt=jpeg',
                                              download_crawler, 13333, "3333", "news")
    print (imgurl, int(width), int(height))
    # imgurl, width, height = get_logo_stock(u"佳利达", "870397", "13400")
    # print (imgurl)

