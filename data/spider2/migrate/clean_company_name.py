# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
import loghelper, config
import db
import name_helper

#logger
loghelper.init_logger("clean_company_name", stream=True)
logger = loghelper.get_logger("clean_company_name")

def update_company_fullname(company_id, fullname):
    conn = db.connect_torndb()
    conn.update("update company set fullName=%s where id=%s", fullname, company_id)
    conn.close()

def save_company_alias(company_id, name):
    conn = db.connect_torndb()
    alias = conn.get("select * from company_alias where companyId=%s and name=%s limit 1", company_id, name)
    if alias is None:
        conn.insert("insert company_alias(companyId, name, type, active, createTime, modifyTime) \
        values(%s,%s,%s,'Y',now(),now())",
                    company_id, name, 12010)
    conn.close()

def update_company_alias(_id, name):
    conn = db.connect_torndb()
    conn.update("update company_alias set name=%s where id=%s", name , _id)
    conn.close()


if __name__ == '__main__':
    logger.info("Begin...")
    conn = db.connect_torndb()
    companies = conn.query("select id,fullname from company")
    for c in companies:
        aliases = conn.query("select * from company_alias where companyId=%s and type=12010", c["id"])
        for alias in aliases:
            name = alias["name"]
            new_name = name_helper.company_name_normalize(name)
            if name != new_name:
                logger.info("1. %s --- %s", name, new_name)
                update_company_alias(alias["id"], new_name)
            main_name = name_helper.get_main_company_name(new_name)
            if main_name != new_name:
                logger.info("2. %s --- %s", new_name, main_name)
                save_company_alias(c["id"],main_name)

        fullname = c["fullname"]
        if fullname is None or fullname.strip() == "":
            continue
        is_chinese, is_company = name_helper.name_check(fullname)
        if is_company:
            new_name = name_helper.company_name_normalize(fullname)
            if fullname != new_name:
                save_company_alias(c["id"],new_name)
                logger.info("3. %s --- %s", fullname, new_name)
            main_name = name_helper.get_main_company_name(new_name)
            if main_name != new_name:
                save_company_alias(c["id"],main_name)
                logger.info("4. %s --- %s", new_name, main_name)

            if main_name != fullname:
                update_company_fullname(c["id"], main_name)
    conn.close()

    logger.info("End.")