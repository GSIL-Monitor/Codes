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
loghelper.init_logger("company_aggregator_baseinfo", stream=True)
logger = loghelper.get_logger("company_aggregator_baseinfo")

#
mongo = db.connect_mongo()
collection = mongo.trend.android
collection_alexa = mongo.trend.alexa
gongshang = mongo.info.gongshang

def get_company_code(name, test=False):
    table_names = helper.get_table_names(test)
    conn = db.connect_torndb()
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

    sql = "select code from " + table_names["company"] + " where code = %s"
    result = conn.get(sql, company_code)
    while result is not None:
        company_code += str(random.randint(1, 100))
        result = conn.get(sql, company_code)
        if result is None:
            break

    conn.close()
    return company_code


def create_company(source_company, test=False):
    s = source_company
    source_company_id = s["id"]
    logger.info("source_company_id: %s" % source_company_id)

    if s["companyStatus"] == 2020:  # close down
        return None

    # baseinfo
    code = get_company_code(s["name"], test)
    company_id = aggregator_db_util.insert_company(code,source_company, test)
    logger.info("companyId=%s", company_id)

    return company_id

def add_company_alias(company_id, source_company_id, test=False):
    table_names = helper.get_table_names(test)
    conn = db.connect_torndb()
    #source_company = conn.get("select * from source_company where id=%s", source_company_id)
    source_company_names = conn.query("select * from source_company_name where sourceCompanyId=%s", source_company_id)
    for s in source_company_names:
        if s["name"] is None or s["name"].strip() == "":
            continue
        name = s["name"].strip()
        alias = conn.get("select * from " + table_names["company_alias"] + " where companyId=%s and name=%s limit 1",
                    company_id, name)
        if alias is None:
            sql = "insert " + table_names["company_alias"] + "(companyId,name,type,active,createTime) \
                    values(%s,%s,%s,%s,now())"
            conn.insert(sql, company_id, name, s["type"], 'Y')
    conn.close()


def patch_company_establish_date(company_id):
    conn = db.connect_torndb()
    company1 = conn.get("select * from company where id=%s", company_id)
    if company1["establishDate"] is None:
        establish_date = None
        aliases = conn.query("select * from company_alias where companyId=%s", company_id)
        for alias in aliases:
            gongshang = aggregator_db_util.get_gongshang_by_name(alias["name"])
            if gongshang is not None:
                if establish_date is None or (gongshang["establishTime"] is not None and gongshang["establishTime"] < establish_date):
                    establish_date = gongshang["establishTime"]

        if establish_date is not None:
            try:
                conn.update("update company set establishDate=%s where id=%s", establish_date, company_id)
            except:
                pass
        else:
            fp = conn.get("select * from footprint where companyId=%s order by footDate limit 1", company_id)
            if fp is not None:
                conn.update("update company set establishDate=%s where id=%s", fp["footDate"],company_id)
    conn.close()

def patch_company_fullname(company_id):
    flag = False
    conn = db.connect_torndb()
    company1 = conn.get("select * from company where id=%s", company_id)
    patch = False
    if company1["fullName"] is None or company1["fullName"].strip() == "":
        patch = True
    else:
        chinese, iscompany = name_helper.name_check(company1["fullName"])
        if chinese is False:
            patch = True
        elif iscompany is False:
            patch = True

        if patch is False:
            gs = gongshang.find_one({"name":company1["fullName"]})
            if gs is None:
                patch = True

    if patch:
        logger.info("patch: %s, %s", company_id, company1["code"])
        aliases = conn.query("select * from company_alias where companyId=%s and type=12010", company_id)
        for alias in aliases:
            company_name = alias["name"]
            gs = gongshang.find_one({"name":company_name})
            if gs:
                logger.info("fullname: %s", company_name)
                conn.update("update company set fullName=%s where id=%s", company_name, company_id)
                flag = True
                break
        if flag is False:
            if company1["fullName"] is None or company1["fullName"].strip() == "":
                for alias in aliases:
                    company_name = alias["name"]
                    logger.info("fullname: %s", company_name)
                    conn.update("update company set fullName=%s where id=%s", company_name, company_id)
                    flag = True
                    break
    conn.close()
    return flag


def patch_company_location(company_id):
    conn = db.connect_torndb()
    company1 = conn.get("select * from company where id=%s", company_id)
    if company1["locationId"] is None or company1["locationId"] == 0:
        locationId = None
        scs = conn.query("select * from source_company where companyId=%s and (active is null or active='Y')", company_id)
        for sc in scs:
            if sc["locationId"] is not None and sc["locationId"] > 0:
                locationId = sc["locationId"]
                break

        if locationId is None:
            aliases = conn.query("select * from company_alias where companyId=%s and type=12010", company_id)
            for alias in aliases:
                loc1, loc2 = name_helper.get_location_from_company_name(alias["name"])
                if loc1 is not None:
                    l = conn.get("select *from location where locationName=%s", loc1)
                    if l:
                        locationId = l["locationId"]
                        break
        if locationId is not None:
            conn.update("update company set locationId=%s where id=%s", locationId, company1["id"])
    conn.close()


def patch_company_status(company_id):
    conn = db.connect_torndb()
    sc = conn.query("select id,companyStatus from source_company where source=13030 and companyId=%s and (active is null or active='Y')", company_id)
    if len(sc) > 0:
        company_status = 2020
        for s in sc:
            if s["companyStatus"] != 2020:
                company_status = s["companyStatus"]
                break
        logger.info("companyStatus: %s", company_status)
        conn.update("update company set companyStatus=%s where id=%s", company_status, company_id)
    conn.close()


def patch_should_index(company_id):
    #新产品(无其他源聚合)不建索引
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    if company["type"] == 41020:
        sc = conn.query("select id from source_company "
                        "where type=41010 and companyId=%s "
                        "and (verify is null or verify='Y') and (active is null or active='Y')",
                        company_id)
        if len(sc) == 0:
            conn.update("update company set shouldIndex=-1 where id=%s", company_id)
        else:
            conn.update("update company set shouldIndex=null,type=41010 where id=%s", company_id)
    else:
        if company["privatization"] == 'Y':
            conn.update("update company set shouldIndex=-1 where id=%s", company_id)
        else:
            conn.update("update company set shouldIndex=null where id=%s", company_id)
    conn.close()


def patch_logo(company_id):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    if company["logo"] is not None and company["logo"].strip() != "":
        conn.close()
        return
    logo = None
    scs = conn.query("select * from source_company where companyId=%s "
                     "and name=%s "
                     "and (active is null or active='Y') "
                     "order by source, id desc",
                     company_id, company["name"])
    for sc in scs:
        if sc["logo"] is not None and sc["logo"].strip() != "":
            logo = sc["logo"]
            break
    if logo is None:
        scs = conn.query("select * from source_company where companyId=%s "
                     "and (active is null or active='Y') "
                     "order by source, id desc",
                     company_id)
        for sc in scs:
            if sc["logo"] is not None and sc["logo"].strip() != "":
                logo = sc["logo"]
                break

    if logo:
        logger.info("code: %s, name: %s", company["code"],company["name"])
        conn.update("update company set logo=%s where id=%s", logo, company_id)
    conn.close()


def patch_website(company_id):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)
    logger.info("code: %s, name: %s", company["code"],company["name"])
    if company["website"] is not None and company["website"].strip() != "":
        conn.close()
        return

    website = None
    ats = conn.query("select * from artifact where (active is null or active='Y') "
                     "and type=4010 and companyId=%s", company_id)
    if len(ats) == 1:
        #如果只有一个website
        logger.info("select1")
        website = ats[0]["link"]


    if website is None:
        #从ITJuzi源寻找
        scs = conn.query("select id, name from source_company where (active is null or active='Y') "
                                 "and companyId=%s and source in (13030) order by source, id desc",
                                 company_id)
        for sc in scs:
            if sc["name"] != company["name"] and company["name"] not in sc["name"]:
                continue
            logger.info("sourceCompanyId: %s, name: %s", sc["id"], sc["name"])
            sas = conn.query("select id, link, domain from source_artifact where "
                             "sourceCompanyId=%s "
                             "and type=4010 and extended is null "
                             "and (active is null or active='Y')",
                             sc["id"])
            if len(sas) > 0:
                logger.info("select2")
                website = sas[0]["link"]
                break

    if website is None:
        #从36kr, lagou源寻找
        scs = conn.query("select id, name from source_company where (active is null or active='Y') "
                                 "and companyId=%s and source in (13020,13050) order by source, id desc",
                                 company_id)
        for sc in scs:
            if sc["name"] != company["name"] and company["name"] not in sc["name"]:
                continue
            logger.info("sourceCompanyId: %s, name: %s", sc["id"], sc["name"])
            sas = conn.query("select id, link, domain from source_artifact where "
                             "sourceCompanyId=%s "
                             "and type=4010 and extended is null "
                             "and (active is null or active='Y')",
                             sc["id"])
            if len(sas) > 0:
                logger.info("select2")
                website = sas[0]["link"]
                break

    if website is None:
        #所有源中排名最靠前的
        sas = conn.query("select id, link, domain from source_artifact where "
                        "type=4010 and extended is null "
                        "and sourceCompanyId in ("
                         "select id from source_company where (active is null or active='Y') and companyId=%s"
                        ") order by id desc",
                        company_id)
        for sa in sas:
            logger.info("candidate: %s", sa["link"])

        if len(sas) == 1:
            #只有一个website
            logger.info("select3")
            website = sas[0]["link"]
        elif len(sas) > 1:
            country_rank = 10000000
            selected = None
            #选排名最前的
            for sa in sas:
                if sa["domain"] is None or sa["domain"].strip() == "":
                    continue
                trend = collection_alexa.find_one({"domain":sa["domain"]}, sort=[("date", pymongo.DESCENDING)], limit=1)
                if trend and trend["country_rank"] is not None and trend["country_rank"] > 0:
                    if trend["country_rank"] < country_rank:
                        country_rank = trend["country_rank"]
                        selected = sa

            if selected is not None:
                logger.info("select4")
                website = selected["link"]

    if website is None:
        #找不到, 找active为N的 ITJUZI
        scs = conn.query("select id, name from source_company where (active is null or active='Y') "
                                 "and companyId=%s and source in (13030) order by source, id desc",
                                 company_id)
        for sc in scs:
            if sc["name"] != company["name"] and company["name"] not in sc["name"]:
                continue
            logger.info("sourceCompanyId: %s, name: %s", sc["id"], sc["name"])
            sas = conn.query("select id, link, domain from source_artifact where "
                             "sourceCompanyId=%s "
                             "and type=4010 and extended is null",
                             sc["id"])
            if len(sas) > 0:
                logger.info("select4.1")
                website = sas[0]["link"]
                break

    if website is None:
        #找不到, 找active为N的 36KR, Lagou
        scs = conn.query("select id, name from source_company where (active is null or active='Y') "
                                 "and companyId=%s and source in (13020,13050) order by source, id desc",
                                 company_id)
        for sc in scs:
            if sc["name"] != company["name"] and company["name"] not in sc["name"]:
                continue
            logger.info("sourceCompanyId: %s, name: %s", sc["id"], sc["name"])
            sas = conn.query("select id, link, domain from source_artifact where "
                             "sourceCompanyId=%s "
                             "and type=4010 and extended is null",
                             sc["id"])
            if len(sas) > 0:
                logger.info("select4.1")
                website = sas[0]["link"]
                break

    if website is None:
        #选最新出现的source_company的website
        scs = conn.query("select id from source_company where (active is null or active='Y') "
                         "and companyId=%s and source in (13020,13030,13050) order by id desc",
                         company_id)
        for sc in scs:
            sas = conn.query("select id, link, domain from source_artifact where "
                             "sourceCompanyId=%s "
                             "and type=4010 and extended is null",
                             sc["id"])
            if len(sas) > 0:
                logger.info("select5")
                website = sas[0]["link"]
                break

    if website is None:
        #选最新的source_company扩展出来的website
        for sc in scs:
            sas = conn.query("select id, link, domain from source_artifact where "
                             "sourceCompanyId=%s and type=4010",
                             sc["id"])
            if len(sas) > 0:
                logger.info("select6")
                website = sas[0]["link"]
                break

    if website is None:
        #选一个最新的website
        a = conn.get("select * from artifact where (active is null or active='Y') "
                     "and type=4010 and companyId=%s order by id desc limit 1", company_id)
        if a:
            logger.info("select7")
            website = a["link"]

    logger.info("selected website: %s", website)
    if website is not None:
        conn.update("update company set website=%s where id=%s", website, company_id)
    conn.close()


def get_best_artifact(company_id):
    return None
    # conn = db.connect_torndb()
    # selected = None
    # download = 0
    # android_artifacts = conn.query("select * from artifact where companyId=%s and type=4050 and (active is null or active='Y')",
    #                            company_id)
    # for a in android_artifacts:
    #     #选择流量最大的应用
    #     if a["name"] is None or a["name"].strip() == "":
    #             continue
    #     if a["domain"] is None or a["domain"].strip() == "":
    #         continue
    #     trend = collection.find_one({"appmarket":16010, "apkname":a["domain"]}, sort=[("date", pymongo.DESCENDING)], limit=1)
    #     if trend:
    #         if trend.has_key("download") and trend["download"] > download:
    #             download = trend["download"]
    #             selected = a
    #
    # if selected:
    #     logger.info("selected android: %s - %s", selected["id"], selected["name"])
    # else:
    #     country_rank = 10000000
    #     website_artifacts = conn.query("select * from artifact where companyId=%s and type=4010 and (active is null or active='Y')",
    #                            company_id)
    #     for a in website_artifacts:
    #         if a["name"] is None or a["name"].strip() == "":
    #             continue
    #         if a["domain"] is None or a["domain"].strip() == "":
    #             continue
    #         trend = collection_alexa.find_one({"domain":a["domain"]}, sort=[("date", pymongo.DESCENDING)], limit=1)
    #         if trend and trend["country_rank"] is not None and trend["country_rank"] > 0:
    #             if trend["country_rank"] < country_rank:
    #                 country_rank = trend["country_rank"]
    #                 selected = a
    #     if selected:
    #         logger.info("selected website: %s - %s", selected["id"], selected["name"])
    # conn.close()
    # return selected


def get_best_name(company_id):
    conn = db.connect_torndb()
    content = ""
    scs = conn.query("select * from source_company where companyId=%s and (active is null or active='Y') and (source<13050 or source>=13060)", company_id)
    if len(scs) == 0:
        scs = conn.query("select * from source_company where companyId=%s and (active is null or active='Y')", company_id)
    for sc in scs:
        if sc["brief"] is not None:
            content += sc["brief"]
        if sc["description"] is not None:
            content += sc["description"]
        if sc["productDesc"] is not None:
            content += sc["productDesc"]

        #sfs = conn.query("select * from source_footprint where sourceCompanyId=%s and footDate>date_sub(now(),interval 1 year)", sc["id"])
        sfs = conn.query("select * from source_footprint where sourceCompanyId=%s", sc["id"])
        for sf in sfs:
            if sf["description"] is not None:
                content += sf["description"]

    #names = conn.query("select distinct name from artifact where (active is null or active='Y') and companyId=%s", company_id)
    names = conn.query("select distinct name from source_company where companyId=%s and (active is null or active='Y') and (source<13050 or source>=13060)", company_id)
    if len(names) == 0:
        names = conn.query("select distinct name from source_company where companyId=%s and (active is null or active='Y')", company_id)
    # names = conn.query("select name,count(*) cnt from source_company where companyId=%s and (active is null or active='Y') having cnt>1", company_id)
    # if len(names) == 0:
    #     names = conn.query("select distinct name from source_company where companyId=%s and (active is null or active='Y')", company_id)

    selected_name = None
    cnt = 0
    for n in names:
        name = n["name"]
        if name is None or name.strip() == "":
            continue
        name = name.strip()
        _cnt = content.count(name)
        #logger.info("%s: %s", name, _cnt)
        if _cnt > cnt:
            cnt = _cnt
            selected_name = name
    conn.close()

    return selected_name


def aggregate(company_id, source_company_id):
    conn = db.connect_torndb()
    company = conn.get("select * from company where id=%s", company_id)

    if company["verify"] == "Y":
        conn.close()
        return

    # source_companies = conn.query("select * from source_company where companyId=%s and (active is null or active='Y') and source != 13002 and source is not null order by source", company_id)
    # if len(source_companies) > 0:
    #     selected = get_best_artifact(company_id)
    #
    #     if len(source_companies) == 1:
    #         aggregator_db_util.update_company(company_id, source_companies[0])
    #         sc = source_companies[0]
    #         if sc["source"] >= 13050 and sc["source"] < 13059:
    #             if selected and selected["type"] == 4050:
    #                 conn.update("update company set name=%s where id=%s", selected["name"], company_id)
    #                 if selected["description"] is not None and selected["description"].strip() != "":
    #                     conn.update("update company set description=%s where id=%s", selected["description"].strip(), company_id)
    #     else:
    #         from_job = True
    #         for sc in source_companies:
    #             if sc["source"] >= 13050 and sc["source"] < 13059:
    #                 continue
    #             from_job = False
    #             break
    #
    #         if from_job:
    #             #如果只有拉钩,用市场的产品描述
    #             if selected and selected["type"] == 4050:
    #                 conn.update("update company set name=%s where id=%s", selected["name"], company_id)
    #                 if selected["description"] is not None and selected["description"].strip() != "":
    #                     conn.update("update company set description=%s where id=%s", selected["description"].strip(), company_id)
    #         else:
    #             #从android或website选
    #             result = conn.get("select source, count(*) cnt from source_company where companyId=%s and (active is null or active='Y') group by source order by cnt desc limit 1", company_id)
    #             if result is not None and result['cnt'] > 1: # 一个源有多个产品
    #                 if selected is not None:
    #                     source_artifacts = conn.query("select c.id,extended,a.type,link,domain from source_artifact a join source_company c on a.sourceCompanyId=c.id \
    #                                 where c.companyId=%s order by extended", company_id)
    #                     selected_source_company_id = None
    #                     for sa in source_artifacts:
    #                         if sa["type"] == selected["type"] and sa["type"] == 4010 and sa["link"] == selected["link"]:
    #                             selected_source_company_id = sa["id"]
    #                             break
    #                         if sa["type"] == selected["type"] and sa["type"] == 4050 and sa["domain"] == selected["domain"]:
    #                             selected_source_company_id = sa["id"]
    #                             break
    #
    #                     logger.info("selected_source_company_id: %s", selected_source_company_id)
    #                     if selected_source_company_id:
    #                         source_company = conn.get("select * from source_company where id=%s", selected_source_company_id)
    #                         update_column(company, source_company)
    #
    #                     conn.update("update company set name=%s where id=%s",selected["name"], company_id)
    #
    #             else: # 一个源只有一个产品
    #                 #source_companyies按source排序,优先36kr
    #                 company = conn.get("select * from company where id=%s", company_id)
    #                 selected = source_companies[0]
    #                 update_column(company, selected)
    #
    # if company["description"] is None or company["description"]=="":
    #     source_company = conn.get("select * from source_company where id=%s", source_company_id)
    #     if source_company["description"] is not None:
    #         conn.update("update company set description=%s where id=%s", source_company["description"], company_id)

    source_companies = conn.query("select * from source_company where companyId=%s and (active is null or active='Y') and source != 13002 and source is not null order by source", company_id)
    if len(source_companies) > 1:
        selected_name = get_best_name(company_id)
        if selected_name is not None:
            logger.info("selected name: %s", selected_name)
            conn.update("update company set name=%s where id=%s", selected_name, company_id)
            scs = conn.query("select * from source_company where source=13030 and (active is null or active='Y') and companyId=%s and name=%s order by source", company_id, selected_name)
            if len(scs) == 0:
                scs = conn.query("select * from source_company where source>=13010 and (active is null or active='Y') and companyId=%s and name=%s order by source", company_id, selected_name)
            for sc in scs:
                if (sc["description"] is not None and sc["description"].strip() != "") or \
                        (sc["productDesc"] is not None and sc["productDesc"].strip() != ""):
                    logger.info("selected descrtion: %s, %s", sc["source"], sc["sourceId"])
                    logger.info(sc["description"].strip())
                    update_column(company_id, sc)
                    break

            for sc in scs:
                if sc["logo"] is not None and sc["logo"].strip() != "":
                    conn.update("update company set logo=%s where id=%s", sc["logo"],company_id)
                    break
    elif len(source_companies) == 1:
        sc = source_companies[0]
        update_column(company_id, sc)
        if sc["logo"] is not None and sc["logo"].strip() != "":
            conn.update("update company set logo=%s where id=%s", sc["logo"],company_id)
        if sc["name"] is not None and sc["name"].strip() != "":
            conn.update("update company set name=%s where id=%s", sc["name"], company_id)
    conn.close()


def update_column(company_id, source_company):
    columns = [
        "description",
        "productDesc",
        "modelDesc",
        "operationDesc",
        "teamDesc",
        "marketDesc",
        "compititorDesc",
        "advantageDesc",
        "planDesc",
        "brief"
    ]

    conn = db.connect_torndb()
    for column in columns:
        sql = "update company set " + column + "=%s where id=%s"
        if source_company[column] is not None and source_company[column].strip() != "":
            conn.update(sql, source_company[column].strip(), company_id)
    conn.close()


# kafka
kafkaProducer = None


def init_kafka():
    global kafkaProducer
    (url) = config.get_kafka_config()
    kafka = KafkaClient(url)
    # HashedPartitioner is default
    kafkaProducer = SimpleProducer(kafka)


def send_message(company_id):
    msg = {"type":"company", "id":company_id}
    flag = False
    while flag is False:
        try:
            kafkaProducer.send_messages("aggregator_v2", json.dumps(msg))
            flag = True
        except Exception,e :
            logger.exception(e)
            time.sleep(60)


if __name__ == "__main__":
    #init_kafka()
    # logger.info(get_best_name(881))
    # logger.info(get_best_name(284))
    # logger.info(get_best_name(3162))
    # logger.info(get_best_name(3291))
    # logger.info(get_best_name(48604))
    # logger.info(get_best_name(13842))
    # aggregate(3162,0)
    # aggregate(3291,0)
    # aggregate(48604,0)
    # aggregate(13842,0)
    #aggregate(14502,0)
    # conn = db.connect_torndb()
    # # cs = conn.query("select companyId from deal where organizationId=1")
    # cs = conn.query("select id as companyId from company where active is null or active='Y'")
    # for c in cs:
    #     company = conn.get("select * from company where id=%s", c["companyId"])
    #     logger.info(company["name"])
    #     # choosed_name = get_best_artifact(c["companyId"])
    #     # logger.info("%s: %s - %s", c["companyId"], company["name"], choosed_name)
    #     aggregate(c["companyId"], 0)
    #     send_message(c["companyId"])
    #     logger.info("\n\n\n\n\n")
    #
    # conn.close()

    '''
    conn = db.connect_torndb()
    cs = conn.query("select id, code, locationId from company where (active is null or active='Y') and (locationId is null or locationId=0)")
    for c in cs:
        logger.info("companyId: %s, code: %s,  locationId: %s", c["id"], c["code"], c["locationId"])
        patch_company_location(c["id"])
        #break
    conn.close()
    '''

    '''
    conn = db.connect_torndb()
    cs = conn.query("select id, name, code, logo from company where (active is null or active='Y')")
    for c in cs:
        logger.info("companyId: %s, code: %s,  logo: %s", c["id"], c["code"], c["logo"])

        scs = conn.query("select * from source_company where (active is null or active='Y') and companyId=%s and name=%s order by source", c["id"], c["name"])
        if len(scs) == 0 and (c["logo"] is None or c["logo"]==""):
            scs = conn.query("select * from source_company where (active is null or active='Y') and companyId=%s order by source", c["id"])

        for sc in scs:
            if sc["logo"] is not None and sc["logo"] != "" and sc["logo"] != c["logo"]:
                logger.info("c logo:%s, s logo: %s", c["logo"], sc["logo"])
                conn.update("update company set logo=%s where id=%s", sc["logo"],c["id"])
                break
        #break
    conn.close()
    '''

    '''
    num =0
    conn = db.connect_torndb()
    cs = conn.query("select id, name, code, verify,createUser, modifyUser from company where (active is null or active='Y')")
    for c in cs:
        if c["verify"] == 'Y' or c["createUser"] is not None or c["modifyUser"] is not None:
            continue
        new_name = get_best_name(c["id"])
        if new_name is not None and new_name != c["name"]:
            logger.info("companyId: %s, code: %s, name: %s, new name: %s", c["id"], c["code"], c["name"], new_name)
            #
            aggregate(c["id"],1)
            #break
            num+=1
    logger.info(num)
    '''

    '''
    conn = db.connect_torndb()
    cs = conn.query("select id from company where (active is null or active='Y') order by id")
    for c in cs:
        patch_website(c["id"])
        logger.info("")
    conn.close()
    '''

    conn = db.connect_torndb()
    cs = conn.query("select id from company where (active is null or active='Y') and type=41020 order by id")
    for c in cs:
        patch_should_index(c["id"])
        logger.info("")
    conn.close()


    # conn = db.connect_torndb()
    # cs = conn.query("select id from company where (active is null or active='Y') order by id")
    # conn.close()
    # for c in cs:
    #     #patch_company_fullname(c["id"])
    #     patch_logo(c["id"])
    #     #logger.info("")
    pass