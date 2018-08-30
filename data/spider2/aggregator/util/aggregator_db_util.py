# -*- coding: utf-8 -*-
import os, sys
from pymongo import MongoClient
reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
import config
import db
import loghelper

import helper

#logger
loghelper.init_logger("aggregator_db_util", stream=True)
logger = loghelper.get_logger("aggregator_db_util")

#mongo
mongo = db.connect_mongo()
collection_gongshang = mongo.info.gongshang

def update_source_company_found(company_id, source_company_id):
    conn = db.connect_torndb()
    conn.update("update source_company set companyId=%s where id=%s", company_id, source_company_id)
    conn.close()


def insert_company(code, source_company, test):
    table_names = helper.get_table_names(test)
    s = source_company
    conn = db.connect_torndb()
    sql = "insert " + table_names["company"] + "(code,name,fullName,description,brief,\
        productDesc, modelDesc, operationDesc, teamDesc, marketDesc, compititorDesc, advantageDesc, planDesc, \
        round,roundDesc,companyStatus,fundingType,preMoney,currency,\
        locationId,address,phone,establishDate,logo,type,\
        headCountMin,headCountMax,\
        active,createTime,modifyTime) \
        values(%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,%s,%s, \
            %s,%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,\
            %s,%s,\
            %s,now(),now())"
    company_id = conn.insert(sql,
            code,s["name"],s["fullName"],s["description"],s["brief"],
            s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
            s["round"],s["roundDesc"],s["companyStatus"],s["fundingType"],s["preMoney"],s["currency"],
            s["locationId"],s["address"],s["phone"],s["establishDate"],s["logo"],s["type"],
            s["headCountMin"],s["headCountMax"],
            'Y')

    if not test:
        conn.update("update source_company set companyId=%s where id=%s", company_id, s["id"])

    conn.close()
    return company_id


def update_company(company_id, source_company):
    s = source_company
    conn = db.connect_torndb()
    sql = "update company set \
                name=%s,fullName=%s,description=%s,brief=%s,\
                productDesc=%s, modelDesc=%s, operationDesc=%s, teamDesc=%s, marketDesc=%s, compititorDesc=%s, advantageDesc=%s, planDesc=%s, \
                round=%s,roundDesc=%s,companyStatus=%s,fundingType=%s,preMoney=%s,currency=%s,\
                locationId=%s,address=%s,phone=%s,establishDate=%s,logo=%s,\
                headCountMin=%s,headCountMax=%s,\
                modifyTime=now() \
                where id=%s"
    conn.update(sql,
            s["name"],s["fullName"],s["description"],s["brief"],
            s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
            s["round"],s["roundDesc"],s["companyStatus"],s["fundingType"],s["preMoney"],s["currency"],
            s["locationId"],s["address"],s["phone"],s["establishDate"],s["logo"],
            s["headCountMin"],s["headCountMax"],
            company_id
            )
    conn.close()


def insert_artifact(company_id, sa, test=False):
    table_names = helper.get_table_names(test)
    conn = db.connect_torndb()
    sql = "insert " + table_names["artifact"] + "(companyId,name,description,link,domain,type,active,createTime,modifyTime) \
                            values(%s,%s,%s,%s,%s,%s,%s,now(),now())"
    artifact_id = conn.insert(sql,
            company_id,
            sa["name"],
            sa["description"],
            sa["link"],
            sa["domain"],
            sa["type"],
            sa["active"]
    )
    conn.close()
    return artifact_id


def update_artifact():
    conn = db.connect_torndb()
    conn.close()


def insert_member(source_member, test=False):
    table_names = helper.get_table_names(test)
    conn = db.connect_torndb()
    member_id = conn.insert("insert " + table_names["member"] + "( \
                                name,description,education,work,photo,active,createTime,modifyTime \
                                ) \
                                values(%s,%s,%s,%s,%s,'Y',now(),now())",
                                source_member["name"],
                                source_member["description"],
                                source_member["education"],
                                source_member["work"],
                                source_member["photo"]
        )
    conn.close()
    return member_id


def update_member(member):
    m = member
    conn = db.connect_torndb()
    conn.update("update member set \
                        description=%s, education=%s, work=%s, photo=%s, modifyTime=now() \
                        where id=%s",
                        m["description"],m["education"],m["work"],m["photo"],m["id"])
    conn.close()


def get_company_member_rel(company_id, member_id):
    conn = db.connect_torndb()
    cmrel = conn.get("select * from company_member_rel where companyId=%s and memberId=%s order by id limit 1",
                           company_id, member_id)
    conn.close()
    return cmrel


def insert_company_member_rel(company_id, member_id, source_company_member_rel, test=False):
    rel = source_company_member_rel
    conn = db.connect_torndb()
    table_names = helper.get_table_names(test)
    item = conn.get("select * from " + table_names["company_member_rel"] + " where companyId=%s and memberId=%s "
                    "and (active is null or active='Y' or (active='N' and modifyUser != 139)) "
                    "limit 1", company_id, member_id)
    if item is None:

        cmrelId = conn.insert("insert " + table_names["company_member_rel"] +"(\
                    companyId,memberId,position,joinDate,leaveDate,type,\
                    active,createTime,modifyTime) \
                    values(%s,%s,%s,%s,%s,%s,'Y',now(),now())",
                    company_id, member_id, rel["position"],rel["joinDate"],rel["leaveDate"],rel["type"]
                    )
    else:
        cmrelId = item["id"]
    conn.close()
    return cmrelId

def update_company_member_rel():
    conn = db.connect_torndb()
    conn.close()

def insert_funding(company_id, source_funding):
    sf = source_funding
    conn = db.connect_torndb()
    sql = "insert funding(companyId,preMoney,postMoney,investment,\
                            round,roundDesc,currency,precise,fundingDate,fundingType,\
                            active,createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Y',now(),now())"
    fundingId=conn.insert(sql,
                          company_id,
                          sf["preMoney"],
                          sf["postMoney"],
                          sf["investment"],
                          sf["round"],
                          sf["roundDesc"],
                          sf["currency"],
                          sf["precise"],
                          sf["fundingDate"],
                          8030      #已融资结束
                          )
    conn.close()
    return fundingId

def update_funding():
    conn = db.connect_torndb()
    conn.close()


def insert_funding_investor_rel(funding_id, investor_id, source_funding_investor_rel):
    sfir = source_funding_investor_rel
    conn = db.connect_torndb()
    sql = "insert funding_investor_rel(fundingId, investorId, currency, investment,\
                        precise,active,createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s,'Y',now(),now())"
    fundingInvestorRelId = conn.insert(sql,
                funding_id,
                investor_id,
                sfir["currency"],
                sfir["investment"],
                sfir["precise"]
            )
    conn.close()
    return fundingInvestorRelId


def insert_footprint(company_id, sf):
    conn = db.connect_torndb()
    sql = "insert footprint(companyId,footDate,description,active,createTime,modifyTime) \
                values(%s,%s,%s,'Y',now(),now())"
    footprint_id = conn.insert(sql,company_id,sf["footDate"],sf["description"])
    conn.close()
    return footprint_id


def insert_job(company_id, source_job):
    job = source_job
    conn = db.connect_torndb()
    sql = 'insert job(companyId, position, salary, description, domain,' \
                  ' locationId, educationType, workYearType, startDate, updateDate,' \
                  'createTime, modifyTime) values(' \
                  '%s, %s, %s, %s, %s,' \
                  '%s, %s, %s, %s, %s,' \
                  'now(), now())'
    job_id = conn.insert(sql, company_id, job['position'], job['salary'], job['description'], job['domain'],
            job['locationId'], job['educationType'], job['workYearType'], job['startDate'], job['updateDate'])
    conn.close()
    return job_id


def get_gongshang_by_name(name):
    gongshang = collection_gongshang.find_one({"name": name})
    return gongshang