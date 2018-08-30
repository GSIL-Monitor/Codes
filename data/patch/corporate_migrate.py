# -*- coding: utf-8 -*-
import os, sys
import time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, util, db, config, name_helper

#logger
loghelper.init_logger("corporate_migrate", stream=True)
logger = loghelper.get_logger("corporate_migrate")

def process_corporate():
    id = -1
    conn = db.connect_torndb()
    while True:
        cs = conn.query("select * from company where id>%s order by id limit 1000", id)
        if len(cs) == 0:
            break
        for c in cs:
            company_id =c["id"]
            logger.info(c["name"])
            if company_id > id:
                id = company_id
            if c["corporateId"] is not None:
                continue
            corporate_id = conn.insert(
                "insert corporate(name,fullName,website,brief,description,"
                "round,roundDesc,corporateStatus,fundingType,currentRound,currentRoundDesc,preMoney,investment,postMoney,shareRatio,currency,"
                "headCountMin,headCountMax,locationId,address,phone,establishDate,logo,"
                "verify,active,createTime,modifyTime,createUser,modifyUser,confidence,statusDate) "
                "values(%s,%s,%s,%s,%s,"
                "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
                "%s,%s,%s,%s,%s,%s,%s,"
                "%s,%s,%s,%s,%s,%s,%s,%s)",
                c["name"], c["fullName"], c["website"], c["brief"], c["description"],
                c["round"], c["roundDesc"], c["companyStatus"], c["fundingType"], c["currentRound"], c["currentRoundDesc"], c["preMoney"], c["investment"], c["postMoney"], c["shareRatio"], c["currency"],
                c["headCountMin"], c["headCountMax"], c["locationId"], c["address"], c["phone"], c["establishDate"], c["logo"],
                c["verify"], c["active"], c["createTime"], c["modifyTime"], c["createUser"], c["modifyUser"], c["confidence"], c["statusDate"]
            )
            conn.update("update company set corporateId=%s where id=%s", corporate_id, company_id)
    conn.close()


def process_funding():
    id = -1
    conn = db.connect_torndb()
    while True:
        fs = conn.query("select * from funding where id>%s order by id limit 1000", id)
        if len(fs) == 0:
            break
        for f in fs:
            funding_id = f["id"]
            logger.info(funding_id)
            if funding_id > id:
                id = funding_id
            if f["corporateId"] is not None:
                continue
            c = conn.get("select * from company where id=%s", f["companyId"])
            corporate_id = c["corporateId"]
            if corporate_id is not None:
                conn.update("update funding set corporateId=%s where id=%s", corporate_id, funding_id)
    conn.close()


def process_alias():
    id = -1
    conn = db.connect_torndb()
    while True:
        cas = conn.query("select * from company_alias where id>%s order by id limit 1000", id)
        if len(cas) == 0:
            break
        for ca in cas:
            company_alias_id = ca["id"]
            logger.info(ca["name"])
            if company_alias_id > id:
                id = company_alias_id
            c = conn.get("select * from company where id=%s", ca["companyId"])
            corporate_id = c["corporateId"]
            if corporate_id is None:
                continue
            cpa = conn.get("select * from corporate_alias where corporateId=%s and name=%s limit 1", corporate_id, ca["name"])
            if cpa is not None:
                continue
            type = ca["type"]
            chinese, company = name_helper.name_check(ca["name"])
            if chinese and company:
                type = 12010
            conn.insert(
                "insert corporate_alias("
                "corporateId, name, type, verify, active, createTime, modifyTime,createUser,modifyUser,confidence)"
                "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                corporate_id,
                ca["name"], type, ca["verify"], ca["active"], ca["createTime"], ca["modifyTime"],
                ca["createUser"], ca["modifyUser"], ca["confidence"]
            )
    conn.update("update corporate_alias set type=12020 where type is null")
    conn.close()


def process_dup_alias():
    conn = db.connect_torndb()
    items = conn.query("select corporateId,name,count(*) from corporate_alias group by corporateId,name having count(*) > 1")
    for item in items:
        aliases = conn.query("select * from corporate_alias where corporateId=%s and name=%s", item["corporateId"], item["name"])
        logger.info("keep: %s", aliases[0]["id"])
        for alias in aliases[1:]:
            conn.execute("delete from corporate_alias where id=%s", alias["id"])
            logger.info("delete: %s", alias["id"])
    conn.close()


def patch_corporate_info():
    # 一个corporate只有一个company 同步company location, round 到corporate
    id = -1
    conn = db.connect_torndb()
    while True:
        cs = conn.query("select * from company where id>%s order by id limit 1000", id)
        if len(cs) == 0:
            break
        for c in cs:
            company_id = c["id"]
            corporate_id = c["corporateId"]
            logger.info(c["name"])
            if company_id > id:
                id = company_id
            if corporate_id is not None:
                continue
            result = conn.get("select count(*) cnt from company where corporateId=%s", corporate_id)
            if result["cnt"] > 1:
                continue
            conn.update("update corporate set locationId=%s, round=%s where id=%s", c["locationId"], c["round"], corporate_id)
    conn.close()

def patch_company_alias():
    # 删除 fullname 12010
    # type is null 处理
    id = -1
    conn = db.connect_torndb()
    while True:
        cas = conn.query("select * from company_alias where id>%s order by id limit 1000", id)
        if len(cas) == 0:
            break
        for ca in cas:
            company_alias_id = ca["id"]
            logger.info(ca["name"])
            if company_alias_id > id:
                id = company_alias_id

            type = ca["type"]
            chinese, company = name_helper.name_check(ca["name"])
            if chinese and company:
                type = 12010
            if type is None:
                type = 12020
            if type == 12010:
                conn.update("update company_alias set active='N', modifyUser=139 where id=%s", company_alias_id)
            else:
                conn.update("update company_alias set type=12020 where id=%s", company_alias_id)
    conn.close()


def migrate_corporate_alias_gongshangCheckTime():
    id = -1
    conn = db.connect_torndb()
    while True:
        cas = conn.query("select * from company_alias where id>%s order by id limit 1000", id)
        if len(cas) == 0:
            break
        for ca in cas:
            company_alias_id = ca["id"]
            logger.info(ca["name"])
            if company_alias_id > id:
                id = company_alias_id

            cpas = conn.query("select * from corporate_alias where name=%s", ca["name"])
            for cpa in cpas:
                if ca["gongshangCheckTime"] is not None:
                    conn.update("update corporate_alias set gongshangCheckTime=%s where id=%s", ca["gongshangCheckTime"], cpa["id"])
    conn.close()


if __name__ == "__main__":
    #process_corporate()
    #process_funding()
    #process_alias()

    #process_dup_alias()
    #patch_corporate_info()
    #patch_company_alias()
    migrate_corporate_alias_gongshangCheckTime()