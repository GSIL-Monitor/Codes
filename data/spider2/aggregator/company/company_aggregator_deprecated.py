# -*- coding: utf-8 -*-
# 准备停用, 由company_aggregator2.py代替

import os, sys
import time
from pypinyin import pinyin, lazy_pinyin
import pypinyin
import re, random
import json
from kafka import (KafkaClient, SimpleProducer)

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../util'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../support'))
import config
import loghelper
import util
import db

#logger
loghelper.init_logger("company_aggregator", stream=True)
logger = loghelper.get_logger("company_aggregator")

# kafka
kafkaProducer = None


def initKafka():
    global kafkaProducer

    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)

def get_company_code(name):
    conn = db.connect_torndb()
    datestring = "%s" % time.strftime("%Y%m%d", time.localtime())

    if len(name) <8 :
        pinyin = lazy_pinyin(name.decode('utf-8'))
        company_code = ''.join(pinyin)
    else:
        pinyin = lazy_pinyin(name.decode('utf-8'), style=pypinyin.INITIALS)
        company_code = ''.join(pinyin)

    bs = bytes(company_code)
    st = ''
    for b in bs:
        if re.match('-|[0-9a-zA-Z]', b):
            st +=b
    company_code = st

    if len(company_code) >31:
        company_code = company_code[0:30]

    if len(company_code) < 3:
        company_code = company_code+str(random.randint(1, 100))

    sql = 'select code from company where code = %s'
    result = conn.get(sql, company_code)
    if result != None:
        code = company_code + datestring[4:]
        result2 = conn.get(sql, code)
        if result2 != None:
            company_code = company_code + datestring
        else:
            company_code = code

    conn.close()
    return company_code


def find_company(source_company):
    if source_company["companyId"] is not None:
        return source_company["companyId"]

    full_name = source_company["fullName"]
    if full_name is not None and full_name != "":
        company_id = find_company_by_full_name(full_name)
        if company_id is not None:
            return company_id


    source_domains = conn.query("select * from source_domain where sourceCompanyId=%s", source_company["id"])
    for source_domain in source_domains:
        if source_domain["organizerType"] == "企业":
            company_id = find_company_by_full_name(source_domain["organizer"])
            if company_id is not None:
                return company_id
        company_id = find_company_by_domain(source_domain["domain"])
        if company_id is not None:
            return company_id

    source_artifacts = conn.query("select * from source_artifact where sourceCompanyId=%s", source_company["id"])
    for source_artifact in source_artifacts:
        if source_artifact["type"] == 4010:
            company_id = find_company_by_artifact(source_artifact)
            if company_id is not None:
                return company_id
    return None


def find_company_by_full_name(full_name):
    if full_name is None or full_name == "":
        return None

    full_name = util.norm_company_name(full_name)
    company = conn.get("select * from company where fullName=%s", full_name)
    if company is not None:
        return company["id"]

    company_alias = conn.get("select * from company_alias where type=12010 and name=%s", full_name)
    if company_alias is not None:
        return company_alias["companyId"]
    return None


def find_company_by_domain(domain):
    if domain is None or domain == "":
        return None

    domain = conn.get("select * from domain where domain=%s limit 1", domain)
    if domain is not None:
        return domain["companyId"]
    return None

def find_company_by_artifact(source_artifact):
    if source_artifact["type"] == 4010:
        artifact = conn.get("select * from artifact where type=4010 and link=%s limit 1", source_artifact["link"])
        if artifact is not None:
            return artifact["companyId"]

    return None


def add_company_alias(company_id, full_name):
    if full_name is None or full_name == "":
        return

    full_name = util.norm_company_name(full_name)
    alias = conn.get("select * from company_alias where companyId=%s and name=%s",
        company_id, full_name)

    if alias is None:
        sql = "insert company_alias(companyId,name,type,active,createTime) \
                values(%s,%s,%s,%s,now())"
        conn.insert(sql, company_id, full_name, 12010, 'Y')


def aggregate(source_company_id):
    logger.info("source_company_id: %s" % source_company_id)
    s = conn.get("select * from source_company where id=%s", source_company_id)
    if s is None:
        return

    company_id = find_company(s)

    #company
    if company_id is not None:
        logger.info("Update company: %s" % s["name"])
    else:
        logger.info("New company: %s" % s["name"])
        if s["companyStatus"] != 2020:
            code = get_company_code(s["name"])
            sql = "insert company(code,name,fullName,description,brief,\
                productDesc, modelDesc, operationDesc, teamDesc, marketDesc, compititorDesc, advantageDesc, planDesc, \
                round,roundDesc,companyStatus,fundingType,preMoney,currency,\
                locationId,address,phone,establishDate,logo,type,\
                headCountMin,headCountMax,\
                active,createTime,modifyTime) \
                values(%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,%s,%s,%s, \
                    %s,%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,%s,41020,\
                    %s,%s,\
                    %s,now(),now())"
            company_id = conn.insert(sql,
                    code,s["name"],s["fullName"],s["description"],s["brief"],
                    s.get("productDesc"), s.get("modelDesc"), s.get("operationDesc"), s.get("teamDesc"), s.get("marketDesc"), s.get("compititorDesc"), s.get("advantageDesc"), s.get("planDesc"),
                    s["round"],s["roundDesc"],s["companyStatus"],s["fundingType"],s["preMoney"],s["currency"],
                    s["locationId"],s["address"],s["phone"],s["establishDate"],s["logo"],
                    s["headCountMin"],s["headCountMax"],
                    'Y')
        else:
            return

    logger.info("companyId=%s", company_id)
    conn.update("update source_company set companyId=%s where id=%s", company_id, source_company_id)

    # company_alias
    add_company_alias(company_id, s["fullName"])

    # domain & company_alias
    source_domains = conn.query("select * from source_domain where sourceCompanyId=%s", source_company_id)
    for sd in source_domains:
        if sd["organizerType"] == "企业":
            add_company_alias(company_id, sd["organizer"])

        if sd["organizer"] is not None:
            domain = conn.get("select * from domain where companyId=%s and domain=%s and organizer=%s",
                    company_id,sd["domain"],sd["organizer"])
        else:
            domain = conn.get("select * from domain where companyId=%s and domain=%s limit 1",
                    company_id,sd["domain"])
        if domain is None:
            sql = "insert domain(companyId,domain,organizer,organizerType,beianhao,mainBeianhao,\
                    websiteName,homepage,beianDate,expire,\
                    active,createTime,modifyTime)\
                    values(%s,%s,%s,%s,%s,%s,\
                    %s,%s,%s,%s,\
                    'Y',now(),now())"
            conn.insert(sql,
                    company_id,
                    sd["domain"],sd["organizer"],sd["organizerType"],sd["beianhao"],sd["mainBeianhao"],\
                    sd["websiteName"],sd["homepage"],sd["beianDate"],sd["expire"]
                    )
        #TODO expire处理


    # artifact
    sas = conn.query("select * from source_artifact where sourceCompanyId=%s", source_company_id)
    for sa in sas:
        if sa["artifactId"] is not None:
            continue
        if sa["type"] == 4010: #website
            if sa["link"] is not None and sa["link"] != "":
                link = util.norm_url(sa["link"])
                try:
                    domain = util.get_domain(link)
                except:
                    continue
                a = conn.get("select * from artifact where companyId=%s and type=4010 and (name=%s or link=%s) limit 1", company_id, sa["name"], link)
                if a is None:
                    sql = "insert artifact(companyId,name,description,link,domain,type,active,createTime,modifyTime) \
                            values(%s,%s,%s,%s,%s,4010,'Y',now(),now())"
                    artifact_id = conn.insert(sql,
                            company_id, sa["name"], sa["description"], link, domain
                                )
                else:
                    artifact_id = a["id"]
                conn.update("update source_artifact set artifactId=%s where id=%s",
                            artifact_id, sa["id"])
        elif sa["type"] == 4040: #itunes
            result = util.re_get_result('id(\d*)', sa["link"])
            if result is None:
                continue
            app_id, = result

            a = conn.get("select * from artifact where type=4040 and domain=%s", app_id)
            if a is None:
                sql = "insert artifact(companyId,name,description,link,domain,type,active,createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s,4040,'Y',now(),now())"
                artifact_id = conn.insert(sql,
                        company_id,sa["name"],sa["description"],sa["link"],app_id
                            )
            else:
                artifact_id = a["id"]
            conn.update("update source_artifact set artifactId=%s where id=%s",
                        artifact_id, sa["id"])
        elif sa["type"] == 4050: #android
            package = None
            type,market = util.get_market(sa["link"])
            if market == 16030: #wandoujia
                result = util.re_get_result('wandoujia.com/apps/(.*)', sa["link"])
                if result is None:
                    continue
                package, = result
            elif market == 16040:
                result = util.re_get_result('apkName=(.*)', sa["link"])
                if result is None:
                    continue
                package, = result
            else:
                continue
            a = conn.get("select * from artifact where type=4050 and domain=%s",package)
            if a is None:
                sql = "insert artifact(companyId,name,description,link,domain,type,active,createTime,modifyTime) \
                        values(%s,%s,%s,%s,%s,4050,'Y',now(),now())"
                artifact_id = conn.insert(sql,
                        company_id,sa["name"],sa["description"],sa["link"],package
                            )
            else:
                artifact_id = a["id"]
            conn.update("update source_artifact set artifactId=%s where id=%s",
                        artifact_id, sa["id"])

    msg = {"type":"company", "id":company_id}
    flag = False
    while flag == False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


def setSourceCompanyAggregateStatus(source_company_id):
    conn = db.connect_torndb()
    s_status = conn.get("select * from source_company_aggregate_status where type=45000 and sourceCompanyId=%s", source_company_id)
    if s_status is not None:
        conn.update("update source_company_aggregate_status set status=46020, modifyTime=now() \
                    where sourceCompanyId=%s and type=45000",
                source_company_id)
    else:
        conn.insert("insert source_company_aggregate_status(sourceCompanyId, type ,status, createTime) \
                    values(%s,%s,%s,now())",
                    source_company_id, 45000, 46020)
    conn.close()


if __name__ == '__main__':
    initKafka()

    while True:
        logger.info("Company aggregator start...")
        conn = db.connect_torndb()
        #目前仅处理新产品!
        scs = conn.query("select sc.id as sourceCompanyId from source_company sc \
                        join source_company_aggregate_status status \
                            on \
                            sc.id=status.sourceCompanyId and \
                            status.status=46020 and \
                            status.type=45010 \
                        left join source_company_aggregate_status status_a \
                            on \
                            sc.id=status_a.sourceCompanyId and \
                            status_a.type=45000 \
                        where sc.type=41020 and \
                            (status_a.status is null or status_a.status!=46020)")
        conn.close()

        for sc in scs:
            aggregate(sc["sourceCompanyId"])
            setSourceCompanyAggregateStatus(sc["sourceCompanyId"])
            #break

        logger.info("Company aggregator end.")
        #break
        time.sleep(60)