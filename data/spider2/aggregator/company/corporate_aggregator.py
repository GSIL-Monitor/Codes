# -*- coding: utf-8 -*-
import os, sys
import time
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random
import pymongo
from kafka import (KafkaClient, SimpleProducer)
import find_company
import json

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import name_helper
import db

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import aggregator_db_util
import helper

#logger
loghelper.init_logger("corporate1_aggregate", stream=True)
logger = loghelper.get_logger("corporate1_aggregate")


def update_corporate(company_id):

    logger.info("company_id: %s" % company_id)
    conn = db.connect_torndb()

    company = conn.get("select * from company where id=%s", company_id)
    if company["corporateId"] is None:
        corporate_id = insert_corporate(company)
    else:
        corporate_id = company["corporateId"]
        # aggregator_db_util.update_corporate(company_id, company["corporateId"])
        update_column(company_id, corporate_id)

    conn.close()
    return corporate_id

def add_corporate_alias(company_id, corporate_id):
    conn = db.connect_torndb()
    corporate_aliases = conn.query("select * from company_alias where companyId=%s", company_id)
    for s in corporate_aliases:
        if s["name"] is None or s["name"].strip() == "":
            continue
        name = s["name"].strip()
        alias = conn.get("select * from corporate_alias where corporateId=%s and name=%s limit 1",
                         corporate_id, name)
        if alias is None:
            sql = "insert corporate_alias(corporateId,name,type,active,createTime) \
                    values(%s,%s,%s,%s,now())"
            conn.insert(sql, corporate_id, name, s["type"], 'Y')
    conn.close()


def add_funding_corporateId(company_id, corporate_id):
    conn = db.connect_torndb()
    conn.update("update funding set corporateId=%s where companyId=%s", corporate_id, company_id)
    conn.close()


def set_corporateId(company_id, corporate_id):
    conn = db.connect_torndb()
    conn.update("update company set corporateId=%s where id=%s", corporate_id, company_id)
    conn.close()


def insert_corporate(s):

    conn = db.connect_torndb()
    sql = "insert corporate(code,name,fullName,website,brief,description,round,roundDesc,corporateStatus,fundingType,currentRound,currentRoundDesc, \
           preMoney,investment,postMoney,shareRatio,currency,headCountMin,headCountMax,locationId,address,phone,establishDate,logo, \
           verify,active,createTime,modifyTime) \
           values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"

    corporate_id = conn.insert(sql,
                                s["code"], s["name"], s["fullName"], s["website"], s["brief"], s["description"], s["round"], s["roundDesc"],
                                s["companyStatus"], s["fundingType"], s["currentRound"], s["currentRoundDesc"],s["preMoney"], s["investment"],
                                s["postMoney"], s["shareRatio"], s["currency"], s["headCountMin"], s["headCountMax"], s["locationId"], s["address"],
                                s["phone"], s["establishDate"], s["logo"], s["verify"], s["active"]
                                )
    conn.close()
    return corporate_id


def update_column(company_id, corporate_id):
    columns = [
        "description",
        "fullName",
        "website",
        "round",
        "logo",
        "establishDate",
        "locationId",
    ]

    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    corporate = conn.get("select * from corporate where id=%s", corporate_id)
    if company is not None and corporate is not None:
        for column in columns:
            sql = "update corporate set " + column + "=%s where id=%s"
            if (corporate[column] is None and company[column] is not None):
               # (corporate[column] is not None and company[column] is not None and company[column]!=corporate[column]):
                conn.update(sql, company[column], corporate_id)
    conn.close()



if __name__ == "__main__":

    pass